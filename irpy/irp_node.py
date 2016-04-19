import logging
from __init__ import appendattr_lock, setattr_lock, delattr_lock, Stack

from irp_debug import zmq_send_edge, zmq_send_node_info, irp_logger
# ___                                                  
#  |     _  _. ._ / _|_    _   _ _|_   ._   _   _|  _  
# _|_   (_ (_| | |   |_   (_| (/_ |_   | | (_) (_| (/_ 
#                          _|
#Satisfaction
def set_node_value(lazy_obj, pri_node, value):

    logger = irp_logger(lazy_obj)
    logger.debug("Set node %s", pri_node)
    setattr_lock(lazy_obj, pri_node, value)
    
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
        
        logger.debug("Unset parents: %s", l_ancestor)
        for parent in l_ancestor:
            delattr_lock(lazy_obj,parent)
            zmq_send_node_info(lazy_obj,parent,mode=1)

    def irp_set_uncoherent_ancestor():
        #Now handle the mutability
        l_descendant = irp_sap(pri_node, "children") - set([pri_node])
    
        logger.debug("All %s in uncoherent cause of %s", l_descendant, pri_node)
        for child in l_descendant:
            appendattr_lock(lazy_obj, "{0}_uncoherent".format(child), pri_node)
    
    def irp_unset_siblings():
    
        visited = set()
    
        for sibling in getattr(lazy_obj, "%s_uncoherent" % pri_node):
    
            l_descendant = irp_sap(sibling, "children")  - visited
    
            logger.debug("%s was uncoherent cause of %s", pri_node, sibling)
            logger.debug("So maybe %s is valid now", l_descendant)
    
            for descendant in l_descendant:
                s = getattr(lazy_obj, "%s_uncoherent" % descendant) - set([sibling])
                setattr_lock(lazy_obj, "{0}_uncoherent".format(descendant), s)
                visited.add(descendant)


    irp_remove_ancestor_cache()
    irp_set_uncoherent_ancestor()
    irp_unset_siblings()

def get_node(lazy_obj, pri_node, provider):
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
    logger = irp_logger(lazy_obj)

    logger.debug("Ask for %s", pri_node)
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

            #Send
            zmq_send_edge(obj=lazy_obj,
                          u=caller_name,
                          v=pri_node)    
        #~=~=~
        #Get and set the value node
        #~=~=~
    
        try:
            value = getattr(lazy_obj, pri_node)
        except AttributeError:
            logger.debug("Provide")

            zmq_send_node_info(lazy_obj,pri_node,mode=1)
            value = provider(lazy_obj)
            zmq_send_node_info(lazy_obj,pri_node,mode=2)
            setattr_lock(lazy_obj, pri_node, value)
   
        else:
            zmq_send_node_info(lazy_obj,pri_node,mode=2)
            logger.debug("Already provided")
        
    return value