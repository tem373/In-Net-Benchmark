#!/usr/bin/python

import math
import numpy as np
import matplotlib.pyplot as plt

global_alpha = 1.3
def geom_intervals(trials=10000000, success_prob=0.02):
    """ In general, provide a probability in the range of .99-.95 to conform
        to the experimental parameters."""

    intervals = np.random.geometric(p=success_prob, size=trials)
    return intervals


def pareto_intervals(beta_min, trials=10000000, alpha=global_alpha):
    """ Must be 1 <= alpha <= 2, closer to 1 -> more bursty."""
    
    intervals = (np.random.pareto(alpha, size=trials) + 1) * beta_min 
    intervals2 = np.round(intervals).astype(int)

    return intervals2


def pareto_mean(beta_min, alpha=global_alpha):
    """ Simply calculates out the mean pareto mean corresponding to 
        u = (aB)/(a-1) """
    mean = float((alpha*beta_min) / (alpha - 1.0))
    return mean
    

def geom_mean(p=0.02):
    
    mean = float(1/p)
    return mean


def find_beta(geom_mean, alpha=global_alpha):
    """ B = ((u * (a-1))/a); alpha set for now """
    beta = (geom_mean * (alpha-1)) / alpha
    return beta


######## Main block ########

# Calculate beta
geom_mean = geom_mean()     # typical link - drop prob = 2%
beta_min = find_beta(geom_mean)
pareto_mean = pareto_mean(beta_min)

print("Geometric mean: " + str(geom_mean))
print("Beta: " + str(beta_min))
print("Pareto mean: " + str(pareto_mean))

# Generate distributions
bernoullis = geom_intervals()
paretos = pareto_intervals(beta_min)

print("Bernoulli:")
print(bernoullis[:500])
print("Max: " + str(max(bernoullis)))
print("Avg: " + str(bernoullis.mean()))
print("Pareto:")
print(paretos[:500])
print("Max: " + str(max(paretos)))
print("Avg: " + str(paretos.mean()))


