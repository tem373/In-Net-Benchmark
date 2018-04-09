import sys
import argparse
import csv
import os
import glob

from network import *
from host import *
from algorithms import *
from packet import *

################################################################################
############################### Argparse Setup #################################
################################################################################

def check_recvrs(num_recvrs):
    if (num_recvrs not in ['2', '4', '8', '16', '32', '64', '128', '256']):
        raise argparse.ArgumentTypeError("Available experiments are 2^n up to 2^n = 128 receivers")
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
    help='Specify number of receivers for this experiment', required=False, default=2)

optional_args.add_argument('--mode', dest='mode', type=check_mode,
    help='Run in either <tomography> or <sdn> mode', required=False, default="tomography")
parser._action_groups.append(optional_args)

# Argument Parsing
args = parser.parse_args()
print(args)


################################################################################
###################### Network Topology Setup Functions ########################
################################################################################

def network_setup(num_recvrs):
    """Sets up the network topology based on a max-heap structure for the 
    hosts and links"""

    link_array = []
    host_array = []

    ######## LINK SETUP ########
    total_links = 2 * num_recvrs                    # omit initial link
    bernoulli_array = bernoulli_setup(total_links, 0.1) # Can change this to change true alpha

    # IF YOU WANT TO EDIT THE BERNOULLIS BY HAND, DO SO HERE
    #
    # IF YOU WANT TO EDIT THE BERNOULLIS BY HAND, DO SO HERE

    for i in range(0, total_links):
        if (i == 0):
            link_array.append(Link(0.0))    # Initial link will never fail (alpha = 0)
        else:
            link_array.append(Link(bernoulli_array[i]))

    #TODO: Figure out a scheme for algorithmically generating descriptive names for links
        

    ######## NODE SETUP ########    
    # Receiver setup
    receiver_array = []
    for j in range(0, num_recvrs):
        name = 'receiver{}'.format(j+1)
        receiver_array.append(Host(name))

    # Router setup
    router_array = []
    for k in range(0, num_recvrs): #in a heap the receivers are 1/2 of the nodes
        if (k == 0):
            name = 'sender'
        else:
            name = 'router{}'.format(k)
            
        router_array.append(Host(name))

    # Concatenate the router and receiver lists
    host_array = router_array + receiver_array

    # Connect the nodes
    incr = num_recvrs-1       # start at the last router and work down
    while(incr > 0):
        node = host_array[incr]
        if (incr > 0):
            node.downstream_nodes.append(host_array[(2 * incr)])
            node.downstream_nodes.append(host_array[(2 * incr) + 1])

        elif (incr == 0):
            node.downstream_nodes.append(host_array[incr+1])    # sender has only 1 node

        incr = incr - 1


    return link_array, host_array


def bernoulli_setup(total_links, default_bernoulli):
    """Creates an array containing the link bernoulli drop probabilities
    TODO: add ability for user to customize from the command line"""

    bernoulli_array = []

    for i in range(0, total_links):
        bernoulli_array.append(default_bernoulli)

    return bernoulli_array


def tomography_reporting(tick, host_array, yhat_dict, gamma_dict, alpha_dict):
    """Encapsulation of the tomography reporting, to be run inside 
    run_simulation()"""

    print("Tick: " + str(tick))

    for host in host_array:
        yhat, gamma, alpha = est_bernoulli_prob(host, yhat_dict, gamma_dict, alpha_dict, tick)

        yhat_dict[host.name].append(yhat)
        gamma_dict[host.name] = gamma
        alpha_dict[host.name].append(alpha)

    # Need to figure out a way to subtract upstream links


def sdn_reporting(tick, host_array, yhat_dict, gamma_dict, alpha_dict):
    """Encapsulation of the SDN reporting, to be run inside run_simulation()"""

    print("Tick: " + str(tick))
    router_alpha = 0.0

    for host in host_array:
        yhat = host.success_queue[tick]
        yhat_dict[host.name].append(yhat)
        gamma = sum(yhat_dict[host.name]) / len(yhat_dict[host.name])
        
        # Alpha Calculations
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


