#! /usr/bin/python3
import numpy.random
import statistics
import sys

# Simulate 1M ticks
num_ticks = 1000000

# track whether or not there was a drop
drops = [0] * num_ticks

# simulate 10K ticks
for i in range(0, num_ticks):
  if (numpy.random.random() < float(sys.argv[1])):
    drops[i] = 1
  else:
    drops[i] = 0

# run length encode the drops
rle_vals = []   # values of each run
rle_lens = []   # length of each run
for i in range(0, num_ticks):
  assert(len(rle_vals) == len(rle_lens))
  if len(rle_vals) == 0 or drops[i] != rle_vals[-1]: # new run
    rle_vals += [drops[i]]
    rle_lens += [1]
  else: # extend old run
    assert(len(rle_vals) != 0)
    assert(drops[i] == rle_vals[-1])
    rle_lens[-1] += 1
assert(len(rle_vals) == len(rle_lens))
assert(sum(rle_lens) == len(drops))
rle_array = zip(rle_vals, rle_lens)

print("total drops:", sum(drops), "in", num_ticks, "ticks")
burst_error_array = list(filter(lambda x : x[0] == 1, rle_array))
print("Avg. burst error size: ", statistics.mean([length for (val, length) in burst_error_array]))
