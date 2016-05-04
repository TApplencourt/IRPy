#!/usr/bin/env python

import irpy
from math import cos, sin

class NewtonRaphson(object):
    '''Solve cos x - x = 0 by Newton Rapshon's algorithm'''

    @irpy.lazy_property_leaves(mutables=["x"])
    def __init__(self, x):
        self.x = x

    @irpy.lazy_property
    def f(self):
        return cos(self.x) - self.x

    @irpy.lazy_property
    def fprime(self):
        return -sin(self.x) - 1

    @irpy.lazy_property
    def x_next(self):
        return self.x - self.f / self.fprime

if __name__ == '__main__':

    print NewtonRaphson.__doc__
    F = NewtonRaphson(x=1)

    print "Begin, the auto coherent resolution..."
    while abs(F.x - F.x_next) > 1.e-9:
        F.x = F.x_next

    assert (abs(F.x - 0.739085133) < 1.e-9)
    print "Success! x={0:.9f}".format(F.x)
