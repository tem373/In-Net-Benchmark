

def est_bernoulli_prob(k, yhat_queue, gamma_queue, alpha_queue, tick, host_array):
    """ Main function for estimating the bernoulli packet drop probability
    in each link. Takes as input link k and calculates the alpha"""

    yhat, gamma = find_gamma(k, yhat_queue, gamma_queue, tick)
    alpha = infer(k, 1, gamma_queue, host_array)     #1 implies certainty of root node succeeding

    return yhat, gamma, alpha


def find_gamma(k, yhat_queue, gamma_queue, tick):
    """ Computes gamma value and success values of non-receiver routers"""

    # Sender is not a "real" link, so no need to spend time calculating
    if(k.name == 'sender'):
        yhat_k = 1
        gamma_k = 1.0
        return yhat_k, gamma_k

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

    return yhat_k, gamma_k


def infer(k, A, gamma_queue, host_array):
    """ Calculates the actual alpha value"""

    # Sender will always be 1, so save time on calculating it out
    if(k.name == 'sender'):
        return 0.0
    
    gamma = gamma_queue[k.name]

    index = host_array.index(k)
    upstream_host = host_array[int(index/2)]

    upstream_gamma = gamma_queue[upstream_host.name]

    alpha = upstream_gamma - gamma

    

    #pre_alpha = A - gamma
    #if (len(k.downstream_nodes) > 0):

    #    A = gamma

    #    for j in k.downstream_nodes:
    #        alpha = infer(j, A, gamma_queue, host_array)
    #        return alpha

    #alpha = pre_alpha

    
    return alpha

