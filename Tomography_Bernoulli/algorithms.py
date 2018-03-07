
""" VARIABLES
    
    k       = node
    j       = node descended from node k
    A       = 
    Yhat_k  = record of successes/failures (1s and 0s). Actual success queue in leaf
              nodes, estimated from children otherwise
"""

def est_bernoulli_prob(k, yhat_queue, gamma_queue, alpha_queue):
    """ Main function for estimating the bernoulli packet drop probability
    in each link. Takes as input link k and calculates the alpha"""

    #n = len(k.success_queue)

    #yhat_queue = []
    #gamma_queue = []
    #alpha_queue = []

    yhat, gamma = find_gamma(k, yhat_queue, gamma_queue)
    alpha = infer(k, 1, alpha_queue, gamma_queue)     # 1 implies certainty of root node succeeding (sender)

    return yhat, gamma, alpha


def find_gamma(k, yhat_queue, gamma_queue):
    """ Add docstring"""

    n = len(k.success_queue)

    yhat_k = 0
    gamma_k = 0.0

    # for loop of all the downstream links - maybe pass array of links?
    for j in k.downstream_nodes:
        find_gamma(j, yhat_queue, gamma_queue)

        for i in range(1, n):

            # if not leaf node, check if any children succeeded. 1 if yes, 0 if no 
            if len(k.downstream_nodes) == 0:
                #yhat_k.append(k.success_queue[i])
                yhat_k = k.success_queue[i]
                print("success queue: " + str(k.success_queue[i]))
            
            else:
                counter = 0
                for node in k.downstream_nodes:
                    if (node.success_queue[i] == 1):
                        counter = counter + 1
                if (counter > 0):
                    #yhat_k.append(1)
                    yhat_k = 1
                else:
                    #yhat_k.append(0)
                    yhat_k = 0
        #print("Yhat: " + str(yhat_k))

        # calculate gamma        
        tempsum = 0
        for i in range(1, n):
            #tempsum += yhat_k[i]
            tempsum += yhat_queue[i]
        
        if(n > 0):
            gamma_k = float(tempsum) / n

    #print("Yhat: " + str(yhat_k))
    #print("Gamma: " + str(gamma_k))

    return yhat_k, gamma_k
    

    #yhat_queue.append(yhat_k)
    #gamma_queue.append(gamma_k)
    #return yhat_k, gamma_k


def infer(k, A, alpha_queue, gamma_queue):
    """ Calculates the actual alpha value"""

    # "Solvefor" method simple implementation
    k_gamma = (1 - gamma_queue[k.name]) / A
    mult_result = 1    
    for j in k.downstream_nodes:
        j_gamma = gamma_queue[j.name]
        mult_result = mult_result * ((1 - j_gamma) / A)

    A_k = mult_result / k_gamma

    alpha_k = float(A_k) / A

    #print("Alpha K: " + str(alpha_k))

    return alpha_k
    
    #alpha_queue.append(alpha_k)

    for j in k.downstream_nodes:
        infer(j, A_k, alpha_queue, gamma_queue)







