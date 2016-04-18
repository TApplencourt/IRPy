#!/usr/bin/python
from collections import defaultdict
from irp_node import set_node_value, get_node

#  _                              
# | \  _   _  _  ._ _. _|_  _  ._ 
# |_/ (/_ (_ (_) | (_|  |_ (_) |  
#
class lazy_property(object):
    """
    My little Property
    My little Property
    My little Property...  friend
    """

    #Handle the instance variable.
    #We need a global dict, cause property are created when the class is imported
    #not when it is execuded

    d_is_set = defaultdict(lambda: defaultdict(lambda: False))

    def __init__(self, provider, leaf_node=None, immutability=True):
        """Provider: If a function who will be used to compute the node
           leaf_node: If the name of the node
           immutability: If immutability is set you cannot set the node"""

        self.provider = provider

        if not leaf_node:
            self.node = provider.__name__
            self.leaf = False
        else:
            self.node = leaf_node
            self.leaf = True

        self.pri_node = "_{0}".format(self.node)
        self.immutability = immutability

    def init_obj_attr(self, obj):
        """Initiate some useful private value
           Do this only once"""

        if not lazy_property.d_is_set[obj][self.node]:
            d = {
                "_{0}_children": set(),
                "_{0}_parents": set(),
                "_{0}_uncoherent": set()
            }

            for attr, value in d.items():
                setattr(obj, attr.format(self.node), value)

            lazy_property.d_is_set[obj][self.node] = True

    def __get__(self, obj, objtype):
        "Get the value of the node"
        self.init_obj_attr(obj)

        return get_node(obj, self.pri_node, self.provider)

    def __set__(self, obj, value):
        """Set the value of the node
        But wait, leaves are "gradual typed" variable! Youpi!
        Idea borrowed from the-worst-programming-language-ever (http://bit.ly/13tc6XW)
        """
        self.init_obj_attr(obj)

        if self.immutability:
            if self.leaf:
                self.leaf = False
            else:
                raise AttributeError, "Immutable Node {0}".format(self.pri_node)

        set_node_value(lazy_obj=obj, pri_node=self.pri_node, value=value)

def lazy_property_mutable(provider):
    "Return a lazy_property with false set to False"
    return lazy_property(provider=provider, immutability=False)


def lazy_property_leaves(mutables=[], immutables=[]):
    "Set to properties for the __init__ method"

    def leaf_decorator(func):
        def func_wrapper(self, *args, **kwargs):

            for node in set(immutables) | set(mutables):

                def provider(self):
                    return getattr(self, "_%s" % node)

                p = lazy_property(provider=provider,
                                  leaf_node=node,
                                  immutability=node in immutables)
                #If this ugly? Yeah... Is this an issue? I don't really know
                setattr(self.__class__, node, p)

            return func(self, *args, **kwargs)

        return func_wrapper

    return leaf_decorator
