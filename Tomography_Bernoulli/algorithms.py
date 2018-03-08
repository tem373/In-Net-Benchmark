
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

    #n = len(k.success_queue)
    n = tick+1    
    

    yhat_k = 0
    gamma_k = 0.0

    # for loop of all the downstream links - maybe pass array of links?
    for j in k.downstream_nodes:
        find_gamma(j, yhat_queue, gamma_queue, tick)

        for i in range(0, n):

            #print(k.name + ": downstream nodes: " + str(len(k.downstream_nodes)))

            # if not leaf node, check if any children succeeded. 1 if yes, 0 if no 
            if not k.downstream_nodes:
                #yhat_k.append(k.success_queue[i])
                yhat_k = k.success_queue[i]
                print("success queue: " + str(k.success_queue[i]))
            
            else:
                #print("didnt reach success queue")
                counter = 0
                for node in k.downstream_nodes:
                    if (node.success_queue[i] == 1):
                        counter = counter + 1
                if (counter > 0):
                    
                    yhat_k = 1
                else:
                    
                    yhat_k = 0
        
        #print("Yhat: " + str(yhat_k))

        # calculate gamma        
        tempsum = 0
        for i in range(1, n):
            
            tempsum += yhat_queue[k.name][i-1]
        if(n > 0):
            gamma_k = float(tempsum) / n

    #print("Yhat: " + str(yhat_k))
    #print("Gamma: " + str(gamma_k))

    return yhat_k, gamma_k



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

    #return alpha_k

    for j in k.downstream_nodes:
        infer(j, A_k, alpha_queue, gamma_queue)

    return alpha_k





