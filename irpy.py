#!/usr/bin/python
import logging

from collections import defaultdict
from threading import Lock

#Handle your lock stack
D_LOCK = defaultdict(lambda: defaultdict(lambda: Lock()))

D_DEBUG = False

if D_DEBUG:
    #import pylab
    import networkx as nx
    D_DG = defaultdict(lambda: nx.DiGraph())

def DG_plot(self):

    import matplotlib.pyplot as plt
    import pylab
    from networkx.drawing.nx_agraph import graphviz_layout

    plt.clf()

    values = D_DG.values()
    nb_graph = len(values)
    for i, D in enumerate(values):
        
        plt.subplot(nb_graph, 1, i+1)
        pos=graphviz_layout(D,prog='dot')
    
        node_color = [ D.node[n]['color'] for n in D.nodes()]
    
        nx.draw(D,pos,with_labels=True,arrows=True,node_color=node_color)
            
    plt.pause(1)

def change_and_plot(lazy_obj, pri_node, color):
    if D_DEBUG:
        D_DG[lazy_obj].node[pri_node]['color']= color
        DG_plot(lazy_obj)
    

def appendattr_lock(object, name, value):
    with D_LOCK[object][name]:
        s = getattr(object, name)
        setattr(object, name, set([value]) | s)

def setattr_lock(object, name, value):
    with D_LOCK[object][name]:
        setattr(object, name, value)

def delattr_lock(object, name):
    with D_LOCK[object][name]:
        #Maybe somebody already delete this private node
        try:
            delattr(object, name)
        except AttributeError:
            pass

# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
#Satisfaction
def  set_node_value(lazy_obj, pri_node, value):

    def irp_sap(pri_node, direction, visited=None):
        """
        Direction is $parents or $children, recurse accordingly
        """
        if visited is None:
            visited = set()

        visited.add(pri_node)

        s = getattr(lazy_obj, "{0}_{1}".format(pri_node, direction))

        for next_ in s - visited:
            irp_sap(next_, direction, visited)

        return visited
    
    def irp_remove_ancestor_cache():
        l_ancestor = irp_sap(pri_node, "parents",) - set([pri_node])
    
        logging.debug("Unset parents: %s", l_ancestor)
        for parent in l_ancestor:
            delattr_lock(lazy_obj,parent)
    
    def irp_set_uncoherent_ancestor():
        #Now handle the mutability
        l_descendant = irp_sap(pri_node, "children") - set([pri_node])
    
        logging.debug("All %s in uncoherent cause of %s", l_descendant, pri_node)
        for child in l_descendant:
            appendattr_lock(lazy_obj, "{0}_uncoherent".format(child), pri_node)            
            change_and_plot(lazy_obj,child,'black')
    
    def irp_unset_siblings():
    
        visited = set()
    
        for sibling in getattr(lazy_obj, "%s_uncoherent" % pri_node):
    
            l_descendant = irp_sap(sibling, "children")  - visited
    
            logging.debug("%s was uncoherent cause of %s", pri_node, sibling)
            logging.debug("So maybe %s is valid now", l_descendant)
    
            for descendant in l_descendant:
                s = getattr(lazy_obj, "%s_uncoherent" % descendant) - set([sibling])
                setattr_lock(lazy_obj, "{0}_uncoherent".format(descendant), s)
                visited.add(descendant)
    
    logging.debug("Set node %s", pri_node)
    setattr_lock(lazy_obj, pri_node, value)
    irp_remove_ancestor_cache()
    irp_set_uncoherent_ancestor()
    irp_unset_siblings()


class Stack(object):

    #Handle your execution stack
    d_path = defaultdict(lambda: [None])

    def __init__(self,lazy_obj, pri_node):
        self.lazy_obj = lazy_obj
        self.pri_node = pri_node

    def __enter__(self):
        with D_LOCK[self.lazy_obj][self.pri_node]:
            caller_name = Stack.d_path[self.lazy_obj][-1]
            Stack.d_path[self.lazy_obj].append(self.pri_node)

        return caller_name

    def __exit__(self, type, value, traceback):
        with D_LOCK[self.lazy_obj][self.pri_node]:
            Stack.d_path[self.lazy_obj].pop()

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

    if D_DEBUG:
        D_DG[lazy_obj].add_node(pri_node)

    logging.debug("Ask for %s", pri_node)

    if getattr(lazy_obj, "%s_uncoherent" % pri_node):
        raise AttributeError, "Node is incoherent {0}".format(pri_node)

    with Stack(lazy_obj,pri_node) as caller_name:
        #~=~=~
        #Handle the mutability
        #~=~=~

        if caller_name:
            #Set parent
            local_parent = "{0}_parents".format(pri_node)
            appendattr_lock(lazy_obj, local_parent, caller_name)
    
            #Set children
            local_child = "{0}_children".format(caller_name)
            appendattr_lock(lazy_obj, local_child, pri_node)
    
            if D_DEBUG:
                D_DG[lazy_obj].add_edge(caller_name,pri_node)
    
        #~=~=~
        #Get and set the value node
        #~=~=~
    
        try:
            value = getattr(lazy_obj, pri_node)
        except AttributeError:
            logging.debug("Provide")
            change_and_plot(lazy_obj,pri_node,'red')
    
            value = provider(lazy_obj)
            setattr_lock(lazy_obj, pri_node, value)
    
            change_and_plot(lazy_obj,pri_node,'green')
                
        else:
            logging.debug("Already provided")
            change_and_plot(lazy_obj,pri_node,'green')
        
    return value

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

    #Handle the instance variable.
    #We need a global dict, cause property are created when the class is imported
    #not when it is execuded

    d_only_once = defaultdict(lambda: defaultdict(lambda: False))

    def __init__(self, provider, leaf_node=None, immutability=True):

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

        if not lazy_property.d_only_once[obj][self.node]:
            d = {
                "_{0}_children": set(),
                "_{0}_parents": set(),
                "_{0}_uncoherent": set()
            }

            for attr, value in d.items():
                setattr(obj, attr.format(self.node), value)

            lazy_property.d_only_once[obj][self.node] = True

    def __get__(self, obj, objtype):
        "Get the value of the node"
        self.init_obj_attr(obj)

        return get_irp_node(obj, self.pri_node, self.provider)

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

        set_node_value(lazy_obj=obj, pri_node=self.pri_node,value=value)

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
                                  leaf_node=node,
                                  immutability=node in immutables)
                #If this ugly? Yeah... Is this an issue? I don't really know
                setattr(self.__class__, node, p)

            return func(self, *args, **kwargs)

        return func_wrapper

    return leaf_decorator
