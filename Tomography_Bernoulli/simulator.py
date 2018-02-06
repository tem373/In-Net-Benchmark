import sys
import argparse

from network import *

def check_recvrs(num_recvrs):
    if (num_recvrs not in [2, 4]):
        raise argparse.ArgumentTypeError("Available experiments are 2 and 4 receivers")
    return num_recvrs


# Argparse section to take in specified parameters from command-line
parser = argparse.ArgumentParser(description="Network Tomography Simulator with Bernoulli losses.")

required_args = parser.add_argument_group("Required Arguments:")
required_args.add_argument('--num_recvrs', dest='num_recvrs', type=check_recvrs,
    help='Specify 2 or 4 receiver experiment', required=True)
required_args.add_argument('--ticks', dest='ticks', type=int, 
    help='How many rounds of packet traffic to send', required-True)


# Argument Parsing
args = parser.parse_args()
for arg in args:
    print(arg)

# Initialize sender
sender = Sender()

# Based on user input, initialize routers and receivers
if(args.num_recvrs == 2):
    receiver1 = Receiver() #need to add args
    receiver2 = Receiver()
    router = Router()

    # Initialize links (3 separate links)

    for tick in range(0, args.ticks):
        # fill out later
        

else if(args.num_recvrs == 4):
    receiver1 = Receiver() #need to add args
    receiver2 = Receiver()
    receiver3 = Receiver()
    receiver4 = Receiver()

    router1 = Router() 
    router2 = Router()
    router3 = Router()

    # Initialize links (7 separate links)





