#!/usr/bin/python
import logging

from collections import defaultdict
from threading import Lock

#Handle your execution stack
D_PATH = defaultdict(lambda: [None])
#Handle the instance variable
D_ONLY_ONCE = defaultdict(lambda: defaultdict(lambda: False))
#Handle your lock stack
D_LOCK = defaultdict(lambda: defaultdict(lambda: Lock()))


def appendattr(object, name, value):
    s = getattr(object, name)
    setattr(object, name, set([value]) | s)


#  _                                            
# |_ _  | |  _         _|_ |_   _     _  _. ._  
# | (_) | | (_) \/\/    |_ | | (/_   _> (_| |_) 
#                                           |
def irp_sap(lazy_obj, pri_node, direction, visited=None):
    """
    Direction is $parents or $children, recurse accordingly
    """
    if visited is None:
        visited = set()

    visited.add(pri_node)

    s = getattr(lazy_obj, "{0}_{1}".format(pri_node, direction))

    for next_ in s - visited:
        irp_sap(lazy_obj, next_, direction, visited)

    return visited


def irp_ancestor(lazy_obj, pri_node):
    """
    Return the ancestor: A pri_node reachable by repeated proceeding from child to parent.
    The parent of a pri_node is stored in _$pri_node_parent. 
    """
    return irp_sap(lazy_obj, pri_node, "parents") - set([pri_node])


def irp_descendant(lazy_obj, pri_node):
    """
    Return the descendant: A pri_node reachable by repeated proceeding from parent to child.
    The parent of a pri_node is stored in _$pri_node_child. 
    """
    return irp_sap(lazy_obj, pri_node, "children") - set([pri_node])


# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
#Satisfaction
def get_irp_node(lazy_obj, pri_node, provider):
    """
    'provider' is a function used to compute the node.
    'pri_node', is the private value of the node ("_node").
    'lazy_obj' is an instance of the class who use IRPy.

        First, this function return the 'pri_node' value,
               if it not existing yet, we will set it.

        Secondly, We handle your own stack of function execution
               in order to add into ${pri_node}_parent all
               the caller.
        Finally, we return the value of the node.
    This function is (maybe) trade safe.
    """

    logging.debug("Ask for %s", pri_node)
    with D_LOCK[lazy_obj][pri_node]:

        #~=~=~
        #Handle the  execution stack
        #~=~=~
        caller_name = D_PATH[lazy_obj][-1]
        D_PATH[lazy_obj].append(pri_node)

        if not getattr(lazy_obj, "%s_coherent" % pri_node):
            raise AttributeError, "Node is incoherent {0}".format(pri_node)

        #~=~=~
        #Get and set the value node
        #~=~=~

        try:
            value = getattr(lazy_obj, pri_node)
        except AttributeError:
            logging.debug("Provide")

            value = provider(lazy_obj)
            setattr(lazy_obj, pri_node, value)
        else:
            logging.debug("Already provided")

        #~=~=~
        #Handle the mutability
        #~=~=~

        if caller_name:

            #Set parent
            local_parent = "{0}_parents".format(pri_node)
            appendattr(lazy_obj, local_parent, caller_name)

            #Set children
            local_child = "{0}_children".format(caller_name)
            appendattr(lazy_obj, local_child, pri_node)

    return value


def set_irp_node(lazy_obj, pri_node, value):
    """
    'pri_node', is the private value of the node ("_node").
    'parent' is the node who want to access to this particular node.
    'value' is the value of the node who want to set.

    First we remove all the private variable of the node who use this 
        particular node. Then we set the new value

    This function is (maybe) trade safe.  
    """

    logging.debug("Set node %s", pri_node)
    with D_LOCK[lazy_obj][pri_node]:
        setattr(lazy_obj, pri_node, value)

    #Now handle the mutability
    l_ancestor = irp_ancestor(lazy_obj, pri_node)
    l_descendant = irp_descendant(lazy_obj, pri_node)

    logging.debug("Unset parents: %s", l_ancestor)
    for parent in l_ancestor:

        with D_LOCK[lazy_obj][parent]:
            #Maybe somebody already delete this private node
            try:
                delattr(lazy_obj, parent)
            except AttributeError:
                pass

    logging.debug("Set descendant coherence to False: %s", l_descendant)
    for child in l_descendant:
        with D_LOCK[lazy_obj][child]:
            setattr(lazy_obj, "{0}_coherent".format(child), False)

    logging.debug("Set ancestor coherence to True: %s", l_ancestor)
    for parent in l_ancestor | set([pri_node]):
        with D_LOCK[lazy_obj][parent]:
            setattr(lazy_obj, "{0}_coherent".format(parent), True)


#  _                              
# | \  _   _  _  ._ _. _|_  _  ._ 
# |_/ (/_ (_ (_) | (_|  |_ (_) |  
#
class lazy_property(object):
    """
    My little Property
    My little Property
    My little Property...  friend

    Provider: If a function who will be used to compute the node
    node: If the name of the node
    Immutability: If immutability is set you cannot set the node
    """

    def __init__(self, provider, node=None, immutability=True):

        self.provider = provider

        if not node:
            self.node = provider.__name__
            self.leaf = False
        else:
            self.node = node
            self.leaf = True

        self.pri_node = "_{0}".format(self.node)
        self.immutability = immutability

    def set_obj_attr(self, obj):
        "Initiate some useful private value"
        "Do this only once"
        if not D_ONLY_ONCE[obj][self.node]:

            d = {
                "_{0}_children": set(),
                "_{0}_parents": set(),
                "_{0}_coherent": True
            }

            for attr, value in d.items():
                setattr(obj, attr.format(self.node), value)

            D_ONLY_ONCE[obj][self.node] = True

    def __get__(self, obj, objtype):
        "Get the value of the node"
        self.set_obj_attr(obj)
        return get_irp_node(obj, self.pri_node, self.provider)

    def __set__(self, obj, value):
        """Set the value of the node
        But wait, leaves are "gradual typed" variable! Youpi!
        Idea borrowed from the-worst-programming-language-ever (http://bit.ly/13tc6XW)
        """

        self.set_obj_attr(obj)

        if self.leaf and self.immutability:
            set_irp_node(obj, self.pri_node, value)
            self.leaf = False
        elif self.immutability:
            raise AttributeError, "Immutable Node {0}".format(self.pri_node)
        else:
            set_irp_node(obj, self.pri_node, value)


def lazy_property_mutable(provider):
    """
    Return a lazy_property with false set to False
    """
    return lazy_property(provider=provider, immutability=False)


def lazy_property_leaves(mutables=[], immutables=[]):
    """This a named decorator"""

    def leaf_decorator(func):
        def func_wrapper(self, *args, **kwargs):

            for node in set(immutables) | set(mutables):

                def provider(self):
                    return getattr(self, "_%s" % node)

                p = lazy_property(provider=provider,
                                  node=node,
                                  immutability=node in immutables)
                #If this ugly? Yeah... Is this an issue? I don't really know
                setattr(self.__class__, node, p)

            return func(self, *args, **kwargs)

        return func_wrapper

    return leaf_decorator
