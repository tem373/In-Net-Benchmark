import sys
import argparse

from network import *

def check_recvrs(num_recvrs):
    if (num_recvrs not in [2, 4]):
        raise argparse.ArgumentTypeError("Available experiments are 2 and 4 receivers")
    return num_recvrs


# Argparse section to take in specified parameters from command-line
parser = argparse.ArgumentParser(description="")

required_args = parser.add_argument_group("Required Arguments:")
required_args.add_argument('--num_recvrs', dest='num_recvrs', type=check_recvrs,
    help='Specify 2 or 4 receiver experiment', required=True)
required_args.add_argument('--ticks', dest='ticks', type=int, 
    help='How many rounds of packet traffic to send', required-True)


# Argument Parsing
args = parser.parse_args()
for arg in args:
    print(arg)


