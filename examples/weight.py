#!/usr/bin/env python
import irpy
class WeightFactory(object):
    '''Compute the weight of a rectangle'''

    @irpy.lazy_property_leaves(immutables="l w h".split())
    def __init__(self, l, w, h):
        '''Dimension of the box (m)'''
        self.l = l
        self.w = w
        self.h = h

    @irpy.lazy_property_mutable
    def volume(self):
        " V = l * w * h"
        return self.l * self.w * self.h 

    @irpy.lazy_property_mutable
    def density(self):
        "Volumetric mass density of Iron (kg/m^3)"
        return 7.87 * 10**3

    @irpy.lazy_property_mutable
    def mass(self):
        "m = V * d"
        return self.volume * self.density

    @irpy.lazy_property_mutable
    def g(self):
        "g-force (m/s2) in equator"
        return 9.7803

    @irpy.lazy_property_mutable
    def weight(self):
        "In Newton"
        return self.mass*self.g

if __name__ == '__main__':

    print WeightFactory.__doc__
    print "Rectangle dimension 1x1x1 "
    f = WeightFactory(1,1,1)
    assert ( abs(f.weight - 76970.961) < 1.e-4)
    print "Weight: {0} Newton".format(f.weight)

    print "We are now on the  moon (change the acceleration gravity accordingly)"
    f.g = 1.622
    assert ( abs(f.weight - 12765.14) < 1.e-4)
    print "Weight: {0} Newton".format(f.weight)

    print "Change iron to water"
    f.density = 1.000
    assert ( abs(f.weight - 1.622) < 1.e-4)
    print "Weight: {0} Newton".format(f.weight)
