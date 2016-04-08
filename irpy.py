#!/usr/bin/python
import logging

from collections import defaultdict
from threading import Lock

#Handle your execution stack
D_PATH = defaultdict(lambda: [None])
#Handle your lock stack
D_LOCK = defaultdict(lambda: defaultdict(lambda: Lock()))


#  _                                             _ 
# |_ _  | |  _         _|_ |_   _    |  _   _. _|_ 
# | (_) | | (_) \/\/    |_ | | (/_   | (/_ (_|  |  
#
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


# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
def get_irp_node(IRP_instance, provider, private_node):
    """
    'provider' is a function used to compute value of the node.
    'private_node', is private value of the node ("_node").
    'parent' is the other node that wants to access to this particular node.
    'IRP_instance' is an instance of the class which uses IRPy.

        First, this function returns the 'private_node' value,
               if it does not exist yet, this function will set it.

        Secondly, we handle your own stack of function execution
               in order to add into ${private_node}_parent all
               the names of the callers (the paths).

    This function is (maybe) trade safe.
    """
    with D_LOCK[IRP_instance][private_node]:

        logging.debug("Ask for %s", private_node[1:])

        #Handle your execution stack
        caller_name = D_PATH[IRP_instance][-1]

        D_PATH[IRP_instance].append(private_node)

        #Get and set the value node
        try:
            value = getattr(IRP_instance, private_node)
        except AttributeError:
            logging.debug("Provide")

            value = provider(IRP_instance)

            setattr(IRP_instance, private_node, value)
        else:
            logging.debug("Already provided")
        #Set the parent
        finally:
            #Handle the mutability
            local_parent = "{0}_parent".format(private_node)
            if caller_name:

                try:
                    s = getattr(IRP_instance, local_parent).add([caller_name])
                except AttributeError:
                    setattr(IRP_instance, local_parent, set([caller_name]))
                else:
                    setattr(IRP_instance, local_parent, s)

        #Handle the execution stack
        assert (D_PATH[IRP_instance].pop() == private_node)

    return value


def set_irp_node(IRP_instance, provider, private_node, value):
    """
    'provider' is a function used to compute the value node.
    'private_node', is private value of the node ("_node").
    'parent' is the other node that wants to access to this particular node.
    'value' is the value of the node we want to set.

    First we remove all the private variables (caches) of the nodes which use this 
        particular node. Then we set the new value of the node.

    This function is (maybe) thread safe.  
    """

    logging.debug("Set node %s", private_node[1:])

    for i in irp_ancestor(IRP_instance, private_node) - set([private_node]):

        logging.debug("Unset parent: %s", i[1:])

        with D_LOCK[IRP_instance][i]:
            delattr(IRP_instance, i)

    with D_LOCK[IRP_instance][private_node]:
        setattr(IRP_instance, private_node, value)


#  _                              
# | \  _   _  _  ._ _. _|_  _  ._ 
# |_/ (/_ (_ (_) | (_|  |_ (_) |  
#
def irp_node(provider):
    """
    'provider' is a function.

    This is the immutable decorator. It is really similar to the 'property' function.
    In fact we return a property with custom fget and fset. The fset raises an AttributeError
    as the node is immutable.
    """
    str_provider = provider.__name__
    private_node = "_{0}".format(str_provider)

    def fget(self):
        return get_irp_node(self, provider, private_node)

    def fset(self, value):
        raise AttributeError, "Immutable Node"

    return property(fget=fget, fset=fset)


def irp_node_mutable(provider):
    """
    'provider' is a function.

    This is the mutable decorator. It is really similar to the 'property' function.
    In fact we return a property with custom fget and fset
    """
    str_provider = provider.__name__
    private_node = "_{0}".format(str_provider)

    def fget(self):
        return get_irp_node(self, provider, private_node)

    def fset(self, value):
        return set_irp_node(self, provider, private_node, value)

    return property(fget=fget, fset=fset)


def irp_leaves_mutable(*irp_leaves):
    "This a named decorator"
    'For all the nodes in irp_leaves we create the associated property'

    'We set the new property and then we execute the function'

    def leaf_decorator(func):
        def func_wrapper(self, *args, **kwargs):

            for str_provider in irp_leaves:
                private_node = "_{0}".format(str_provider)

                def provider(self):
                    return getattr(self, private_node)

                def fget(self):
                    return get_irp_node(self, provider, private_node)

                def fset(self, value):
                    return set_irp_node(self, provider, private_node, value)

                #If this ugly? Yeah... Is this an issue? I don't realy know
                setattr(self.__class__, str_provider, property(fget=fget,
                                                               fset=fset))

            return func(self, *args, **kwargs)

        return func_wrapper

    return leaf_decorator
