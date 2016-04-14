#!/usr/bin/env python

from irpy import lazy_property
from irpy import lazy_property_mutable
from irpy import lazy_property_leaves

import logging


def loggin_debug():

    logger = logging.getLogger()

    if not logger.handlers:
        handler = logging.StreamHandler()

        str_ = '[%(relativeCreated)d ms] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
        formatter = logging.Formatter(str_)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)


def loggin_info():
    logger = logging.getLogger()

    if not logger.handlers:
        handler = logging.StreamHandler()

        str_ = '[%(relativeCreated)d ms] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
        formatter = logging.Formatter(str_)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)


class NotTrivialFunction(object):
    '''Compute : t(u(d1,d2),v(d3,d4),w(d5))
    where:
        t(x,y) = x + y + 4
        u(x,y) = x + y + 1
        v(x,y) = x + y + 2
        w(x)   = x + 3
    and d1, d2, d3, d3, d5 are the parameters'''

    @lazy_property_leaves(mutables=["d1"],
                          immutables="d2 d3 d4 d5".split())
    def __init__(self, d1, d2, d3, d4, d5):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    @lazy_property
    def t(self):
        return self.u1 + self.v + 4

    @lazy_property
    def u1(self):
        return self.fu(self.d1, self.d2)

    @lazy_property
    def v(self):
        return self.u2 + self.w + 2

    @lazy_property
    def u2(self):
        return self.fu(self.d3, self.d4)

    @lazy_property
    def w(self):
        return self.d5 + 3

    def fu(self, x, y):
        return x + y + 1


from math import cos, sin


class NewtonRaphson(object):
    '''Solve cos x - x = 0 by Newton Rapshon's algorithm'''

    @lazy_property_leaves(mutables=["x"])
    def __init__(self, x):
        self.x = x

    @lazy_property
    def f(self):
        return cos(self.x) - self.x

    @lazy_property
    def fprime(self):
        return -sin(self.x) - 1

    @lazy_property
    def x_next(self):
        return self.x - self.f / self.fprime

    def solve(self):

        while abs(self.x - self.x_next) > 1.e-9:
            self.x = self.x_next


if __name__ == '__main__':

    #This overuse of logging module is require by conda bluid...

    loggin_debug()

    logging.info(NotTrivialFunction.__doc__)

    logging.info('Show the dynamic resolution of node')
    F = NotTrivialFunction(1, 5, 8, 10, 7)
    assert (F.t == 42)
    logging.info('Show the lazy evaluation')
    assert (F.t == 42)

    logging.info('Show the coherence and mutability')

    loggin_info()
    logging.info(NewtonRaphson.__doc__)
    F = NewtonRaphson(x=1)

    F.solve()
    assert (abs(F.x - 0.739085133) < 1.e-9)
    logging.info("Success! x={0:.9f}".format(F.x))
