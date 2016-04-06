#!/usr/bin/env python

from irpy import irp_node
from irpy import irp_node_mutable

class Test(object):
    def __init__(self):
        pass

    @irp_node_mutable
    def x(self):
        return self.x

    @irp_node
    def y(self):
        return self.x + 10

    @irp_node
    def z(self):
        return self.y + 100


if __name__ == '__main__':

    import logging
    
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(relativeCreated)d ms] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    a = Test()
    a.x = 2
    assert (a.y == 12)
    assert (a.z == 112)
    assert (a.z == 112)

    a.x = 1
    assert (a.y == 11)
    assert (a.z == 111)
