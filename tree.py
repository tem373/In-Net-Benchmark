import random

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

  # count number of receivers in the tree rooted at self
  def num_receivers(self):
    if (self.left == None and self.right == None):
      return 1
    else:
      return self.left.num_receivers() + self.right.num_receivers()

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
      return [deliver_probe(self.incoming_loss_prob)]
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
        return [0] * self.num_receivers()

random.seed(1)
tree = Tree(3, 0.1);
print(tree)
for i in range(0, 100000):
  outcome = tree.send_probe()
  for delivery in outcome:
    print(delivery, end=" ")
  print()
