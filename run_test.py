#!/usr/bin/env python
import irpy

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

class TestBigTree(unittest.TestCase):

    def setUp(self):
        self.f = BigTree()

    def test_dynamic(self):
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))
        self.f.b0 = set(["b0_set"])
        self.assertEqual(self.f.a0,  set(['a0', 'b0_set', 'b1']))
        self.f.c0 = set(["c0_set"])
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1','c1', 'c0_set']))

    def test_sibling(self):
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))

        #Change b0
        self.f.b0 = set(["b0_set"])

        #Now all the descendant are invalidate
        try:
            self.f.c0
        except AttributeError:
            pass

        try:
            self.f.c1
        except AttributeError:
            pass

        #We set c0
        self.f.c0 = set(["c0_set"])
        #Now here sibling (c1) are now valid
        self.assertEqual(self.f.c1, set(["c1"]))

    def test_time(self):

        import timeit

        i = timeit.timeit('f.b0;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)
        h = timeit.timeit('f.b0_hand;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)

        try:
            self.assertTrue(i < h*2.25)
        except AssertionError as e:
            raise e

if __name__ == '__main__':

    import unittest
    unittest.main()
