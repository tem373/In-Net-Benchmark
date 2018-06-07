# max likelihood estimator from https://ieeexplore.ieee.org/document/796384/
# "Multicast-based inference of network-internal loss characteristics"
class LossTomographyMle(object):
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
  def update_Y(tree, probe):
    # update the receiver Ys alone to probe
    for receiver in tree.receivers():
      receiver.Y += [probe[receiver.id]]

  @staticmethod
  def compute_gamma(tree):
    # Leaf node, update gamma incrementally using latest Y
    if (tree.left == None and tree.right == None):
      assert(len(tree.Y) > 0)
      tree.gamma = sum(tree.Y)/len(tree.Y)
      return tree.Y
    else: 
      # process left and right branches of tree
      Y_left  = LossTomographyMle.compute_gamma(tree.left)
      Y_right = LossTomographyMle.compute_gamma(tree.right)

      # logic or the left and right together
      assert(len(Y_left) == len(Y_right))
      for i in range(0, len(Y_left)):
        tree.Y += [Y_left[i] or Y_right[i]]

      # compute gamma for resulting tree
      tree.gamma = sum(tree.Y)/len(tree.Y)
      return tree.Y

  @staticmethod
  def compute_mle(tree, total_A):
    # For a binary tree, solvefor in Figure 7 has a closed form solution, which is plugged in below (ab/(a+b-c))
    # In general, we need to solve it numerically.
    if (tree.left == None and tree.right == None):
      tree.A = tree.gamma # Treat this as though the product is 0 per the paper
    else:
      assert (tree.left.gamma + tree.right.gamma - tree.gamma != 0)
      assert (abs(tree.left.gamma + tree.right.gamma - tree.gamma) >= 1e-10)
      # closed form solution for binary trees
      tree.A = (tree.left.gamma * tree.right.gamma * 1.0) / (tree.left.gamma + tree.right.gamma - tree.gamma)
    tree.alpha = tree.A * 1.0 / total_A
    if (tree.left != None and tree.right != None):
      LossTomographyMle.compute_mle(tree.left,  tree.A)
      LossTomographyMle.compute_mle(tree.right, tree.A)

  @staticmethod
  # Check conditions i and iv from 5.1 of http://nickduffield.net/download/papers/minctoit.pdf
  def pre_sanity_check(root):
    for node in root.nodes():
      if node.gamma == 0: # condition i
        print("Condition i: node.gamma is", node.gamma)
        return False
      elif ((node.left != None) and (node.right != None)): # condition iv
        if (node.left.gamma + node.right.gamma - node.gamma == 0):
          print("Condition iv: node.left.gamma, node.right.gamma, node.gamma", node.left.gamma, node.right.gamma, node.gamma)
          return False
        elif (abs(node.left.gamma + node.right.gamma - node.gamma) < 1e-10):
          print("Condition iv' (floating point error): node.left.gamma, node.right.gamma, node.gamma", node.left.gamma, node.right.gamma, node.gamma)
          return False
    return True

  @staticmethod
  # Check conditions ii and iii from 5.1 of http://nickduffield.net/download/papers/minctoit.pdf
  def post_sanity_check(root):
    for node in root.nodes():
      if node != root:
        if (node.alpha <= 0) or (node.alpha >= 1): # condition ii/iii
          print("Condition ii/iii: node.alpha is", node.alpha)
          return False
    return True


