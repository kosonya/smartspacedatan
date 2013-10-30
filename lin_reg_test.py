#!/usr/bin/env python

import numpy
import matplotlib.pyplot as plt
import mdp

order = 10

def one_pol_gen(x, order = 1):
    res = []
    for i in range(1, order+1):
        if x != 0:
            res.append(x**i)
        else:
            res.append(0)
    return res

def mul_pol_gen(xs, order = 1):
    res = []
    for x in xs:
        res.append(one_pol_gen(x, order))
    return res

data = numpy.random.normal(loc = 3, scale = 2, size = 100000)

hist = numpy.histogram(data, bins = 100)

orig_xs = hist[1][:-1]
orig_ys = hist[0]

orig_pols = numpy.array(mul_pol_gen(orig_xs, order), dtype="float64")


lnode = mdp.nodes.LinearRegressionNode()
lnode.train(orig_pols, orig_ys.reshape(orig_ys.size, 1))
lnode.stop_training()

xs = numpy.array(numpy.array(mul_pol_gen([float(x)/100 for x in xrange(-1000, 1500)], order)))
ys = lnode.execute(xs)


plt.bar(orig_xs, orig_ys)
plt.plot(xs[:,0], ys, color="red")

plt.show()
