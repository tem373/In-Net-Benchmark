# Class representing a very simple packet

class Packet:

    # Only data point needed is a simple sequence number
    def __init__(self, seq_num): #sent_tick, seq_num):
        #self.sent_tick = sent_tick
        self.seq_num = seq_num
        self.was_dropped = False

    # Allows user to return the sequence number
    def __repr__(self):
        return str(self.seq_num)



