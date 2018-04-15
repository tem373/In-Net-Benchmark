import random

# generate new IDs for nodes
def new_id():
  if not hasattr(new_id, "counter"):
    new_id.counter = 0
  new_id.counter += 1
  return new_id.counter

class Tree:
  # default constructor
  def __init__(self):
    self.left = None
    self.right = None
    self.id = -1
    self.incoming_loss_prob = 0.0
    self.parent = None
    self.true_loss = 0.0
    self.num_packets_incoming = 0

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
      self.true_loss = 0.0
      self.num_packets_incoming = 0
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
      self.true_loss = 0.0
      self.num_packets_incoming = 0

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

  # deliver probe?
  def deliver_probe(self):
    self.num_packets_incoming += 1
    delivered = not (random.random() < self.incoming_loss_prob)
    loss = 1 if (not delivered) else 0
    self.true_loss = self.true_loss + (loss - self.true_loss)/self.num_packets_incoming
    return delivered

  # send probe down the tree and record outcome at all leaf nodes (receivers)
  def send_probe(self):
    # For every node, look at whether packet is dropped on incoming link
    # And recursively on the trees rooted at that node

    # Base case: leaf node: look at whether packet is dropped on incoming link
    if (self.left == None and self.right == None):
      return [(self.id, self.deliver_probe())]
    # Recursive case: intermediate nodes
    else:
      if (self.parent == None):
        # Always deliver packets that are incoming on the root node
        probe_delivered = True
      else:
        # Again, look at where packet is dropped on incoming link
        probe_delivered = self.deliver_probe()

      # recurse left and right if deliver_probe is true 
      if (probe_delivered):
        return self.left.send_probe() + self.right.send_probe()
      # otherwise save some work and record an outcome of 0 at all receivers below this node
      else:
        ret = []
        for receiver in self.receivers():
          ret += [(receiver.id, False)]
        return ret
