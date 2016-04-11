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

def loggin_info():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

class Trivial(object):
    '''Solve cos x - x = 0 by Newton Rapshon's algorithm'''

    @irp_leaves_mutables("d")
    def __init__(self,d):
        self.d = d        

    @irp_node_mutable
    def c(self):
        return self.d+10

    @irp_node_mutable
    def b(self):
        return self.c+100

    @irp_node_mutable
    def a(self):
        return self.b+1000

class NotTrivialFunction(object):
    '''Compute : t(u(d1,d2),v(d3,d4),w(d5))
    where:
        t(x,y) = x + y + 4
        u(x,y) = x + y + 1
        v(x,y) = x + y + 2
        w(x)   = x + 3
    and d1, d2, d3, d3, d5 are the parameters'''

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

    @irp_node_mutable
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
    '''Solve cos x - x = 0 by Newton Rapshon's algorithm'''

    @irp_leaves_mutables("x")
    def __init__(self,x):
        self.x = x        

    @irp_node
    def f(self):
        return cos(self.x) - self.x

    @irp_node
    def fprime(self):
        return -sin(self.x) - 1

    @irp_node
    def x_next(self):
        return self.x - self.f / self.fprime

    def solve(self):

        while abs(self.x - self.x_next) > 1.e-9:
            self.x = self.x_next

if __name__ == '__main__':
    #This overuse of logging module is require by conda bluid...

    loggin_debug()

    F = Trivial(d=1)
    print F.a

    F.b = 9
    print F.a
 #
    F.d = 1
    print F.a
#
#    logging.info(NotTrivialFunction.__doc__)
#
#    logging.info('Show the dynamic resolution of node')
#    F = NotTrivialFunction(1, 5, 8, 10, 7)
#    assert (F.t == 42)
#    logging.info('Show the lazy evaluation')
#    assert (F.t == 42)
#
#    logging.info('Show the coherence and mutability')

#    loggin_info()
#    logging.info(NewtonRaphson.__doc__)
#    F=NewtonRaphson(x=1)
#
#    F.solve()
#    assert (abs(F.x -0.739085133) < 1.e-9)
#    logging.info("Success! x={0:.9f}".format(F.x))
