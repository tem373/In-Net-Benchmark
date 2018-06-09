from loss_distribution  import LossDistribution
from delay_distribution import DelayDistribution
import numpy

# generate new IDs for nodes
def new_id():
  if not hasattr(new_id, "counter"):
    new_id.counter = 0
  new_id.counter += 1
  return new_id.counter

class Tree:
  def initialize_tree(self, expt_type, mean_delay_or_loss, dist_type):
    self.id = new_id()
    self.parent = None # This will be fixed once the parent is constructed (see below)
    self.true_loss = 0.0
    self.num_packets_incoming = 0
    assert(expt_type in ["delay", "loss"])
    if (expt_type == "loss"): 
      self.loss_dist  = LossDistribution(mean_delay_or_loss, dist_type) 
    else:
      self.delay_dist = DelayDistribution(mean_delay_or_loss, dist_type)

  def children(self):
    if (self.left == None and self.right == None):
      return []
    else:
      assert(self.left != None and self.right != None)
      return [self.left, self.right]

  def tick(self):
    # Anything that needs to run periodically on every probe/tick
    self.loss_dist.state_transition()
 
  # construct tree of depth depth
  def __init__(self, depth, expt_type, mean_delay_or_loss, dist_type):
    assert(depth >= 1)
    assert(expt_type in ["delay", "loss"])

    # Construct leaf nodes (base case)
    if (depth == 1):
      self.left = None
      self.right = None
      self.initialize_tree(expt_type, mean_delay_or_loss, dist_type)

    else:
      # construct left and right trees
      left_tree  = Tree(depth - 1, expt_type, mean_delay_or_loss, dist_type)
      right_tree = Tree(depth - 1, expt_type, mean_delay_or_loss, dist_type)

      # set their parents (which are currently None) to self
      left_tree.parent = self
      right_tree.parent = self

      # Now construct self itself
      self.left  = left_tree
      self.right = right_tree
      self.initialize_tree(expt_type, mean_delay_or_loss, dist_type)

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

  # send multicast probe down the tree and record outcome at all leaf nodes (receivers)
  def send_multicast_probe(self):
    # For every node, look at whether packet is dropped on incoming link
    # And recursively on the trees rooted at that node

    # Base case: leaf node: look at whether packet is dropped on incoming link
    if (self.left == None and self.right == None):
      return [(self.id, self.loss_dist.deliver_probe())]
    # Recursive case: intermediate nodes
    else:
      if (self.parent == None):
        # Always deliver packets that are incoming on the root node
        probe_delivered = True
      else:
        # Again, look at where packet is dropped on incoming link
        probe_delivered = self.loss_dist.deliver_probe()

      # recurse left and right if probe was delivered 
      if (probe_delivered):
        return self.left.send_multicast_probe() + self.right.send_multicast_probe()
      # otherwise save some work and record an outcome of 0 at all receivers below self
      else:
        ret = []
        for receiver in self.receivers():
          ret += [(receiver.id, False)]
        return ret

  # send independent probes down every node
  # This is implemented recursively for convenience,
  # but is equivalent to running an independent random process at each node.
  def send_independent_probes(self):
    # For the root node don't bother delivering, just recurse
    if (self.parent == None):
      probe_delivered = True
    else:
      probe_delivered = self.loss_dist.deliver_probe()
      self.num_packets_incoming += 1
      loss = 1 if (not probe_delivered) else 0
      self.true_loss = self.true_loss + (loss - self.true_loss)/self.num_packets_incoming

    # Recursion logic: deliver left and right probes regardless of value of probe_delivered
    if (self.left != None and self.right != None):
      self.left.send_independent_probes()
      self.right.send_independent_probes()

  # Send a multicast probe that is delayed by an independent amount
  # at each link. This amount is sampled from a delay distribution.
  # There are no losses in this function.
  # Returns a vector of end-to-end one-way delays from source to each of the receivers under the tree.
  def send_multicast_probe_with_delay(self):
    mean_delay = 5
    incoming_link_delay = 0
    if (self.parent == None):
      incoming_link_delay = 0
    else:
      incoming_link_delay = self.delay_dist.sample()

    if (self.left != None and self.right != None):
      return [x + incoming_link_delay for x in self.left.send_multicast_probe_with_delay()] + \
             [x + incoming_link_delay for x in self.right.send_multicast_probe_with_delay()]
    else:
      assert(self.left == None and self.right == None)
      return [incoming_link_delay]
