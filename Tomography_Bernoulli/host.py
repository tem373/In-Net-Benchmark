from packet import *

class Host:
    def __init__(self, name, *downstream_nodes):
        self.ready_to_send = True
        self.in_order_rx_seq = -1       # Sequence number accounting
        self.name = name        
        self.downstream_nodes = []
        self.success_queue = []

        # To check if it is a receiver
        if (len(downstream_nodes) == 0):
            self.downstream_nodes = []
            
        else:
            for node in downstream_nodes:
                self.downstream_nodes.append(node)


    def send(self, tick, *links):
        """If multiple links are provide, multicast traffic is being sent"""

        # Note: no mechanism for retransmitting a dropped packet here
        if(self.ready_to_send == True):
            
            # Create new packet
            new_seq_num = self.in_order_rx_seq + 1
            
            # Deliver packet to the link (or links if multicast)
            for link in links:
                new_packet = Packet(tick)

                # Check if packet got dropped
                if(self.success_queue[tick] == 0):                
                    new_packet.was_dropped = True

                link.recv(new_packet)

            self.ready_to_send = False


    def recv(self, pkt, tick):
        if (pkt.was_dropped == False):        
            self.in_order_rx_seq = pkt.seq_num
            self.ready_to_send = True

            self.success_queue.append(1)


        else:
            self.in_order_rx_seq = pkt.seq_num
            self.ready_to_send = True
            
            # Accounting for dropped packets
            self.success_queue.append(0)


