import numpy
ALPHA = 1.3

class DelayDistribution:
  def __init__(self, t_mean_delay, t_delay_type):
    assert(t_delay_type in ["geometric", "pareto", "uniform"])
    assert(t_mean_delay > 0)
    self.mean_delay = t_mean_delay
    self.delay_type = t_delay_type
    self.beta_min = (self.mean_delay * (ALPHA-1)) / ALPHA

  def delay_sample(self):
    if (self.delay_type == "geometric"):
      return numpy.random.geometric(1.0 / (self.mean_delay + 1)) - 1
    elif (self.delay_type == "pareto"):
      return (numpy.random.pareto(ALPHA) + 1)* self.beta_min
    elif (self.delay_type == "uniform"):
      return numpy.random.random_integers(0, 2 * self.mean_delay)
    else:
      assert(False)
