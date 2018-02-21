import random

# Link that can hold exactly 1 packet, with a provided bernoulli loss probability
class Link:
    def __init__(self, bernoulli_alpha):
        self.link_queue = []
        self.bernoulli_alpha = bernoulli_alpha

    # Not sure if enforcing queue limit is needed here
    def recv(self, pkt):
        droptest = isdropped()
        if (droptest == False):
            self.link_queue.append(pkt)
        else if (droptest == True):

    def tick(self, tick):
        if(len(self.link_queue) != 0):
            head = self.link_queue[0]
            # "Shift" queue upward one
            self.link_queue = self.link_queue[1:]

    def isdropped():
        rand_number = random.uniform(0,1)
        if rand_number <= bernoulli_alpha:
            return True
        else:
            return False
