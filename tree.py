# generate new IDs
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

  # construct tree of depth d
  # with all probabilities assigned to a
  def __init__(self, depth, loss_prob):
    assert(depth >= 1)

    # Construct leaf nodes (base case)
    if (depth == 1):
      self.left = None
      self.right = None
      self.id = new_id()
      self.incoming_loss_prob = loss_prob
      self.parent = None # This will be fixed once the parent is constructed
    else:
      # construct left and right trees
      left_tree  = Tree(depth - 1,loss_prob)
      right_tree = Tree(depth - 1, loss_prob)
      left_tree.parent = self
      right_tree.parent = self

      # Now construct self
      self.left  = left_tree
      self.right = right_tree
      self.id    = new_id()
      self.incoming_loss_prob = loss_prob
      self.parent = None

  def __str__(self):
    return "Root = (" + str(self.id) + "), left=(" + str(self.left) + "), right=(" + str(self.right) + "), loss = (" + str(self.incoming_loss_prob) + ")"

tree = Tree(3, 0.1);
print(tree)
