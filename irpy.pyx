#!/usr/bin/python

#Handle the execution stack
from collections import defaultdict
d_path = defaultdict(lambda: [None])
d_last_caller = defaultdict(lambda: None)


def genealogy(obj, _node, direction, inclusif=False):
    """Return the genealogy of a _node.
       Direction is $parents or $children, recurse accordingly"""

    def sap(_node, direction, visited=None):
        if visited is None:
            visited = set()

        visited.add(_node)
        try:
            s = getattr(obj, "{0}_{1}".format(_node, direction))
        except AttributeError:
            s = set()

        for next_ in s - visited:
            sap(next_, direction, visited)

        return visited - set([None])

    s = sap(_node, direction)
    if not inclusif:
        s = s - set([_node])

    return s


def addattr(obj, name, value):
    try:
        s = getattr(obj, name)
    except AttributeError:
        setattr(obj, name, set([value]))
    else:
        setattr(obj, name, s | set([value]))


def removeattr(obj, name, value):
    try:
        s = getattr(obj, name)
    except AttributeError:
        pass
    else:
        setattr(obj, name, s - set([value]))


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

    def __init__(self, provider, init_node=False, immutable=True):
        """Provider: If a function who will be used to compute the node
           init_node: If the name of the node
           immutable: If immutable is set you cannot set the node"""

        self.provider = provider
        self.init_node = init_node
        self.immutable = immutable

        if not self.init_node:
            name = provider.__name__
        else:
            name = self.init_node

        #Kind of human readable identifier
        self._node = "_%s_%s" % (name, id(provider))

    def __get__(self, obj, objtype):
        "Get the value of the node and handle the genealogy"

        _caller = d_path[obj][-1]
        _node = self._node

        if _caller != d_last_caller[obj]:
            addattr(obj, "%s_parents" % _node, _caller)
            addattr(obj, "%s_children" % _caller, _node)
            d_last_caller[obj] = _caller

        #Wanted: value. Cached or Computed
        try:
            value = getattr(obj, _node)
        except AttributeError:

            d_path[obj].append(_node)

            value = self.provider(obj)
            setattr(obj, _node, value)

            d_path[obj].pop()

        return value

    def __set__(self, obj, value):
        """Set the value of the node
        But wait, init_node are "gradual typed" variable! Youpi!
        Idea borrowed from the-worst-programming-language-ever (http://bit.ly/13tc6XW)
        """

        _node = self._node

        if not self.init_node:

            if self.immutable:
                raise AttributeError, "Immutable Node {0}".format(self._node)

            #Set the new value
            setattr(obj, _node, value)

            #Node ancestor need to be recompute is asked
            for _parent in genealogy(obj, _node, "parents"):
                if hasattr(obj, _parent): delattr(obj, _parent)

            #Node abandons his children
            for _child in getattr(obj, "%s_children" % _node):
                removeattr(obj, "%s_parents" % _child, _node)

            #Indeed node is now a leaf
            setattr(obj, "%s_children" % _node, set())

        else:
            setattr(obj, "%s_parents" % _node, set())
            setattr(obj, "%s_children" % _node, set())
            setattr(obj, _node, value)

            self.init_node = False


def lazy_property_mutable(provider):
    "Return a lazy_property mutable"
    return lazy_property(provider=provider, immutable=False)


def lazy_property_leaves(mutables=(), immutables=()):
    "Set to properties for the __init__ method"

    def leaf_decorator(func):
        def func_wrapper(self, *args, **kwargs):

            for node in set(immutables) | set(mutables):

                def provider(self):
                    return getattr(self, "_%s" % node)

                p = lazy_property(provider=provider,
                                  init_node=node,
                                  immutable=node in immutables)

                #If this ugly? Yeah... Is this an issue? I don't really know
                setattr(self.__class__, node, p)

            return func(self, *args, **kwargs)

        return func_wrapper

    return leaf_decorator
