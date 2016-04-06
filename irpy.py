#!/usr/bin/python
import logging

from collections import defaultdict
from threading import Lock

D_PATH = defaultdict(lambda: [None])
D_LOCK= defaultdict(lambda: defaultdict(lambda: Lock()))

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


def get_irp_node(IRP_instance, provider, private_node):
    """
    Provider is a function used to compute the node.
    Private_node, is private value of the node ("_node").
    Parent is the node who want to acess to this particular node.

    This function set
    """
    with D_LOCK[IRP_instance][provider]:

        logging.debug("Ask for %s", private_node[1:])
    
        caller_name = D_PATH[IRP_instance][-1]
    
        D_PATH[IRP_instance].append(private_node)
    
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
    
        assert(D_PATH[IRP_instance].pop() == private_node)
    
    return value


def irp_node(provider):

    str_provider = provider.__name__
    private_node = "_{0}".format(str_provider)

    def fget(self):
        return get_irp_node(self, provider, private_node)

    def fset(self, value):
        raise AttributeError, "Immutable Node"

    return property(fget=fget, fset=fset)


def irp_node_mutable(provider):

    str_provider = provider.__name__
    private_node = "_{0}".format(str_provider)

    def fget(self):
        return get_irp_node(self, provider, private_node)

    def fset(self, value):

        for i in irp_ancestor(self, private_node) - set([private_node]):
            with D_LOCK[self][i]:
                delattr(self, i)

        with D_LOCK[self][private_node]:
            setattr(self, private_node, value)

    return property(fget=fget, fset=fset)