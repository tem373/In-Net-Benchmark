import random
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
  def update_estimator(tree, probe):
    # update the receiver Ys alone to probe
    for receiver in tree.receivers():
      receiver.Y += [probe[receiver.id]]

    TomographyMle.update_gamma(tree)
    TomographyMle.update_mle(tree, 1)

  @staticmethod
  def update_gamma(tree):
    # Leaf node, update gamma incrementally using latest Y
    if (tree.left == None and tree.right == None):
      assert(len(tree.Y) > 0)
      tree.gamma = tree.gamma + (tree.Y[-1] - tree.gamma)/len(tree.Y)
      return tree.Y
    else: 
      # process left and right branches of tree
      Y_left  = TomographyMle.update_gamma(tree.left)
      Y_right = TomographyMle.update_gamma(tree.right)

      # logic or the last entry of left and right together
      tree.Y += [Y_left[-1] or Y_right[-1]]

      # Incrementally update gamma again using the latest Y
      tree.gamma = tree.gamma + (tree.Y[-1] - tree.gamma)/len(tree.Y)
      return tree.Y

  @staticmethod
  def update_mle(tree, total_A):
    # For a binary tree, solvefor in Figure 7 has a closed form solution, which is plugged in below (ab/(a+b-c))
    # In general, we need to solve it numerically.
    if (tree.left == None and tree.right == None):
      tree.A = tree.gamma # Treat this as though the product is 0 per the paper
    else:
      if (tree.left.gamma + tree.right.gamma - tree.gamma == 0):
        tree.A = -1       # Need to handle divide by zero. Occurs in the beginning when there isn't enough data
      else:               # closed form solution for binary trees
        tree.A = (tree.left.gamma * tree.right.gamma * 1.0) / (tree.left.gamma + tree.right.gamma - tree.gamma)
    # assert(tree.A > 0) # This may fail for the first several probes
    # assert(tree.A < 1) # This may fail for the first several probes
    tree.alpha = tree.A * 1.0 / total_A
    if (tree.left != None and tree.right != None):
      TomographyMle.update_mle(tree.left,  tree.A)
      TomographyMle.update_mle(tree.right, tree.A)

if len(sys.argv) != 5:
  print("Usage: ", sys.argv[0], " depth loss_probability num_probes num_trials ")
  exit(1)
else:
  depth = int(sys.argv[1])
  loss_probability = float(sys.argv[2])
  num_probes = int(sys.argv[3])
  num_trials = int(sys.argv[4])

# Error at each run from tomography and true error
max_tomography_errors = []
max_true_errors = []

for i in range(1, num_trials + 1):
  random.seed(i)
  tree = Tree(depth, loss_probability)
  probe = dict() # To store results of probes keyed by receiver ID
  for receiver in tree.receivers():
    probe[receiver.id] = 0
  TomographyMle.create_estimator(tree)
  for i in range(0, num_probes):
    outcome = tree.send_probe()
    for rx_tuple in outcome:
      probe[rx_tuple[0]] = 1 if rx_tuple[1] else 0
    TomographyMle.update_estimator(tree, probe)

  # Compute max errors for both tomography and true error
  node_tomography_errors = []
  for node in tree.nodes():
    if node != tree:
      node_tomography_errors += [round(100.0 * abs(1 - node.alpha - float(loss_probability)) / float(loss_probability), 5)]
  max_tomography_errors += [max(node_tomography_errors)]

  node_true_errors = []
  for node in tree.nodes():
    if node != tree:
      node_true_errors += [round(100.0 * abs(node.true_loss - float(loss_probability)) / float(loss_probability), 5)]
  max_true_errors += [max(node_true_errors)]

# print out average of max errors
print("Depth = ", depth, " loss_probability = ", loss_probability, \
      " avg. max tomography error = ", round(mean(max_tomography_errors), 5), "%", \
      " avg. max true error = ", round(mean(max_true_errors), 5), "%")
