import random

# Link that can hold exactly 1 packet, with a provided bernoulli loss probability
class Link:
    def __init__(self, bernoulli_alpha):
        self.link_queue = []
        self.bernoulli_alpha = bernoulli_alpha
        #self.name = name
        self.total_received_pkts = 0
        self.total_dropped_pkts = 0

    def loss_rate(self):
        if (self.total_received_pkts == 0):
          return -1
        else:
          return (self.total_dropped_pkts * 1.0) / self.total_received_pkts

    # Not sure if enforcing queue limit is needed here
    def recv(self, pkt):
        
        if(pkt.was_dropped == True):
            self.link_queue.append(pkt)
        elif(pkt.was_dropped == False):
            self.total_received_pkts += 1
            droptest = self.isdropped()
            if (droptest == False):
                self.link_queue.append(pkt)
            elif (droptest == True):
                self.total_dropped_pkts += 1
                pkt.was_dropped = True
                self.link_queue.append(pkt)
        #else:
        #    self.link_queue.append(pkt)
        #print("Drop status: " + str(pkt.was_dropped))

    def tick(self, tick, host):
        if(len(self.link_queue) != 0):
            head = self.link_queue[0]
            # "Shift" queue upward one
            self.link_queue = self.link_queue[1:]
            host.recv(head, tick)

    def isdropped(self):
        rand_number = random.uniform(0,1)

        if rand_number < self.bernoulli_alpha:
            return True
        else:
            return False
