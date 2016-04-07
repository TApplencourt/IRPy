#!/usr/bin/env python

from irpy import irp_node
from irpy import irp_node_mutable
from irpy import irp_leaves_mutables

import logging


def loggin_debug():

    logger = logging.getLogger()
    handler = logging.StreamHandler()

    str_ = '[%(relativeCreated)d ms] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    formatter = logging.Formatter(str_)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

def loggin_unset():
    import logging

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.CRITICAL)

class NotTrivialFunction(object):
    '''
    Compute : t(u(d1,d2),v(d3,d4),w(d5))
    where:
        t(x,y) = x + y + 4
        u(x,y) = x + y + 1
        v(x,y) = x + y + 2
        w(x)   = x + 3
    and d1, d2, d3, d3, d5 are the parameters
    '''

    @irp_leaves_mutables("d1")
    def __init__(self, d1, d2, d3, d4, d5):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    @irp_node
    def t(self):
        return self.u1 + self.v + 4

    @irp_node
    def u1(self):
        return self.fu(self.d1, self.d2)

    @irp_node
    def v(self):
        return self.u2 + self.w + 2

    @irp_node
    def u2(self):
        return self.fu(self.d3, self.d4)

    @irp_node
    def w(self):
        return self.d5 + 3

    def fu(self, x, y):
        return x + y + 1

from math import cos, sin

class NewtonRaphson(object):
    '''
    Solve cos x - x = 0 by Newton Rapshon's algorithm
    '''

    @irp_leaves_mutables("x")
    def __init__(self,x):
        self.x = x        

    @irp_node_mutable
    def f(self):
        return cos(self.x) - self.x

    @irp_node_mutable
    def fprime(self):
        return -sin(self.x) - 1

    @irp_node_mutable
    def x_next(self):
        return self.x - self.f / self.fprime

    def solve(self):

        while abs(self.x - self.x_next) > 1.e-9:
            self.x = self.x_next

if __name__ == '__main__':

    print NotTrivialFunction.__doc__
    loggin_debug()
    
    print 'Show the dynamic resolution of node'
    F = NotTrivialFunction(1, 5, 8, 10, 7)
    assert (F.t == 42)
    print 'Show the lazy evaluation'
    assert (F.t == 42)

    print 'Show the coherence and mutability'
    F.d1 = 2
    assert (F.t == 43)

    print NewtonRaphson.__doc__
    loggin_unset()

    F=NewtonRaphson(x=1)
    F.solve()
    assert (abs(F.x -0.739085133) < 1.e-9)
    print "Success! x={0:.9f}".format(F.x)
