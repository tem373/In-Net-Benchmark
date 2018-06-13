#! /usr/bin/python3

import sys
import math
import numpy
from tree import Tree
from delay_mle import DelayTomographyMle

# seed random number generator
numpy.random.seed(1)

# Parameters
num_probes = 100000

# Create tree
mcast_tree = Tree(int(sys.argv[1]), "delay", int(sys.argv[2]), sys.argv[3])

# multicast estimator setup
max_y = -1
receivers = mcast_tree.receivers()
DelayTomographyMle.create_Y_and_root(mcast_tree, num_probes)
for i in range(0, num_probes):
  outcome = mcast_tree.send_multicast_probe_with_delay()
  assert(len(receivers) == len(outcome))
  for j in range(0, len(receivers)):
    receivers[j].Y[i] = outcome[j]
    if (outcome[j] > max_y):
      max_y = outcome[j]

# run multicast estimator
bin_width = 1
i_max = math.ceil((max_y * 1.0) / bin_width)
print("i_max is", i_max)
DelayTomographyMle.create_estimator(mcast_tree, i_max = i_max, n = num_probes)
DelayTomographyMle.main(mcast_tree, q = bin_width, i_max = i_max, n = num_probes, epsilon = float(sys.argv[4]))
print("inferred probabilities for tree", mcast_tree)
for node in mcast_tree.nodes():
  print(node.id, node.alpha)
