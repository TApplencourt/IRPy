#!/usr/bin/python
import logging

from collections import defaultdict
from threading import Lock

#Handle your execution stack
D_PATH = defaultdict(lambda: [None])
#Handle the instance variable
D_INIT = defaultdict(lambda: defaultdict(lambda: False))
#Handle your lock stack
D_LOCK = defaultdict(lambda: defaultdict(lambda: Lock()))


def appendattr(object,name,value):
    s = getattr(object, name)
    setattr(object, name, set([value]) | s)

#  _                                            
# |_ _  | |  _         _|_ |_   _     _  _. ._  
# | (_) | | (_) \/\/    |_ | | (/_   _> (_| |_) 
#                                           |
def irp_sap(IRP_instance, node, direction, visited=None):
    """
    Direction is $parents or $children, recurse accordingly
    """
    if visited is None:
        visited = set()

    visited.add(node)

    s = getattr(IRP_instance, "{0}_{1}".format(node, direction))

    for next_ in s - visited:
        irp_sap(IRP_instance, next_, direction, visited)

    return visited


def irp_ancestor(IRP_instance, node):
    """
    Return the ancestor: A node reachable by repeated proceeding from child to parent.
    The parent of a node is stored in _$node_parent. 
    """
    return irp_sap(IRP_instance, node, "parents") - set([node])


def irp_descendant(IRP_instance, node):
    """
    Return the descendant: A node reachable by repeated proceeding from parent to child.
    The parent of a node is stored in _$node_child. 
    """
    return irp_sap(IRP_instance, node, "children") - set([node])


# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
#Satisfaction
def get_irp_node(IRP_instance, provider, pri_node):
    """
    'provider' is a function used to compute the node.
    'pri_node', is the private value of the node ("_node").
    'IRP_instance' is an instance of the class who use IRPy.

        First, this function return the 'pri_node' value,
               if it not existing yet, we will set it.

        Secondly, We handle your own stack of function execution
               in order to add into ${pri_node}_parent all
               the caller.
        Finally, we restun the value of the node.
    This function is (maybe) trade safe.
    """

    logging.debug("Ask for %s", pri_node)
    with D_LOCK[IRP_instance][pri_node]:

        #~=~=~
        #Handle the  execution stack
        #~=~=~
        caller_name = D_PATH[IRP_instance][-1]
        D_PATH[IRP_instance].append(pri_node)

        if not getattr(IRP_instance, "%s_coherent" % pri_node):
            raise AttributeError, "Node is incoherent {0}".format(pri_node)

        #~=~=~
        #Get and set the value node
        #~=~=~

        try:
            value = getattr(IRP_instance, pri_node)
        except AttributeError:
            logging.debug("Provide")

            value = provider(IRP_instance)
            setattr(IRP_instance, pri_node, value)
        else:
            logging.debug("Already provided")

        #~=~=~
        #Handle the mutability
        #~=~=~

        if caller_name:

            #Set parent
            local_parent = "{0}_parents".format(pri_node)
            appendattr(IRP_instance,local_parent,caller_name)

            #Set children
            local_child = "{0}_children".format(caller_name)
            appendattr(IRP_instance,local_child,pri_node)

    return value


def set_irp_node(IRP_instance, provider, pri_node, value):
    """
    'provider' is a function used to compute the node.
    'pri_node', is the private value of the node ("_node").
    'parent' is the node who want to access to this particular node.
    'value' is the value of the node who want to set.

    First we remove all the private variable of the node who use this 
        particular node. Then we set the new value

    This function is (maybe) trade safe.  
    """

    logging.debug("Set node %s", pri_node)
    with D_LOCK[IRP_instance][pri_node]:
        setattr(IRP_instance, pri_node, value)

    l_ancestor = irp_ancestor(IRP_instance, pri_node)
    l_descendant = irp_descendant(IRP_instance, pri_node)

    logging.debug("Unset parents: %s", l_ancestor)
    for i in l_ancestor:
        with D_LOCK[IRP_instance][i]:
            delattr(IRP_instance, i)

    logging.debug("Set ancestor coherence to True: %s", l_ancestor)
    for i in l_ancestor | set([pri_node]):
        with D_LOCK[IRP_instance][i]:
            setattr(IRP_instance, "{0}_coherent".format(i), True)

    logging.debug("Set descendant coherence to False: %s", l_descendant)
    for i in l_descendant:
        with D_LOCK[IRP_instance][i]:
            setattr(IRP_instance, "{0}_coherent".format(i), False)


#  _                              
# | \  _   _  _  ._ _. _|_  _  ._ 
# |_/ (/_ (_ (_) | (_|  |_ (_) |  
#
class property_irp(object):
    """
    My little Property
    My little Property
    My little Property...  friend

    Provider: If a function who will be used to compute the node
    Str_provider: If the name of the node
    Immutability: If immutability is set you cannot set the node
    """

    def __init__(self, provider, str_provider=None, immutability=True):

        self.provider = provider
        self.str_provider = str_provider if str_provider else provider.__name__

        self.pri_node = "_{0}".format(self.str_provider)
        self.immutability = immutability

    def set_obj_attr(self, obj):

        #For each instance of the provider initiante somme ussfull values
        if not D_INIT[obj][self.str_provider]:

            d = {
                "_{0}_children": set(),
                "_{0}_parents": set(),
                "_{0}_coherent": True
            }

            for attr, value in d.items():
                setattr(obj, attr.format(self.str_provider), value)

            D_INIT[obj][self.str_provider] = True

    def __get__(self, obj, objtype):
        "Get the value of the node"
        self.set_obj_attr(obj)

        return get_irp_node(obj, self.provider, self.pri_node)

    def __set__(self, obj, value):
        "Set the value of the node"
        self.set_obj_attr(obj)

        if self.immutability:
            raise AttributeError, "Immutable Node {0}".format(self.pri_node)
        else:
            set_irp_node(obj, self.provider, self.pri_node, value)


def property_irp_mutable(provider):
    """
    Return a property_irp with false set to False
    """
    return property_irp(provider=provider, immutability=False)


def property_irp_leaves_mutables(*irp_leaf):
    "This a named decorator"
    'For all the node in irp_leaf we create the property associated'

    'We set the new property and the we execute the function'

    def leaf_decorator(func):
        def func_wrapper(self, *args, **kwargs):

            for str_provider in irp_leaf:

                def provider(self):
                    return getattr(self, self.pri_node)

                p = property_irp(provider=provider,
                                 str_provider=str_provider,
                                 immutability=False)
                #If this ugly? Yeah... Is this an issue? I don't realy know
                setattr(self.__class__, str_provider, p)

            return func(self, *args, **kwargs)

        return func_wrapper

    return leaf_decorator
