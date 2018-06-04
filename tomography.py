#! /usr/bin/python3

import numpy
import sys
from statistics import mean
from tree import Tree

# max likelihood estimator from https://ieeexplore.ieee.org/document/796384/
# "Multicast-based inference of network-internal loss characteristics"
class TomographyMle(object):
  @staticmethod
  def create_estimator(tree):
    # create the Y, gamma, and A for each node
    # we use capital Y and A for consistency with equation 24 of the paper
    all_nodes = tree.nodes()
    for node in all_nodes:
      node.Y = []
      node.gamma = 0.0
      node.A = 0.0

  @staticmethod
  def update_Y(tree, probe):
    # update the receiver Ys alone to probe
    for receiver in tree.receivers():
      receiver.Y += [probe[receiver.id]]

  @staticmethod
  def compute_gamma(tree):
    # Leaf node, update gamma incrementally using latest Y
    if (tree.left == None and tree.right == None):
      assert(len(tree.Y) > 0)
      tree.gamma = sum(tree.Y)/len(tree.Y)
      return tree.Y
    else: 
      # process left and right branches of tree
      Y_left  = TomographyMle.compute_gamma(tree.left)
      Y_right = TomographyMle.compute_gamma(tree.right)

      # logic or the left and right together
      assert(len(Y_left) == len(Y_right))
      for i in range(0, len(Y_left)):
        tree.Y += [Y_left[i] or Y_right[i]]

      # compute gamma for resulting tree
      tree.gamma = sum(tree.Y)/len(tree.Y)
      return tree.Y

  @staticmethod
  def compute_mle(tree, total_A):
    # For a binary tree, solvefor in Figure 7 has a closed form solution, which is plugged in below (ab/(a+b-c))
    # In general, we need to solve it numerically.
    if (tree.left == None and tree.right == None):
      tree.A = tree.gamma # Treat this as though the product is 0 per the paper
    else:
      assert (tree.left.gamma + tree.right.gamma - tree.gamma != 0)
      assert (abs(tree.left.gamma + tree.right.gamma - tree.gamma) >= 1e-10)
      # closed form solution for binary trees
      tree.A = (tree.left.gamma * tree.right.gamma * 1.0) / (tree.left.gamma + tree.right.gamma - tree.gamma)
    tree.alpha = tree.A * 1.0 / total_A
    if (tree.left != None and tree.right != None):
      TomographyMle.compute_mle(tree.left,  tree.A)
      TomographyMle.compute_mle(tree.right, tree.A)

  @staticmethod
  # Check conditions i and iv from 5.1 of http://nickduffield.net/download/papers/minctoit.pdf
  def pre_sanity_check(root):
    for node in root.nodes():
      if node.gamma == 0: # condition i
        print("Condition i: node.gamma is", node.gamma)
        return False
      elif ((node.left != None) and (node.right != None)): # condition iv
        if (node.left.gamma + node.right.gamma - node.gamma == 0):
          print("Condition iv: node.left.gamma, node.right.gamma, node.gamma", node.left.gamma, node.right.gamma, node.gamma)
          return False
        elif (abs(node.left.gamma + node.right.gamma - node.gamma) < 1e-10):
          print("Condition iv' (floating point error): node.left.gamma, node.right.gamma, node.gamma", node.left.gamma, node.right.gamma, node.gamma)
          return False
    return True

  @staticmethod
  # Check conditions ii and iii from 5.1 of http://nickduffield.net/download/papers/minctoit.pdf
  def post_sanity_check(root):
    for node in root.nodes():
      if node != root:
        if (node.alpha <= 0) or (node.alpha >= 1): # condition i
          print("Condition ii/iii: node.alpha is", node.alpha)
          return False
    return True


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
        node.state_transition()
    in_network_tree.send_independent_probes(i)

  # Compute max errors for in network approach
  node_true_errors = []
  for node in in_network_tree.nodes():
    if node != in_network_tree:
      node_true_errors += [round(100.0 * abs(node.true_loss - float(loss_probability)) / float(loss_probability), 5)]

  if (mean(node_true_errors) > 1e10):
    print("Abnormally high in-network error. Omitting this trial from error calculation.")
  else:
    mean_true_errors += [mean(node_true_errors)]

  # multicast tomography based approach
  mcast_tree = Tree(depth, loss_probability, loss_type)
  probe = dict() # To store results of probes keyed by receiver ID
  for receiver in mcast_tree.receivers():
    probe[receiver.id] = 0
  TomographyMle.create_estimator(mcast_tree)
  for i in range(0, num_probes):
    if loss_type == "gilbert_elliot":
      for node in mcast_tree.nodes():
        node.state_transition()
    outcome = mcast_tree.send_multicast_probe(i) # Pass in probe number i as tick to send_multicast_probe
    for rx_tuple in outcome:
      probe[rx_tuple[0]] = 1 if rx_tuple[1] else 0
    TomographyMle.update_Y(mcast_tree, probe)

  # Now compute MLE
  TomographyMle.compute_gamma(mcast_tree)
  if (TomographyMle.pre_sanity_check(mcast_tree) == False):
    print("Pre sanity check failed. Skipping this trial.\n")
    continue
  TomographyMle.compute_mle(mcast_tree, 1.0)
  if (TomographyMle.post_sanity_check(mcast_tree) == False):
    print("Post sanity check failed. Skipping this trial.\n")
    continue

  # Compute max errors for tomography
  node_tomography_errors = []
  for node in mcast_tree.nodes():
    if node != mcast_tree:
      node_tomography_errors += [round(100.0 * abs(1 - node.alpha - float(loss_probability)) / float(loss_probability), 5)]

  if (mean(node_tomography_errors) > 1e10):
    print("Abnormally high tomography error. Omitting this trial from error calculation.")
  else:
    mean_tomography_errors += [mean(node_tomography_errors)]

# print out average of max errors
print("Depth =", depth, "loss_probability =", loss_probability, "loss_type =", loss_type, \
      "num_probes =", num_probes, "num_trials =", num_trials,
      "\navg. tomography error = ", round(mean(mean_tomography_errors), 5), "%,", len(mean_tomography_errors), "trials",\
      "avg. in-network error = ", round(mean(mean_true_errors), 5), "%,", len(mean_true_errors), "trials")
