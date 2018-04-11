

def est_bernoulli_prob(k, yhat_queue, gamma_queue, alpha_queue, tick):
    """ Main function for estimating the bernoulli packet drop probability
    in each link. Takes as input link k and calculates the alpha"""

    yhat, gamma = find_gamma(k, yhat_queue, gamma_queue, tick)
    alpha = infer(k, 1, alpha_queue, gamma_queue)     #1 implies certainty of root node succeeding

    return yhat, gamma, alpha


def find_gamma(k, yhat_queue, gamma_queue, tick):
    """ Computes gamma value and success values of non-receiver routers"""

    n = tick+1

    yhat_k = 0
    gamma_k = 0.0

    if not k.downstream_nodes:
        for i in range(0, n):        
            yhat_k = k.success_queue[i]

    else:   
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
    #print(k.name)
    #print("gamma: " + str(gamma))

    #local_gamma = A - gamma
    pre_alpha = 1 - gamma

    #print("localgamma: " + str(local_gamma) + "\n")

    if (len(k.downstream_nodes) > 0):

        #A = pre_alpha
        A = gamma
        #alpha = pre_alpha - (1 - A)
        #A = 1 - pre_alpha
        for j in k.downstream_nodes:
            infer(j, A, alpha_queue, gamma_queue)
            
            

    #elif not k.downstream_nodes:
        #A = pre_alpha        
    alpha = pre_alpha
    #alpha = 1 - (A + pre_alpha)    
    #alpha = local_gamma
    
    return alpha


