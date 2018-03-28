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
    return mode

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

################################################################################
############################## 2 Receiver Setup ################################
################################################################################

# Based on user input, initialize routers and receivers
if(args.num_recvrs == 2):

    # Initialize hosts
    receiver1 = Host('receiver1') 
    receiver2 = Host('receiver2')
    router = Host('router', receiver1, receiver2)
    sender = Host('sender', router)

    # Initialize links (3 separate links)
    bernoullis = [0.2, 0.1, 0.1]         # Change at user's discretion
    sender_router_link = Link(bernoullis[0])
    router_recv1_link = Link(bernoullis[1])
    router_recv2_link = Link(bernoullis[2])

    #Initial link to set successes in sender
    initial_link = Link(0.0)

    # Calculation Infrastructure
    hosts = [sender, router, receiver1, receiver2]
    yhat_dict = {'sender': [], 'router': [], 'receiver1': [], 'receiver2': []}
    gamma_dict = {'sender': 0, 'router': 0, 'receiver1': 0, 'receiver2': 0}             
    alpha_dict = {'sender': [], 'router': [], 'receiver1': [], 'receiver2': []}

    # reporting purposes
    convergence = False
    conv_tick = 0

############################### Run Simulation #################################

    for tick in range(0, args.ticks):
        # Initial Send
        first_packet = Packet(tick)
        initial_link.recv(first_packet)
        initial_link.tick(tick, sender)

        sender.send(tick, sender_router_link)
        sender_router_link.tick(tick, router)
        router.send(tick, router_recv1_link, router_recv2_link)
        #router.send(tick, router_recv2_link)
        router_recv1_link.tick(tick, receiver1)
        router_recv2_link.tick(tick, receiver2)

        sender.ready_to_send = True


########################### Tomography calculations ############################
    
        if(args.mode == "tomography"):

            print("tick: " + str(tick))

            for host in hosts:
                yhat, gamma, alpha = est_bernoulli_prob(host, yhat_dict, gamma_dict, alpha_dict, tick)
                #print(host.name + " alpha: " + str(alpha))
                
                yhat_dict[host.name].append(yhat)
                gamma_dict[host.name] = gamma
                alpha_dict[host.name].append(alpha)

                if(host.name in('receiver1', 'receiver2')):
                    alpha_dict[host.name][tick] -= alpha_dict['router'][tick]

############################### SDN calculations ###############################
        
        if(args.mode == "sdn"):
            # just count the success queues and do elementary calculations with
            # data collected by the routers

            # placeholder alpha value for router
            router_alpha = 0.0

            for host in hosts:
                yhat = host.success_queue[tick]
                yhat_dict[host.name].append(yhat)
                gamma = sum(yhat_dict[host.name]) / len(yhat_dict[host.name])
                #print(str(host.name) + " gamma: " + str(gamma))

                # Alpha calculations
                pre_alpha = 1 - gamma
                print(str(host.name) + " pre-alpha: " + str(pre_alpha))
                
                # if non-leaf, give pre-alpha to placeholder (sender will be counted over)
                if (host.downstream_nodes):
                    router_alpha = pre_alpha
                    alpha = pre_alpha

                # if leaf, subtract placeholder to get individual link alpha
                if not host.downstream_nodes:
                    alpha = pre_alpha - router_alpha
                
                # Append for reporting
                print(str(host.name) + " alpha: " + str(alpha))
                gamma_dict[host.name] = gamma
                alpha_dict[host.name].append(alpha)

                # convergence check
                #if(convergence == False):
                #    conv_tick = tick
                #    for i in range(0, 2):
                #        if bernoullis[i] - alpha <= .1:
                #            convergence = True
                            
            
################################## Reporting ###################################


    # write this to CSV? do something to analyze data
    for host in hosts:

        print(host.name + " Yhat:  " + str(yhat_dict[host.name]))
        print(host.name + " gamma: %.4f" % gamma_dict[host.name])
        formatted_alpha = ['%.4f' % elem for elem in alpha_dict[host.name]]
        #print(host.name + " alpha: " + str(alpha_dict[host.name]))
        print(host.name + " alpha: " + str(formatted_alpha))

    for host in hosts:

        with open('results/' + host.name + '.csv', 'w') as outfile:
            for item in alpha_dict[host.name]:
                outfile.write(str(item))
                outfile.write('\n')

    #print("Convergence achieved at tick: " + str(conv_tick))

################################################################################
############################## 4 Receiver Setup ################################        
################################################################################

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



    






