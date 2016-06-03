#!/usr/bin/env python
import irpy

class BigTree(object):
    """
    a0 --> b0 --> c0 --> d0
       |      |      |
       |      |      --> d1
       |      --> c1
       --> b1
    """
    @irpy.lazy_property_leaves(immutables=["c1","d1"], mutables=["b1","d0"])
    def __init__(self):
        self.b1 = set(["b1"])
        self.c1 = set(["c1"])
        self.d1 = set(["d1"])
        self.d0 = set(["d0"])
        
    @irpy.lazy_property_mutable
    def c0(self):
        return set(["c0"]) | self.d0 | self.d1

    @irpy.lazy_property_mutable
    def b0(self):
        return set(["b0"]) | self.c0 | self.c1

    @property
    def b0_vlp(self):
        "Vanilla lazy_property"
        try:
            v = self._b0_vlp
        except AttributeError:
            v = set(["b0"]) | self.c0 | self.c1
            self._b0_vlp = v

        return v

    @irpy.lazy_property
    def a0(self):
        return set(["a0"]) | self.b0 | self.b1


import unittest

class TestBigTree(unittest.TestCase):

    def setUp(self):
        self.f = BigTree()
    
    def test_immutability(self):
        try:
            self.f.d1 = set("d1_set")
        except AttributeError:
            return True
        else:
            raise AttributeError, "This node is immutable!"

    def test_dynamic(self):
        """
        a0 --> b0 --> c0 --> d0
           |      |      |
           |      |      --> d1
           |      --> c1
           --> b1
        """
        self.assertEqual(self.f.a0,  set(['a0', 'b0', 'b1', 'c1', 'c0', 'd0', 'd1']))

        #Create a new leaf
        self.f.b0 = set(["b0_set"])
        """
        a0 --> b0_set  ||   c0 --> d0    
           |           ||      |      
           --> b1      ||      --> d1
        """
        self.assertEqual(self.f.a0,  set(['a0', 'b0_set', 'b1']))
        self.assertEqual(self.f.c0,  set(['c0', 'd0', 'd1']))

        #Check if the tree are well separated; aka no filiation relicat
        self.f.b1 = set(['b1_set'])
        self.f.d0 = set(['d0_set'])
        """
        a0 --> b0_set  ||   c0 --> d0_set
           |           ||      |      
           --> b1_set  ||      --> d1
        """
        self.assertEqual(self.f.a0,  set(['a0', 'b0_set', 'b1_set']))
        self.assertEqual(self.f.c0,  set(['c0', 'd0_set', 'd1']))

    def test_performance_cache(self):
        """Compare the naive vanilla python lazy property
                (where property is written in C in the python stdlib)
            with our IRP lazy_property with the genealogy overhead
        """
        import timeit

        i = timeit.timeit('f.b0;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)
        h = timeit.timeit('f.b0_vlp;', setup='from __main__ import BigTree; f = BigTree()', number=5000000)

        try:
            self.assertTrue(i < h*1.25)
        except AssertionError as e:
            raise e

if __name__ == '__main__':

    import unittest
    unittest.main()
