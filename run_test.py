#!/usr/bin/env python

from irpy import property_irp_leaves_mutables
from irpy import property_irp
from irpy import property_irp_mutable
from irpy import property_irp_force_recompute

class Trivial(object):
    '''
    a = b + 1000
    b = c + 100
    '''

    def __init__(self, c):
        self.c = c
        self.first = True

    @property_irp
    def a(self):
        if self.first:
            self.first = False
            return self.b + 100
        else:
            raise AttributeError

    @property_irp
    def b(self):
        return self.c + 10


class TrivialMutable(object):
    '''
    a = b + 1000
    b = c + 100
    '''

    @property_irp_leaves_mutables("c")
    def __init__(self, c):
        self.c = c

    @property_irp_mutable
    def a(self):
        return self.b + 100

    @property_irp_mutable
    def b(self):
        return self.c + 10

import unittest


class TestTrivial(unittest.TestCase):
    def setUp(self):
        self.f = Trivial(c=1)

    def test_dynamic(self):
        """Solve the tree"""
        self.assertEqual(self.f.a, 111)

    def test_cache(self):
        """Cache"""
        self.assertEqual(self.f.a, 111)
        self.assertEqual(self.f.a, 111)

    def test_immutability(self):
        """Cannot change immutable Node"""
        with self.assertRaises(AttributeError):
            self.f.b = 12

    def test_warning_immutability_leaf(self):
        """Any modfication on leaf is not repercuted"""
        self.assertEqual(self.f.a, 111)
        self.c = 12
        self.assertEqual(self.f.a, 111)


class TestTrivialMutable(unittest.TestCase):
    def setUp(self):
        self.f = TrivialMutable(c=1)

    def test_dynamic(self):
        """Solve the tree"""
        self.assertEqual(self.f.a, 111)
        self.f.b = 12
        self.assertEqual(self.f.a, 112)

    def test_incoherence(self):
        """Incoherence"""
        self.assertEqual(self.f.a, 111)

        self.f.a = 112
        self.assertEqual(self.f.a, 112)
        
        with self.assertRaises(AttributeError):
            self.f.b

    def test_forcerecompute(self):
        
        self.assertEqual(self.f.a, 111)

        self.f.a = 112

        property_irp_force_recompute(self.f,"c")
        self.assertEqual(self.f.a, 111)


if __name__ == '__main__':
    #This overuse of logging module is require by conda bluid...
    unittest.main()

