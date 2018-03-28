
""" VARIABLES
    
    k       = node
    j       = node descended from node k
    A       = 
    Yhat_k  = record of successes/failures (1s and 0s). Actual success queue in leaf
              nodes, estimated from children otherwise
"""

def est_bernoulli_prob(k, yhat_queue, gamma_queue, alpha_queue, tick):
    """ Main function for estimating the bernoulli packet drop probability
    in each link. Takes as input link k and calculates the alpha"""

    yhat, gamma = find_gamma(k, yhat_queue, gamma_queue, tick)
    alpha = infer(k, 1, alpha_queue, gamma_queue)     # 1 implies certainty of root node succeeding (sender)

    #print("Yhat: " + str(yhat) + " gamma: " + str(gamma) + " alpha: " + str(alpha))

    return yhat, gamma, alpha


def find_gamma(k, yhat_queue, gamma_queue, tick):
    """ Computes gamma value and success values of non-receiver routers"""

    n = tick+1

    yhat_k = 0
    gamma_k = 0.0

    if not k.downstream_nodes:
        for i in range(0, n):        
            yhat_k = k.success_queue[i]

    # for loop of all the downstream links - maybe pass array of links?
    else:
        #print("Router or sender")    
        for j in k.downstream_nodes:
            find_gamma(j, yhat_queue, gamma_queue, tick)

            for i in range(0, n):

                counter = 0
                for node in k.downstream_nodes:
                    if (node.success_queue[i] == 1):
                        counter = counter + 1
                if (counter > 0):
                    
                    yhat_k = 1
                else:
                    
                    yhat_k = 0

    # calculate gamma        
    tempsum = 0
    for i in range(1, n):
        tempsum += yhat_queue[k.name][i-1]  # yhat_queue only consists of n-1 elements
    tempsum += yhat_k
    gamma_k = float(tempsum) / n

    if(k.name == 'sender'):
        yhat_k = 1
        gamma_k = 1.0

    return yhat_k, gamma_k



def infer(k, A, alpha_queue, gamma_queue):
    """ Calculates the actual alpha value"""

    gamma = gamma_queue[k.name]

    pre_alpha = 1 - gamma
    #print(k.name + " pre-alpha: " + str(pre_alpha))
    #if(k.name == 'sender'):
    #    alpha = 0
    #    return alpha

    #if not k.downstream_nodes:
    #    A = pre_alpha        
    #    alpha = pre_alpha
    #    return alpha

    if(k.downstream_nodes):
        
        #temp = 0.0

        #if(k.name == 'sender'):
        #    alpha = 0
        #    return alpha

        A = pre_alpha
        alpha = pre_alpha # - (1 - A)
        #A = 1 - pre_alpha
        for j in k.downstream_nodes:
            infer(j, A, alpha_queue, gamma_queue)
            
        return alpha

    elif not k.downstream_nodes:
        #A = pre_alpha        
        alpha = pre_alpha - (1 - A)
        
    
        return alpha







# GARBAGE CODE

    # "Solvefor" method simple implementation
    #k_gamma = (1 - gamma_queue[k.name]) / A

    #print("gamma queue: " + str(gamma_queue))
    #print("k_gamma: " + str(k_gamma))

    #mult_result = 1
    
    #if(k.downstream_nodes):
    #    for j in k.downstream_nodes:
    #        j_gamma = gamma_queue[j.name]
    #        mult_result = mult_result * ((1 - j_gamma) / A)

    #A_k = k_gamma / mult_result

    #alpha_k = float(A_k) / A

    #print("Alpha K: " + str(alpha_k))

    #return alpha_k

    #for j in k.downstream_nodes:
    #    infer(j, A_k, alpha_queue, gamma_queue)

    #return alpha_k







