import sys
import argparse
import csv

from network import *
from host import *
from algorithms import *
from packet import *

def check_recvrs(num_recvrs):
    if (num_recvrs not in [2, 4]):
        raise argparse.ArgumentTypeError("Available experiments are 2 and 4 receivers")
    return num_recvrs

def check_mode(mode):
    if (mode not in ["sdn", "tomography"]):
        raise argparse.ArgumentTypeError("Run in either <sdn> (smart router) or <tomography> mode")


# Argparse section to take in specified parameters from command-line
parser = argparse.ArgumentParser(description="Network Tomography Simulator with Bernoulli losses.")
optional_args = parser._action_groups.pop()

# Required Args
required_args = parser.add_argument_group("Required Arguments:")
required_args.add_argument('--ticks', dest='ticks', type=int, 
    help='How many rounds of packet traffic to send', required=True)

# Optional Args
optional_args.add_argument('--num_recvrs', dest='num_recvrs', type=check_recvrs,
    help='Specify 2 or 4 receiver experiment', required=False, default=2)

optional_args.add_argument('--mode', dest='mode', type=check_mode,
    help='Run in either <tomography> or <sdn> mode', required=False, default="tomography")
parser._action_groups.append(optional_args)


# Argument Parsing
args = parser.parse_args()
print(args)


############################## 2 Receiver Setup ################################

# Based on user input, initialize routers and receivers
if(args.num_recvrs == 2):

    # Initialize hosts
    receiver1 = Host('receiver1') 
    receiver2 = Host('receiver2')
    router = Host('router', receiver1, receiver2)
    sender = Host('sender', router)

    # Initialize links (3 separate links)
    bernoullis = [0.05, 0.05, 0.05]         # Change at user's discretion
    sender_router_link = Link(bernoullis[0])
    router_recv1_link = Link(bernoullis[1])
    router_recv2_link = Link(bernoullis[2])

    # Calculation Infrastructure
    hosts = [sender, router, receiver1, receiver2]
    yhat_dict = {'sender': [], 'router': [], 'receiver1': [], 'receiver2': []}
    gamma_dict = {'sender': 0, 'router': 0, 'receiver1': 0, 'receiver2': 0}             
    alpha_dict = {'sender': [], 'router': [], 'receiver1': [], 'receiver2': []}

############################### Run Simulation #################################

    for tick in range(0, args.ticks):

        sender.send(tick, sender_router_link)
        sender_router_link.tick(tick, router)
        router.send(tick, router_recv1_link)
        router.send(tick, router_recv2_link)
        router_recv1_link.tick(tick, receiver1)
        router_recv2_link.tick(tick, receiver2)


########################### Tomography calculations ############################
    
        #if(args.mode == "tomography"):
        if(True):

            print(tick)

            for host in hosts:
                yhat, gamma, alpha = est_bernoulli_prob(host, yhat_dict, gamma_dict, alpha_dict)
                
                #yhat_dict[host.name][tick] = yhat
                yhat_dict[host.name].append(yhat)
                gamma_dict[host.name] = gamma
                #alpha_dict[host.name][tick] = alpha
                alpha_dict[host.name].append(alpha)
        
        if(args.mode == "sdn"):
            pass

    # write this to CSV? do something to analyze data
    for host in hosts:

        print(yhat_dict[host.name])

    for host in hosts:
        #fi = open('results/' + host.name + '.csv', 'wb')
        #wr = csv.writer(fi)    
        #for item in alpha_dict[host.name]:
        #    wr.writerow(item)
        with open('results/' + host.name + '.csv', 'w') as outfile:
            for item in alpha_dict[host.name]:
                outfile.write(str(item))
                outfile.write('\n')




############################## 4 Receiver Setup ################################        

if(args.num_recvrs == 4):      # After debugging 2, fill this out
    pass


"""
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



    






