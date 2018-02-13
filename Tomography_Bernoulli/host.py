import packet

class host:
    def __init__(self):
        self.ready_to_send = True
        self.in_order_rx_seq = -1       # Sequence number accounting


    def send(self, tick, link):

        # Note: no mechanism for retransmitting a dropped packet here
        if(self.ready_to_send = True):
            
            # Create new packet
            new_seq_num = self.in_order_rx_seq + 1
            new_packet = Packet(tick, new_seq_num)
            
            # Deliver packet to the link
            link.recv(new_packet)

            # possibly have to add a packet sent time
            self.ready_to_send = False


    def recv(self, pkt, tick):
        # Update sequence numbers        
        if (pkt.seq_num - self.in_order_rx_seq == 1):
            self.in_order_rx_seq = pkt.seq_num
            self.ready_to_send = True


    # Possibly don't need these two functions, hold onto for now
    def duplicate(self, pkt):
        pass

    def report():
        pass
