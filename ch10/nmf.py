from numpy import *

def difcost(a, b):
    dif = 0
    # loop over every row and column in the matrix
    for i in range(shape(a)[0]):
        for j in range(shape(a)[1]):
            # add together the differences
            dif += pow(a[i,j] - b[i,j], 2)
    return dif

def factorize(v, pc=10, iter=50):
    ic = shape(v)[0]
    fc = shape(v)[1]

    # initialize the weight and feature matrices with random values
    w = matrix([[random.random() for j in range(pc)] for i in range(ic)])
    h = matrix([[random.random() for i in range(fc)] for i in range(pc)])

    # perform operation a maximum of iter times
    for i in range(iter):
        wh = w * h
        # print 'wh-1', wh

        # calculate the current difference
        cost = difcost(v, wh)

        if i % 10 == 0: print cost

        # terminate if the matrix has been fully factorized
        if cost == 0: break

        # update the feature matrix
        tw = transpose(w)
        hn = (tw * v)
        hd = (transpose(w) * w * h) + 0.000000001

        h = matrix(array(h) * array(hn) / array(hd))

        # update weights matrix
        wn = (v * transpose(h))
        wd = (w * h * transpose(h)) + 0.000000001

        w = matrix(array(w) * array(wn) / array(wd))

    return w, h





