import random
import numpy
import sys

# generate new IDs for nodes
def new_id():
  if not hasattr(new_id, "counter"):
    new_id.counter = 0
  new_id.counter += 1
  return new_id.counter

# deliver probe?
def deliver_probe(loss_prob):
  return not (random.random() < loss_prob)

class Tree:
  # default constructor
  def __init__(self):
    self.left = None
    self.right = None
    self.id = -1
    self.incoming_loss_prob = 0.0
    self.parent = None

  # construct tree of depth depth
  # with all probabilities assigned to loss_prob
  def __init__(self, depth, loss_prob):
    assert(depth >= 1)
    assert(loss_prob > 0)
    assert(loss_prob < 1)

    # Construct leaf nodes (base case)
    if (depth == 1):
      self.left = None
      self.right = None
      self.id = new_id()
      self.incoming_loss_prob = loss_prob
      self.parent = None # This will be fixed once the parent is constructed (see below)
    else:
      # construct left and right trees
      left_tree  = Tree(depth - 1, loss_prob)
      right_tree = Tree(depth - 1, loss_prob)

      # set their parents (which are currently None) to self
      left_tree.parent = self
      right_tree.parent = self

      # Now construct self itself
      self.left  = left_tree
      self.right = right_tree
      self.id    = new_id()
      self.incoming_loss_prob = loss_prob
      self.parent = None

  # get a list of receivers under this tree
  def receivers(self):
    if (self.left == None and self.right == None):
      return [self]
    else:
      return self.left.receivers() + self.right.receivers()

  # get a list of all nodes under this tree
  def nodes(self):
    if (self.left == None and self.right == None):
      return [self]
    else:
      return [self] + self.left.nodes() + self.right.nodes()

  def __str__(self):
    assert(self.id != -1)
    assert(self.incoming_loss_prob != 0)
    assert(self.incoming_loss_prob != 1)
    assert((self.left == None and self.right == None) or (self.left != None and self.right != None))
    return "Root = (" + str(self.id) + \
           "), left=(" + str(self.left) + \
           "), right=(" + str(self.right) + \
           "), loss = (" + str(self.incoming_loss_prob) + ")"

  # send probe down the tree and record outcome at all leaf nodes (receivers)
  def send_probe(self):
    # For every node, look at whether packet is dropped on incoming link
    # And recursively on the trees rooted at that node

    # Base case: leaf node: look at whether packet is dropped on incoming link
    if (self.left == None and self.right == None):
      return [(self.id, deliver_probe(self.incoming_loss_prob))]
    # Recursive case: intermediate nodes
    else:
      if (self.parent == None):
        # Always deliver packets that are incoming on the root node
        probe_delivered = True
      else:
        # Again, look at where packet is dropped on incoming link
        probe_delivered = deliver_probe(self.incoming_loss_prob)

      # recurse left and right if deliver_probe is true 
      if (probe_delivered):
        return self.left.send_probe() + self.right.send_probe()
      # otherwise save some work and record an outcome of 0 at all receivers below this node
      else:
        ret = []
        for receiver in self.receivers():
          ret += [(receiver.id, False)]
        return ret

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
    if (tree.left == None and tree.right == None):
      assert(len(tree.Y) > 0)
      tree.gamma = tree.gamma + (tree.Y[-1] - tree.gamma)/len(tree.Y)
      return tree.Y
    else: 
      # process left and right branches of tree
      Y_left  = TomographyMle.update_gamma(tree.left)
      Y_right = TomographyMle.update_gamma(tree.right)

      # Or the last entry together
      tree.Y += [Y_left[-1] or Y_right[-1]]

      # Divide by num_probes to get gamma
      tree.gamma = tree.gamma + (tree.Y[-1] - tree.gamma)/len(tree.Y)
      return tree.Y

  @staticmethod
  def update_mle(tree, total_A):
    # For a binary tree, solvefor in Figure 7 has a closed form solution, which we have plugged in below
    # In general, we need to solve it numerically.
    if (tree.left == None and tree.right == None):
      tree.A = tree.gamma # Treat this as though the product is 0
    else:
      if (tree.left.gamma + tree.right.gamma - tree.gamma == 0):
        tree.A = -1
      else:
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

# Max error at each run 
max_errors = []

for i in range(1, num_trials):
  random.seed(i)
  tree = Tree(depth, loss_probability)
  probe = dict() # To store results of probes
  for receiver in tree.receivers():
    probe[receiver.id] = 0
  TomographyMle.create_estimator(tree)
  for i in range(0, num_probes):
    outcome = tree.send_probe()
    for rx_tuple in outcome:
      probe[rx_tuple[0]] = 1 if rx_tuple[1] else 0
    TomographyMle.update_estimator(tree, probe)

  # print out average max error at the end
  node_errors = []
  for node in tree.nodes():
    if node != tree:
      node_errors += [round(100.0 * abs(1 - node.alpha - float(loss_probability)) / float(loss_probability), 5)]

  max_errors += [max(node_errors)]

print("Depth = ", depth, " loss_probability = ", loss_probability, \
      " avg. max error = ", sum(max_errors)/num_trials, "%")
