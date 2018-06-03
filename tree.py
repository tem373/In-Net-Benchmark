import numpy
LOW_ESCAPE_PROBABILITY = 0.001 # Low probability of escaping a state in the Gilbert-Elliot model

# generate new IDs for nodes
def new_id():
  if not hasattr(new_id, "counter"):
    new_id.counter = 0
  new_id.counter += 1
  return new_id.counter

# compute prob_escape_bad in the Gilbert-Elliot model, given prob_loss
def get_prob_escape_bad(prob_loss):
  prob_escape_good = LOW_ESCAPE_PROBABILITY
  ret = (prob_escape_good / prob_loss) - prob_escape_good
  assert((ret > 0) and (ret < 1))
  return ret

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
    self.loss_type = "bernoulli"
    self.prob_escape_good = self.LOW_ESCAPE_PROBABILITY
    self.prob_escape_bad = self.LOW_ESCAPE_PROBABILITY
    self.link_state = "undefined"

  # construct tree of depth depth
  # with all probabilities assigned to loss_prob
  def __init__(self, depth, loss_prob, loss_type):
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
      self.loss_type = loss_type
      self.prob_escape_good = LOW_ESCAPE_PROBABILITY
      self.prob_escape_bad = get_prob_escape_bad(self.incoming_loss_prob)

      # steady-state probability of being in "bad" is the same as self.incoming_loss_prob
      self.link_state = "bad" if (numpy.random.random() < self.incoming_loss_prob) else "good"

    else:
      # construct left and right trees
      left_tree  = Tree(depth - 1, loss_prob, loss_type)
      right_tree = Tree(depth - 1, loss_prob, loss_type)

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
      self.loss_type = loss_type
      self.prob_escape_good = LOW_ESCAPE_PROBABILITY
      self.prob_escape_bad = get_prob_escape_bad(self.incoming_loss_prob)

      # steady-state probability of being in "bad" is the same as self.incoming_loss_prob
      self.link_state = "bad" if (numpy.random.random() < self.incoming_loss_prob) else "good"

  # State transitions for Gilbert-Elliot loss model
  # Run this even if there aren't packets to maintain correctness of model.
  def state_transition(self):
    if (self.link_state == "good"):
      self.link_state = "bad" if (numpy.random.random() < self.prob_escape_good) else "good"
    else:
      assert(self.link_state == "bad")
      self.link_state = "good" if (numpy.random.random() < self.prob_escape_bad) else "bad"

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

  # deliver probe? Also use this to calculate true loss rate at incoming link to each node
  def deliver_probe(self, tick):
    self.num_packets_incoming += 1
    if (self.loss_type == "bernoulli"):
      delivered = not (numpy.random.random() < self.incoming_loss_prob)
    else:
      assert(self.loss_type == "gilbert_elliot")
      delivered = (self.link_state == "good")

    loss = 1 if (not delivered) else 0
    self.true_loss = self.true_loss + (loss - self.true_loss)/self.num_packets_incoming
    return delivered

  # send multicast probe down the tree and record outcome at all leaf nodes (receivers)
  def send_multicast_probe(self, tick):
    # For every node, look at whether packet is dropped on incoming link
    # And recursively on the trees rooted at that node

    # Base case: leaf node: look at whether packet is dropped on incoming link
    if (self.left == None and self.right == None):
      return [(self.id, self.deliver_probe(tick))]
    # Recursive case: intermediate nodes
    else:
      if (self.parent == None):
        # Always deliver packets that are incoming on the root node
        probe_delivered = True
      else:
        # Again, look at where packet is dropped on incoming link
        probe_delivered = self.deliver_probe(tick)

      # recurse left and right if probe was delivered 
      if (probe_delivered):
        return self.left.send_multicast_probe(tick) + self.right.send_multicast_probe(tick)
      # otherwise save some work and record an outcome of 0 at all receivers below self
      else:
        ret = []
        for receiver in self.receivers():
          ret += [(receiver.id, False)]
        return ret

  # send independent probes down every node
  # This is implemented recursively for convenience,
  # but is equivalent to running an independent random process at each node.
  def send_independent_probes(self, tick):
    # For the root node don't bother delivering, just recurse
    if (self.parent == None):
      probe_delivered = True
    else:
      probe_delivered = self.deliver_probe(tick)

    # Recursion logic: deliver left and right probes regardless of value of probe_delivered
    if (self.left != None and self.right != None):
      self.left.send_independent_probes(tick)
      self.right.send_independent_probes(tick)
