#!/usr/bin/env python

from irpy import lazy_property
from irpy import lazy_property_mutable
from irpy import lazy_property_leaves

class TrivialImmutable(object):
    '''
    a = b + 1000
    b = c + 100
    '''

    @lazy_property_leaves(immutables=["c"])
    def __init__(self, c):
        self.c = c
        self.first = True

    @lazy_property
    def a(self):
        if self.first:
            self.first = False
            return self.b + 100
        else:
            raise AttributeError

    @lazy_property
    def b(self):
        return self.c + 10


class TrivialMutable(object):
    '''
    a = b + 1000
    b = c + 100
    '''

    @lazy_property_leaves(mutables=["c"])
    def __init__(self, c):
        self.c = c

    @lazy_property_mutable
    def a(self):
        return self.b + 100

    @lazy_property_mutable
    def b(self):
        return self.c + 10

import unittest


class TestTrivial(unittest.TestCase):
    def setUp(self):
        self.f = TrivialImmutable(c=1)

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

    def test_immutability_leaf(self):
        """Any modfication on leaf is not repercuted"""
        with self.assertRaises(AttributeError):
            self.f.c = 2

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

if __name__ == '__main__':
    unittest.main()

