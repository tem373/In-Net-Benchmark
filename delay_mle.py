import math
from tree import Tree
import cvxpy
import numpy
import numpy.matlib

# max likelihood delay distribution estimator from http://nickduffield.net/download/papers/delaylast.pdf
# "Multicast-based inference of network-internal delay distributions"
# The equations are 8/16 in the delaylast.pdf paper, but they are 8/18 in the IEEE ToN paper.
# The IEEE ToN paper equations correspond more closely to the p + qx + (c1 + c2x)(c3+ c4x) that we convert into.
class DelayTomographyMle(object):
  @staticmethod
  def create_Y_and_root(tree, n):
    all_nodes = tree.nodes()
    for node in all_nodes:
      node.Y = [math.inf] * n
    # create a fake root node so that k.parent doesn't throw an error
    root = Tree(1, "delay", 0.5, "geometric") # The exact values here are irrelevant because root is a fake node
    root.id = -1
    root.left = tree
    root.right = tree
    root.parent = None
    tree.parent = root

  @staticmethod
  def create_estimator(tree, i_max, n):
    # Create the alpha, A, Y, gamma, beta data structures for each node 
    all_nodes = tree.nodes()
    for node in all_nodes:
      node.alpha = [0.0] * (i_max + 1)
      node.A = [0.0] * (i_max + 1)
      node.gamma = [0.0] * (i_max + 1)
      node.beta = [-1.0] * (i_max + 1)

    tree.parent.A = [0.0] * (i_max + 1)
    tree.parent.A[0] = 1 # initialize A_0(0) = 1 according to paper's instructions. 

  @staticmethod
  def main(tree, q, i_max, n):
    assert(tree.parent != None) # Can't have a parentless tree.

    # Y and gamma calculations
    DelayTomographyMle.find_y(tree, q, i_max, n)
    print("Gamma values for tree ", tree)
    for node in tree.nodes():
      print(node.id, node.gamma)

    # A calculations
    for i in range(0, i_max + 1):
      DelayTomographyMle.infer_delay(tree, i, q, i_max)

  @staticmethod
  def find_y(k, q, i_max, n):
    for j in k.children():
      DelayTomographyMle.find_y(j, q, i_max, n)
      for m in range(0, n): # for all probes
        k.Y[m] = min(k.Y[m], j.Y[m])
    for i in range(0, i_max + 1): # compute CDF
      assert(n != 0)
      k.gamma[i] = sum([y <= ((i * q) + (q / 2)) for y in k.Y]) / n
      if ((k.gamma[i] <= 0) or (k.gamma[i] > 1)):
        print("Invalid k.gamma[", i, "] = ", k.gamma[i], " for node ", k.id)
        assert(False)

  @staticmethod
  def infer_delay(k, i, q, i_max):
    if (i == 0):
      if (k.children() == []): # leaf nodes
        k.A[i] = k.gamma[i]
      else:
        assert(k.children() != [])
        if (k.left.gamma[i] + k.right.gamma[i] - k.gamma[i] == 0):
          print(i)
          print(k.left.gamma[i])
          print(k.right.gamma[i])
          print(k.gamma[i])
        assert (k.left.gamma[i] + k.right.gamma[i] - k.gamma[i] != 0)
        # closed form solution for binary trees
        k.A[i] = (k.left.gamma[i] * k.right.gamma[i] * 1.0) / (k.left.gamma[i] + k.right.gamma[i] - k.gamma[i])
    else:
      k.A[i] = DelayTomographyMle.solvefor2(k, i)

    # Compute beta
    summation = 0
    for j in range(1, i+1): # 1 to i
      if (k.beta[i-j] <= 0):
        print(i, j, k.beta[i-j])
      assert(k.beta[i-j] > 0)
      summation += (k.parent.A[j] * k.beta[i-j])
    k.beta[i] = (k.gamma[i] - summation)/k.parent.A[0]

    # Compute alpha using least squares
    k.alpha = DelayTomographyMle.least_squares(k, i_max)

    # Recursively process children
    for j in k.children():
      DelayTomographyMle.infer_delay(j, i, q, i_max)

  @staticmethod
  def least_squares(k, i_max):
    E = numpy.matlib.zeros((i_max + 1, i_max + 1))
    # populate E
    for i in range(0, i_max + 1): # row
      for j in range(0, i_max + 1): # column
        if (j > i):
          E[i, j] = 0
        else:
          assert(i - j >= 0)
          E[i, j] = k.parent.A[i-j]

    # populate b
    b = numpy.array(k.A)

    # Construct the problem.
    x = cvxpy.Variable(i_max + 1) # solve for alpha
    objective = cvxpy.Minimize(cvxpy.sum_squares(E*x - b))
    constraints = [0 <= x, sum(x) <= 1]
    prob = cvxpy.Problem(objective, constraints)

    # The optimal objective is returned by prob.solve().
    result = prob.solve()

    # The optimal value for x is stored in x.value.
    ret = []
    for var in x:
      ret += [var.value]
    return ret

  @staticmethod
  def solvefor2(k, i):
    assert(i >= 1)
    # Use equation 8/16 for solution.
    if (k.children() == []):
      summation = 0
      for j in range(0, i): # 0 to i - 1
        summation += k.A[j]
      return k.gamma[i] - summation
    else:
      p  = DelayTomographyMle.compute_p(k, i)
      q  = DelayTomographyMle.compute_q(k)
      c1 = DelayTomographyMle.compute_c1(k, i)
      c2 = DelayTomographyMle.compute_c2(k)
      c3 = DelayTomographyMle.compute_c3(k, i)
      c4 = DelayTomographyMle.compute_c4(k)
      (a, b, c)    = DelayTomographyMle.compute_canonical_quadratic_equation(p, q, c1, c2, c3, c4)
      (sol1, sol2) = DelayTomographyMle.compute_quadratic_solutions(a, b, c)

      # Return second largest solution, i.e., smallest solution in the quadratic case.
      if (sol1 > sol2):
        return sol2
      else:
        return sol1

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # Compute p below.
  @staticmethod
  def compute_p(k, i):
    assert(k.left != None)
    assert(k.right != None)
    assert(i >= 1)
    p = k.gamma[i] - k.A[0]
    if (i == 1):
      return p
    else:
      for j in range(1, i): # i.e., 1 to i-1
        assert(i - j >= 0)
        p += k.A[j] * ((1 - k.left.beta[i - j]) * (1 - k.right.beta[i - j]) - 1)
      return p

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # Compute q below.
  @staticmethod
  def compute_q(k):
    assert(k.left != None)
    assert(k.right != None)
    return (1 - k.left.beta[0]) * (1 - k.right.beta[0]) - 1

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # Compute c1 below.
  @staticmethod
  def compute_c1(k, i):
    assert(k.left != None)
    assert(k.right != None)
    assert(i >= 1)
    summation = 0
    if i == 1:
      summation = 0
    else:
      for j in range(1, i): # i.e., j goes from 1 to i - 1
        assert(i - j >= 0)
        assert(k.left.beta[i - j] > 0)
        summation += k.left.beta[i - j] * k.A[j]
    return k.A[0] * (1 - k.left.gamma[i]/k.A[0] + summation / k.A[0])

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # Compute c2 below.
  @staticmethod
  def compute_c2(k):
    assert(k.left != None)
    assert(k.right != None)
    return k.A[0] * (k.left.beta[0] / k.A[0])

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # Compute c3 below.
  @staticmethod
  def compute_c3(k, i):
    summation = 0
    assert(k.left != None)
    assert(k.right != None)
    assert(i >= 1)
    if i == 1:
      summation = 0
    else:
      for j in range(1, i):
        assert(i - j >= 0)
        assert(k.right.beta[i - j] > 0)
        summation += k.right.beta[i - j] * k.A[j]
    return (1 - k.right.gamma[i]/k.A[0] + summation / k.A[0])

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # Compute c4 below.
  @staticmethod
  def compute_c4(k):
    assert(k.left != None)
    assert(k.right != None)
    return (k.right.beta[0] / k.A[0])

  # Rewrite equation 8/16 as p + qx + (c1 + c2x)(c3 + c4x) = 0
  # In the canonical ax^2 + bx + c = 0 format, this turns into
  # (c2*c4)x^2 + (q +c2c3 + c4c1)x + (p + c1*c3) = 0
  @staticmethod
  def compute_canonical_quadratic_equation(p, q, c1, c2, c3, c4):
    return (c2*c4, q + c2*c3 + c4*c1, p + c1*c3)

  # Apply closed form solution to solve quadratic equation.
  @staticmethod
  def compute_quadratic_solutions(a, b, c):
    assert(b*b - 4 * a * c > 0)
    return ((-b + math.sqrt(b*b - 4*a*c))/(2*a), (-b - math.sqrt(b*b - 4*a*c)) / (2*a))
