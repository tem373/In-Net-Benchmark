
""" VARIABLES
    
    k       = node
    j       = node descended from node k
    A       = 
    Yhat_k  = record of successes/failures (1s and 0s). Actual success queue in leaf
              nodes, estimated from children otherwise
"""

def est_bernoulli_prob(k):
    """ Main function for estimating the bernoulli packet drop probability
    in each link. Takes as input link k and calculates the alpha"""

    #n = len(k.success_queue)

    yhat_queue = []
    gamma_queue = []
    alpha_queue = []

    find_gamma(k)
    infer(k, 1)     # 1 implies certainty of root node succeeding (sender)

    return yhat_queue, gamma_queue, alpha_queue

def find_gamma(k, yhat_queue, gamma_queue):
    """ Add docstring"""

    n = len(k.success_queue)

    yhat_k = []
    gamma_k = 0.0

    # for loop of all the downstream links - maybe pass array of links?
    for j in k.downstream_nodes:
        find_gamma(j)

        for i in n:

            # if not leaf node, check if any children succeeded. 1 if yes, 0 if no 
            if len(k.downstream_nodes) == 0;
                yhat_k.append(k.success_queue[i])
            else:
                counter = 0
                for node in k.downstream_nodes:
                    if (node.success_queue[i] == 1):
                        counter++
                if (counter > 0):
                    yhat_k.append(1)
                else:
                    yhat_k.append(0)
        
        # calculate gamma        
        tempsum = 0
        for i in n:
             tempsum += yhat_k[i]
        gamma_k = float(tempsum) / n

    yhat_queue.append(yhat_k)
    gamma_queue.append(gamma_k)
    #return yhat_k, gamma_k


def infer(k, A, alpha_queue):
    """ Calculates the actual alpha value"""










