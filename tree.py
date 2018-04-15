import random
import numpy

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
  def run_estimator(tree, probe_data, num_probes):
    # create the Y, gamma, and A for each node
    # we use capital Y and A for consistency with equation 24 of the paper
    all_nodes = tree.nodes()
    for node in all_nodes:
      node.Y = numpy.array([0] * num_probes)
      node.gamma = 0.0
      node.A = 0.0

    # initialize the receiver Ys alone to probe_data
    for receiver in tree.receivers():
      receiver.Y = probe_data[receiver.id]

    TomographyMle.find_gamma(tree, num_probes)
    TomographyMle.infer(tree, 1)

  @staticmethod
  def find_gamma(tree, num_probes):
    if (tree.left == None and tree.right == None):
      tree.gamma = (numpy.sum(tree.Y) * 1.0)/num_probes
      return tree.Y
    else: 
      # process left and right branches of tree
      Y_left  = TomographyMle.find_gamma(tree.left, num_probes)
      Y_right = TomographyMle.find_gamma(tree.right, num_probes)

      # Or them together
      tree.Y = numpy.logical_or(Y_left, Y_right)

      # Divide by num_probes to get gamma
      tree.gamma = (numpy.sum(tree.Y) * 1.0)/num_probes
      return tree.Y

  @staticmethod
  def infer(tree, total_A):
    # For a binary tree, solvefor in Figure 7 has a closed form solution, which we have plugged in below
    # In general, we need to solve it numerically.
    if (tree.left == None and tree.right == None):
      tree.A = tree.gamma # Treat this as though the product is 0
    else:
      tree.A = (tree.left.gamma * tree.right.gamma * 1.0) / (tree.left.gamma + tree.right.gamma - tree.gamma)
    assert(tree.A > 0)
    assert(tree.A < 1)
    tree.alpha = tree.A * 1.0 / total_A
    if (tree.left != None and tree.right != None):
      TomographyMle.infer(tree.left, tree.A)
      TomographyMle.infer(tree.right, tree.A)
 
random.seed(1)
tree = Tree(3, 0.1);
print(tree)
probe_data = dict() # To store results of probes
for receiver in tree.receivers():
  probe_data[receiver.id] = []
for i in range(0, 100000):
  outcome = tree.send_probe()
  for rx_tuple in outcome:
    probe_data[rx_tuple[0]] += [1 if rx_tuple[1] else 0]

mle_est = TomographyMle()
TomographyMle.run_estimator(tree, probe_data, 100000)
for node in tree.nodes():
  print(node.alpha)
