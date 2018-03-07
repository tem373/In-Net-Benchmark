from packet import *

class Host:
    def __init__(self, name, *downstream_nodes):
        self.ready_to_send = True
        self.in_order_rx_seq = -1       # Sequence number accounting
        self.name = name        
        self.downstream_nodes = []

        # To keep track of 
        self.success_queue = []

        # To check if it is a receiver
        if (len(downstream_nodes) == 0):
            self.downstream_nodes = []
            
        else:
            for node in downstream_nodes:
                self.downstream_nodes.append(node)


    def send(self, tick, link):

        # Note: no mechanism for retransmitting a dropped packet here
        if(self.ready_to_send == True):
            
            # Create new packet
            new_seq_num = self.in_order_rx_seq + 1
            new_packet = Packet(tick, new_seq_num)
            
            # Deliver packet to the link
            link.recv(new_packet)

            # possibly have to add a packet sent time
            self.ready_to_send = False
            print("Host " + self.name + " sent packet #: " + str(new_packet.seq_num))


    def recv(self, pkt, tick):
        # Update sequence numbers        
        if (pkt.seq_num - self.in_order_rx_seq == 1):
            self.in_order_rx_seq = pkt.seq_num
            self.ready_to_send = True

            # Accounting for dropped packet
            # Only leaf nodes can perform measurement (we here assume routers have
            # no measurement functionality. Perform this test to see if a node
            # is an endpoint and if so measure successes/failures
            if (len(self.downstream_nodes) == 0):
                self.success_queue.append(1)
            else:
                self.success_queue.append(0)

        else:
            self.in_order_rx_seq = pkt.seq_num
            self.ready_to_send = True
            
            # Accounting for dropped packets
            self.success_queue.append(0)

        print("Host " + self.name + " received packet #: " + str(pkt.seq_num))
        print("Host " + self.name + " success queue: " + str(self.success_queue))