def run_simulation(ticks, link_array, host_array, yhat_dict, gamma_dict, alpha_dict):
    """A note on how the simulation runs: the links and nodes are stored as
    heaps in arrays. When the simulation runs, the links simply send to the 
    router sharing their incremented position in the array. See the below 4 recv example:

    R = [s, r1, r2,  r3,  rv1, rv2, rv3, rv4]
         ^   ^   ^    ^    ^    ^    ^    ^
         | \ | \ |  \ | \  |  \ |  \ |  \ |
            >   >    >   >     >    >    >
    L = [i, sr, r12, r13, rv1, rv2, rv3, rv4]
    """

    num_recv = int(len(host_array) / 2)
    num_other = num_recv

    for tick in range(0, ticks):

        # Run the traffic through the network
        first_packet = Packet(tick)
        for i in range(0, len(link_array)):     # Run through all links

            # Initial link
            if (i == 0):
                link_array[i].recv(first_packet)
            
                # All links perform this step
            link_array[i].tick(tick, host_array[i])
            
            # Sender performs this step (since it has only 1 downstream node)
            if (i == 0):
                link = link_array[i+1]
                host_array[i].send(tick, link)
            

            # All <routers> must perform this step (but not sender or receivers)
# MAY NEED TO FIX
            if (i > 0 and i < num_other):
                # Create the two downstream links to the node
                # Links after sender are located at 2i and 2i+1 (heap property)                    
                link1 = link_array[(2 * i)]
                link2 = link_array[(2 * i) + 1]                
                host_array[i].send(tick, link1, link2)
                

        
        # Reset sender to be ready to send
        host_array[0].ready_to_send = True


        # Estimation - Tomography
        if(args.mode == 'tomography'):
            tomography_reporting(tick, host_array, yhat_dict, gamma_dict, alpha_dict)

        # Estimation - SDN
        if(args.mode == 'sdn'):
            sdn_reporting(tick, host_array, yhat_dict, gamma_dict, alpha_dict)


################################################################################
################################ Setup and Run #################################
################################################################################

num_recvrs = int(args.num_recvrs)
link_heap, host_heap = network_setup(num_recvrs)
yhat_dict = {}
gamma_dict = {}
alpha_dict = {}
    
for host in host_heap:
    # yhat_dict
    yhat_dict[host.name] = []
    
    # gamma_dict
    gamma_dict[host.name] = 0

    # alpha_dict
    alpha_dict[host.name] = []

run_simulation(args.ticks, link_heap, host_heap, yhat_dict, gamma_dict, alpha_dict)


################################################################################
################################# Reporting ####################################
################################################################################

# Delete results of last run so not to confuse current results
files = glob.glob('results/*')
for f in files:
    os.remove(f)

# IMPORTANT: THIS WILL NEED TO BE HEAVILY EDITED

for host in host_heap:

    print(host.name + " Yhat:  " + str(yhat_dict[host.name]))
    print(host.name + " gamma: %.4f" % gamma_dict[host.name])
    formatted_alpha = ['%.4f' % elem for elem in alpha_dict[host.name]]
    #print(host.name + " alpha: " + str(alpha_dict[host.name]))
    print(host.name + " alpha: " + str(formatted_alpha))

for host in host_heap:

    with open('results/' + host.name + '.csv', 'w') as outfile:
        for item in alpha_dict[host.name]:
            outfile.write(str(item))
            outfile.write('\n')

# IMPORTANT: THIS WILL NEED TO BE HEAVILY EDITED



"""
############################## 2 Receiver Setup ################################


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
"""

"""
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
"""

########################### Tomography calculations ############################

"""    
        if(args.mode == "tomography"):

            print("tick: " + str(tick))

            for host in hosts:
                yhat, gamma, alpha = est_bernoulli_prob(host, yhat_dict, gamma_dict, alpha_dict, tick)
                #print(host.name + " alpha: " + str(alpha))
                
                yhat_dict[host.name].append(yhat)
                gamma_dict[host.name] = gamma
                alpha_dict[host.name].append(alpha)

                # Correcting for upstream losses
                if(host.name in('receiver1', 'receiver2')):
                    alpha_dict[host.name][tick] -= alpha_dict['router'][tick]

"""
############################### SDN calculations ###############################
"""        
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

"""                            
"""            
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
"""

"""
############################## 4 Receiver Setup ################################        

if(args.num_recvrs == 4):      # After debugging 2, fill this out

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



    






