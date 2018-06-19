#! /usr/bin/python3

import sys
import math
import numpy
from tree import Tree
from delay_mle import DelayTomographyMle

# seed random number generator
numpy.random.seed(1)

# Cmdline args
if (len(sys.argv) < 6):
  print("Usage: " , sys.argv[0], " depth mean_delay delay_type error_tolerance num_probes")
  sys.exit(1)
else:
  depth = int(sys.argv[1])
  assert(depth > 1)
  mean_delay = float(sys.argv[2])
  assert(mean_delay > 0)
  delay_type = sys.argv[3]
  assert(delay_type in ["geometric", "pareto", "uniform"])
  epsilon = float(sys.argv[4])
  assert(epsilon > 0)
  num_probes = int(sys.argv[5])
  assert(num_probes > 100)

# Create tree
mcast_tree = Tree(depth, "delay", mean_delay, delay_type)

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
DelayTomographyMle.main(mcast_tree, q = bin_width, i_max = i_max, n = num_probes, epsilon = epsilon)
print("inferred probabilities for tree", mcast_tree)
for node in mcast_tree.nodes():
  print(node.id, node.alpha)
