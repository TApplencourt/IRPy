#!/usr/bin/env python
import irpy 

class BigTree(object):

    def __init__(self):
        pass

    @irpy.lazy_property
    def a0(self):
        return set(["a0"]) | self.b0 | self.b1

    @property
    def a0_hand(self):
        try:
            v = self._a0_hand
        except AttributeError:
            v = set(["a0"]) | self.b0 | self.b1
            self._a0_hand = v

        return v

    @irpy.lazy_property_mutable
    def b1(self):
        return set(["b1"])

    @irpy.lazy_property_mutable
    def b0(self):
        return set(["b0"]) | self.c0 | self.c1

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

#    def test_dynamic(self):
#        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))
#        self.f.b0 = set(["b0_set"])
#        self.assertEqual(self.f.a0,  set(['a0', 'b0_set', 'b1']))
#        self.f.c0 = set(["c0_set"])
#        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1','c1', 'c0_set']))

#    def test_out_of_tree(self):
#        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))
#        self.f.b0 = set(["b0_set"])
#
#        with self.assertRaises(AttributeError):
#            self.f.c0
#
#        self.f.c0 = set(["c0_set"])
#        self.f.c0

if __name__ == '__main__':

    print "============"
    import timeit
    print "By Hand",
    h = timeit.timeit('f.a0_hand;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)
    print h
    print "With IRPY (Cython)",
    i = timeit.timeit('f.a0;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)
    print i

    print "Overhead"
    print i*100. / h
    
    import unittest
    unittest.main()