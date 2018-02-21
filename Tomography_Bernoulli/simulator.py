import sys
import argparse
import csv

import network
import host
import algorithms

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


############################### Initialization #################################

# Based on user input, initialize routers and receivers
if(args.num_recvrs == 2):
    receiver1 = host() #need to add args
    receiver2 = host()
    router = host(receiver1, receiver2)

    # Initialize sender
    sender = host(router)

    # Initialize links (3 separate links)
    bernoullis = [0.05, 0.02, 0.01]         # Change at user's discretion
    sender_router_link = Link(bernoullis[0])
    router_recv1_link = Link(bernoullis[1])
    router_recv2_link = Link(bernoullis[2])


############################### Run Simulation #################################

    for tick in range(0, args.ticks):
        sender.send(tick, sender_router_link)
        sender_router_link.tick(tick)
        router.send(tick, router_recv1_link)
        router.send(tick, router_recv2_link)


########################### Algorithm calculations #############################

    iterated_bernoullis = []
    recv_hosts = [router, receiver1, receiver2]  # definitely need a better way to do this
                                                    # (needs to be recursive - change later   

    for host in recv_hosts:
        y, g, b = est_bernoulli_prob(host)
        iterated_bernoullis.append(b)
        

    # write this to CSV? do something to analyze data
    fi = open(results.csv, 'wb')
    wr = csv.writer(fi)
    
    for item in iterated_bernoullis:
        wr.writerow(item)





        
"""
else if(args.num_recvrs == 4):
    receiver1 = host() 
    receiver2 = host()
    receiver3 = host()
    receiver4 = host()

    router1 = host(router2, router3) 
    router2 = host(receiver1, receiver2)
    router3 = host(receiver3, receiver4)

    # Initialize sender
    sender = host(router1)

    # Initialize links (7 separate links)
    bernoullis = [0.05, 0.02, 0.04, 0.01, 0.025, 0.035, 0.015] # Change at user's discretion
    sender_router1_link = Link(bernoullis[0])
    router1_router2_link = Link(bernoullis[1])
    router1_router3_link = Link(bernoullis[2])

    router2_recv1_link = Link(bernoullis[3])
    router2_recv2_link = Link(bernoullis[4])
    router3_recv3_link = Link(bernoullis[5])
    router3_recv4_link = Link(bernoullis[6])
"""



    






