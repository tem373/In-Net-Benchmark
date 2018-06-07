#! /usr/bin/python3

import numpy
import sys
from statistics import mean
from tree import Tree
from loss_mle import LossTomographyMle

if len(sys.argv) != 6:
  print("Usage: ", sys.argv[0], " depth loss_probability loss_type num_probes num_trials ")
  exit(1)
else:
  depth = int(sys.argv[1])
  loss_probability = float(sys.argv[2])
  loss_type =  sys.argv[3]
  assert(loss_type in ["bernoulli", "gilbert_elliot"])
  num_probes = int(sys.argv[4])
  num_trials = int(sys.argv[5])

# Error at each run from tomography and true error
mean_tomography_errors = []
mean_true_errors = []

for i in range(1, num_trials + 1):
  # seed random number generator
  numpy.random.seed(i)

  # in network approach
  in_network_tree = Tree(depth, loss_probability, loss_type)
  for i in range(0, num_probes):
    if loss_type == "gilbert_elliot":
      for node in in_network_tree.nodes():
        node.tick()
    in_network_tree.send_independent_probes()

  # Compute max errors for in network approach
  node_true_errors = []
  for node in in_network_tree.nodes():
    if node != in_network_tree:
      node_true_errors += [round(100.0 * abs(node.true_loss - float(loss_probability)) / float(loss_probability), 5)]

  mean_true_errors += [mean(node_true_errors)]

  # multicast tomography based approach
  mcast_tree = Tree(depth, loss_probability, loss_type)
  probe = dict() # To store results of probes keyed by receiver ID
  for receiver in mcast_tree.receivers():
    probe[receiver.id] = 0
  LossTomographyMle.create_estimator(mcast_tree)
  for i in range(0, num_probes):
    if loss_type == "gilbert_elliot":
      for node in mcast_tree.nodes():
        node.state_transition()
    outcome = mcast_tree.send_multicast_probe()
    for rx_tuple in outcome:
      probe[rx_tuple[0]] = 1 if rx_tuple[1] else 0
    LossTomographyMle.update_Y(mcast_tree, probe)

  # Now compute MLE
  LossTomographyMle.compute_gamma(mcast_tree)
  if (LossTomographyMle.pre_sanity_check(mcast_tree) == False):
    print("Pre sanity check failed. Skipping this trial.\n")
    continue
  LossTomographyMle.compute_mle(mcast_tree, 1.0)
  if (LossTomographyMle.post_sanity_check(mcast_tree) == False):
    print("Post sanity check failed. Skipping this trial.\n")
    continue

  # Compute max errors for tomography
  node_tomography_errors = []
  for node in mcast_tree.nodes():
    if node != mcast_tree:
      node_tomography_errors += [round(100.0 * abs(1 - node.alpha - float(loss_probability)) / float(loss_probability), 5)]

  mean_tomography_errors += [mean(node_tomography_errors)]

# print out average of max errors
print("Depth =", depth, "loss_probability =", loss_probability, "loss_type =", loss_type, \
      "num_probes =", num_probes, "num_trials =", num_trials,
      "\navg. tomography error = ", round(mean(mean_tomography_errors), 5) if len(mean_tomography_errors) > 0 else "undef",\
      "%,", len(mean_tomography_errors), "trials",\
      "\navg. in-network error = ", round(mean(mean_true_errors), 5),\
      "%,", len(mean_true_errors), "trials")
