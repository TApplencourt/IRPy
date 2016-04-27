#!/usr/bin/env python
import irpy

class TrivialImmutable(object):
    '''
    a = b + 1000
    b = c + 100
    '''

    @irpy.lazy_property_leaves(immutables=["c"])
    def __init__(self, c):
        self.c = c
        self.first = True

    @irpy.lazy_property
    def a(self):
        if self.first:
            self.first = False
            return self.b + 100
        else:
            raise AttributeError

    @irpy.lazy_property
    def b(self):
        return self.c + 10

class BigTree(object):

    def __init__(self):
        pass

    @irpy.lazy_property
    def a0(self):
        return set(["a0"]) | self.b0 | self.b1

    @irpy.lazy_property_mutable
    def b1(self):
        return set(["b1"])

    @irpy.lazy_property_mutable
    def b0(self):
        return set(["b0"]) | self.c0 | self.c1

    @property
    def b0_hand(self):
        try:
            v = self._b0_hand
        except AttributeError:
            v = set(["b0"]) | self.c0 | self.c1
            self._b0_hand = v

        return v

    @irpy.lazy_property_mutable
    def c1(self):
        return set(["c1"])

    @irpy.lazy_property_mutable
    def c0(self):
        return set(["c0"]) | self.d0 | self.d1

    @irpy.lazy_property_mutable
    def d0(self):
        return set(["d0"])

    @irpy.lazy_property_mutable
    def d1(self):
        return set(["d1"])


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

        with self.assertRaises(AttributeError):
            self.f.c = 2



class TestBigTree(unittest.TestCase):

    def setUp(self):
        self.f = BigTree()

    def test_dynamic(self):
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))
        self.f.b0 = set(["b0_set"])
        self.assertEqual(self.f.a0,  set(['a0', 'b0_set', 'b1']))
        self.f.c0 = set(["c0_set"])
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1','c1', 'c0_set']))

    def test_out_of_tree(self):
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))
        self.f.b0 = set(["b0_set"])

        with self.assertRaises(AttributeError):
            self.f.c0

        self.f.c0 = set(["c0_set"])
        self.f.c0

    def test_time(self):

        import timeit

        h = timeit.timeit('f.b0_hand;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)
        i = timeit.timeit('f.b0;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)

        try:
            self.assertLessEqual(i, h*2.25)
        except AssertionError as e:
#            print "Overhead", i*100. / h
#            print "IRP have a to big overhead"
#            print "By Hand", h
#            print "IRP", i
            raise e

if __name__ == '__main__':

    import unittest
    unittest.main()