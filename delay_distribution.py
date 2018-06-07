import numpy
ALPHA = 1.3

class DelayDistribution:
  def __init__(self, t_mean_delay, t_delay_type):
    assert(t_delay_type in ["exponential", "pareto"])
    assert(t_mean_delay > 0)
    self.mean_delay = t_mean_delay
    self.delay_type = t_delay_type
    self.beta_min = (self.mean_delay * (ALPHA-1)) / ALPHA

  def delay_sample(self):
    if (self.delay_type == "exponential"):
      return numpy.random.exponential(1/self.mean_delay)
    elif (self.delay_type == "pareto"):
      return (numpy.random.pareto(ALPHA) + 1)* self.beta_min
    else:
      assert(False) 
