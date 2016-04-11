#!/usr/bin/env python

from irpy import property_irp_leaves_mutables
from irpy import property_irp
from irpy import property_irp_mutable
from irpy import property_irp_force_recompute

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


class Trivial(object):
    '''
    a = b + 1000
    b = c + 100
    c = d + 10
    d = d
    e = a 
    '''

    @property_irp_leaves_mutables("d")
    def __init__(self, d):
        self.init_d = d

    @property_irp_mutable
    def a(self):
        return self.b + 1000

    @property_irp_mutable
    def b(self):
        return self.c + 100

    @property_irp_mutable
    def c(self):
        return self.d + 10

    @property_irp
    def e(self):
        return self.a


import unittest


class TestIRP(unittest.TestCase):
    def setUp(self):
        self.f = Trivial(d=1)

    def test_dynamic(self):
        """Solve the tree"""
        self.assertEqual(self.f.a, 1111)

    def test_immutability(self):
        """Cannot change immutable Node"""
        with self.assertRaises(AttributeError):
            self.f.e = 12

    def test_mutability(self):
        """The tree have change"""
        self.f.d = 2
        self.assertEqual(self.f.a, 1112)

    def test_mutability(self):
        """The tree have change, some node are now invalid"""
        self.f.a
        self.f.a = 1113
        with self.assertRaises(AttributeError):
            self.f.d

    def test_mutability2(self):
        """The tree have change, some node are now invalid"""
        self.f.a
        self.f.a = 1113
        self.f.d = 1
        self.assertEqual(self.f.a, 1111)

    def test_force_recompute(self):
        """The tree have change, some node are now invalid"""
        self.f.a
        self.f.a = 1113
        try:
            self.f.d
        except AttributeError:
            property_irp_force_recompute(self.f,"d")
        finally:
            self.assertEqual(self.f.d, 1)
            self.assertEqual(self.f.a, 1111)

if __name__ == '__main__':
    #This overuse of logging module is require by conda bluid...
    unittest.main()

