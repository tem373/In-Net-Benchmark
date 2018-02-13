import sys
import argparse

import network
import host

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
sender = host()

# Based on user input, initialize routers and receivers
if(args.num_recvrs == 2):
    receiver1 = host() #need to add args
    receiver2 = host()
    router = host()

    # Initialize links (3 separate links)
    bernoullis = [0.05, 0.02, 0.01]         # Change at user's discretion
    sender_router = Link(bernoullis[0])
    router_recv1 = Link(bernoullis[1])
    router_recv2 = Link(bernoullis[2])

    for tick in range(0, args.ticks):
        # fill out later
        

else if(args.num_recvrs == 4):
    receiver1 = host() #need to add args
    receiver2 = host()
    receiver3 = host()
    receiver4 = host()

    router1 = host() 
    router2 = host()
    router3 = host()

    # Initialize links (7 separate links)
    bernoullis = [0.05, 0.02, 0.04, 0.01, 0.025, 0.035, 0.015] # Change at user's discretion
    sender_router1 = Link(bernoullis[0])
    router1_router2 = Link(bernoullis[1])
    router1_router3 = Link(bernoullis[2])

    router2_recv1 = Link(bernoullis[3])
    router2_recv2 = Link(bernoullis[4])
    router3_recv3 = Link(bernoullis[5])
    router3_recv4 = Link(bernoullis[6])





