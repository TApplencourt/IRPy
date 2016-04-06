#!/usr/bin/python
import logging

import inspect
import sys

FRAME = [None]

def irp_ancestor(IRP_instance, EoI, visited=None):
    """
    Return the ancestor: A node reachable by repeated proceeding from child to parent.
    The parent of a node is stored in _$node_parent. 
    If the node is a Root, no parent are present.
    """
    if visited is None:
        visited = set()

    visited.add(EoI)

    try:
        s = getattr(IRP_instance, "{0}_parent".format(EoI))
    except AttributeError:
        s = set()

    for next_ in s - visited:
        irp_ancestor(IRP_instance, next_, visited)

    return visited


def get_node(IRP_instance, provider, private_node):
    """
    Provider is a function used to compute the node.
    Private_node, is private value of the node ("_node").
    Parent is the node who want to acess to this particular node.

    This function set
    """
    logging.debug("Ask for %s", private_node[1:])

    caller_name = FRAME[-1]

    FRAME.append(private_node)

    try:
        value = getattr(IRP_instance, private_node)
    except AttributeError:
        logging.debug("Provide")

        value = provider(IRP_instance)

        setattr(IRP_instance, private_node, value)
    else:
        logging.debug("Already provided")

    finally:
        #Handle the mutability
        local_parent = "{0}_parent".format(private_node)
        if caller_name:

            try:
                setattr(IRP_instance, local_parent, set([caller_name]))
            except AttributeError:
                s = getattr(IRP_instance, local_parent)
                setattr(IRP_instance, local_parent, set([caller_name]) | s)

    x = FRAME.pop()
    assert(x==private_node)
    return value


def irp_node(provider):

    str_provider = provider.__name__
    private_node = "_{0}".format(str_provider)

    def fget(self):
        return get_node(self, provider, private_node)

    def fset(self, value):
        raise AttributeError, "Immutable Node"

    return property(fget=fget, fset=fset)


def irp_node_mutable(provider):

    str_provider = provider.__name__
    private_node = "_{0}".format(str_provider)

    def fset(self, value):

        for i in irp_ancestor(self, private_node) - set([private_node]):
            delattr(self, i)
        setattr(self, private_node, value)

    def fget(self):
        return get_node(self, provider, private_node)

    return property(fget=fget, fset=fset)


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

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(relativeCreated)d ms] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    #You need to see only one "provide" in the output"
    a = Test()
    a.x = 2
    assert (a.y == 12)
    assert (a.z == 112)
    assert (a.z == 112)

#    a.y = 1

    a.x = 1
    assert (a.y == 11)
    assert (a.z == 111)
