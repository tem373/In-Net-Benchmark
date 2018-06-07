import numpy

LOW_ESCAPE_PROBABILITY = 0.001 # Low probability of escaping a state in the Gilbert-Elliot model

class LossDistribution:
  def __init__(self, t_loss_prob, t_loss_type):
    assert(t_loss_type in ["bernoulli", "gilbert_elliot"])
    self.incoming_loss_prob = t_loss_prob
    self.loss_type = t_loss_type
    if (t_loss_type == "gilbert_elliot"):
      # steady-state probability of being in "bad" is the same as self.incoming_loss_prob
      self.link_state = "bad" if (numpy.random.random() < self.incoming_loss_prob) else "good"
      prob_escape_good = LOW_ESCAPE_PROBABILITY
      self.prob_escape_bad = (prob_escape_good / self.incoming_loss_prob) - prob_escape_good
      assert((self.prob_escape_bad > 0) and (self.prob_escape_bad < 1))

  # State transitions for Gilbert-Elliot loss model
  # Run this even if there aren't packets to maintain correctness of model.
  def state_transition(self):
    if (self.loss_type == "gilbert_elliot"):
      if (self.link_state == "good"):
        self.link_state = "bad" if (numpy.random.random() < self.prob_escape_good) else "good"
      else:
        assert(self.link_state == "bad")
        self.link_state = "good" if (numpy.random.random() < self.prob_escape_bad) else "bad"

  # deliver probe?
  def deliver_probe(self):
    if (self.loss_type == "bernoulli"):
      delivered = not (numpy.random.random() < self.incoming_loss_prob)
    else:
      assert(self.loss_type == "gilbert_elliot")
      delivered = (self.link_state == "good")
    return delivered
