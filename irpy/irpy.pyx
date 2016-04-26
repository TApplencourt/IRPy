#!/usr/bin/python
from collections import defaultdict

#Handle your execution stack
d_path = [None]

def appendattr(object, name, value):
    try:
        s = getattr(object, name)
    except AttributeError:
        setattr(object, name, set([value]))
    else:
        setattr(object, name, set([value]) | s)

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

    def __init__(self, provider, immutability=True):
        """Provider: If a function who will be used to compute the node
           leaf_node: If the name of the node
           immutability: If immutability is set you cannot set the node"""

        self.provider = provider

        self.node = provider.__name__

        self.pri_node = "_{0}".format(self.node)
        self.parents = "_{0}_parents".format(self.node)
        self.children = "_{0}_children".format(self.node)
        self.uncoherent = "_{0}_uncoherent".format(self.node)


        self.immutability = immutability

        self.last_caller = None

    def __get__(self, obj, objtype):
        "Get the value of the node"
        caller_name = d_path[-1]

        pri_node = self.pri_node

        "Handle The Genealogy"
        if caller_name != self.last_caller:
            appendattr(obj,self.parents,caller_name)
            appendattr(obj,"{0}_children".format(caller_name),pri_node)
            self.last_caller = caller_name
 
        "Get the value"
        try:
            value = getattr(obj, pri_node)
        except AttributeError:
            
            try:
                getattr(obj,self.uncoherent)
            except AttributeError:   
                pass
            else:
                raise AttributeError, "Node is incoherent {0}".format(pri_node)

            d_path.append(pri_node)

            value = self.provider(obj)
            setattr(obj, pri_node, value)

            d_path.pop()

        return value

    def __set__(self, obj, value):
        """Set the value of the node
        But wait, leaves are "gradual typed" variable! Youpi!
        Idea borrowed from the-worst-programming-language-ever (http://bit.ly/13tc6XW)
        """
        if self.immutability:
            raise AttributeError, "Immutable Node {0}".format(self.pri_node)
        else:
            set_node_value(lazy_obj=obj, pri_node=self.pri_node, value=value)

def lazy_property_mutable(provider):
    "Return a lazy_property mutable"
    return lazy_property(provider=provider, immutability=False)

# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
#Satisfaction
def set_node_value(lazy_obj, pri_node, value):

    setattr(lazy_obj, pri_node, value)
    
    def irp_sap(pri_node, direction, visited=None):
        """
        Direction is $parents or $children, recurse accordingly
        """
        if visited is None:
            visited = set()

        visited.add(pri_node)
        try:
            s = getattr(lazy_obj, "{0}_{1}".format(pri_node, direction))
        except AttributeError:
            s = set()

        for next_ in s - visited:
            irp_sap(next_, direction, visited)

        return visited - set([None])
    
    def irp_remove_ancestor_cache():
        l_ancestor = irp_sap(pri_node, "parents") - set([pri_node])
        
        for parent in l_ancestor:
            try:
                delattr(lazy_obj,parent)
            except AttributeError:
                pass

    def irp_set_uncoherent_descendant():
        #Now handle the mutability
        l_descendant = irp_sap(pri_node, "children") - set([pri_node])
        
        for child in l_descendant:
            appendattr(lazy_obj, "{0}_uncoherent".format(child), pri_node)
            try:
                delattr(lazy_obj,child)
            except AttributeError:
                pass

    def irp_unset_siblings():

        str_uncoherent = "{0}_uncoherent"

        try:
            l_uncoherent = getattr(lazy_obj, str_uncoherent.format(pri_node))
        except AttributeError:
            pass
        else:

            visited = set()
            for sibling in l_uncoherent:
                for descendant in irp_sap(sibling, "children")  - visited:

                    try:
                        s = getattr(lazy_obj, str_uncoherent.format(descendant)) - set([sibling])
                    except AttributeError:
                        pass
                    else:
                        if not s:
                            delattr(lazy_obj,"{0}_uncoherent".format(descendant))
                        else:
                            setattr(lazy_obj, "{0}_uncoherent".format(descendant), s)
        
                    visited.add(descendant)


    irp_remove_ancestor_cache()
    irp_set_uncoherent_descendant()
    irp_unset_siblings()