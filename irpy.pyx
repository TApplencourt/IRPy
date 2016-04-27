#!/usr/bin/python
from collections import defaultdict

#Handle your execution stack
#Handle the instance variable.
#We need a global dict, cause property are created when the class is imported
#not when it is execuded
d_path = defaultdict(lambda: [None])
d_last_caller = defaultdict(lambda: None)


def appendattr(obj, name, value):
    try:
        s = getattr(obj, name)
    except AttributeError:
        setattr(obj, name, set([value]))
    else:
        setattr(obj, name, set([value]) | s)


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

    def __init__(self, provider, leaf_node=None, immutability=True):
        """Provider: If a function who will be used to compute the node
           leaf_node: If the name of the node
           immutability: If immutability is set you cannot set the node"""

        self.provider = provider
        self.leaf_node = leaf_node

        if not self.leaf_node:
            self.node = provider.__name__
        else:
            self.node = self.leaf_node

        self.pri_node = "_{0}".format(self.node)
        self.parents = "_{0}_parents".format(self.node)
        self.children = "_{0}_children".format(self.node)
        self.uncoherent = "_{0}_uncoherent".format(self.node)

        self.immutability = immutability

    def __get__(self, obj, objtype):
        "Get the value of the node"
        caller = d_path[obj][-1]
        pri_node = self.pri_node

        "Handle The Genealogy"
        if caller != d_last_caller[obj]:
            appendattr(obj, self.parents, caller)
            appendattr(obj, "{0}_children".format(caller), pri_node)
            d_last_caller[obj] = caller

        "Get the value"
        try:
            value = getattr(obj, pri_node)
        except AttributeError:

            try:
                getattr(obj, self.uncoherent)
            except AttributeError:
                pass
            else:
                raise AttributeError, "Node is incoherent {0}".format(pri_node)

            d_path[obj].append(pri_node)

            value = self.provider(obj)
            setattr(obj, pri_node, value)

            d_path[obj].pop()

        return value

    def __set__(self, obj, value):
        """Set the value of the node
        But wait, leaves are "gradual typed" variable! Youpi!
        Idea borrowed from the-worst-programming-language-ever (http://bit.ly/13tc6XW)
        """

        if self.immutability:
            if self.leaf_node:
                self.leaf_node = False
            else:
                raise AttributeError, "Immutable Node {0}".format(self.pri_node)

        set_node_value(obj=obj, pri_node=self.pri_node, value=value)


def lazy_property_mutable(provider):
    "Return a lazy_property mutable"
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


# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
#Satisfaction
def set_node_value(obj, pri_node, value):
    def irp_sap(pri_node, direction, visited=None):
        """
        Direction is $parents or $children, recurse accordingly
        """
        if visited is None:
            visited = set()

        visited.add(pri_node)
        try:
            s = getattr(obj, "{0}_{1}".format(pri_node, direction))
        except AttributeError:
            s = set()

        for next_ in s - visited:
            irp_sap(next_, direction, visited)

        return visited - set([None])

    def irp_remove_ancestor_cache():
        l_ancestor = irp_sap(pri_node, "parents") - set([pri_node])

        for parent in l_ancestor:
            try:
                delattr(obj, parent)
            except AttributeError:
                pass

    def irp_set_uncoherent_descendant():
        #Now handle the mutability
        l_descendant = irp_sap(pri_node, "children") - set([pri_node])

        for child in l_descendant:
            appendattr(obj, "{0}_uncoherent".format(child), pri_node)
            try:
                delattr(obj, child)
            except AttributeError:
                pass

    def irp_unset_siblings():

        try:
            l_uncoherent = getattr(obj, "{0}_uncoherent".format(pri_node))
        except AttributeError:
            pass
        else:
            visited = set()
            for sibling in l_uncoherent:
                for descendant in irp_sap(sibling, "children") - visited:

                    name = "{0}_uncoherent".format(descendant)

                    try:
                        s = getattr(obj, name) - set([sibling])
                    except AttributeError:
                        pass
                    else:
                        if not s:
                            delattr(obj, name)
                        else:
                            setattr(obj, name, s)

                    visited.add(descendant)

    try:
        cur_value = getattr(obj, pri_node)
    except AttributeError:
        cur_value = None
    finally:
        if cur_value != value:
            setattr(obj, pri_node, value)
            irp_remove_ancestor_cache()
            irp_set_uncoherent_descendant()
            irp_unset_siblings()
