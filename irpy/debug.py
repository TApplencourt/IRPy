#                          
# |   _   _   _  o ._   _  
# |_ (_) (_| (_| | | | (_| 
#         _|  _|        _| 
#         


D_LOGGER=dict()

import logging
def set_loggin_level(name, level):

    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()

        str_ = '[%(relativeCreated)d ms] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
        formatter = logging.Formatter(str_)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)

    return logger

def logging_debug(obj,msg, *args, **kwargs):
    name = obj.__class__.__name__
    try:
        D_LOGGER[name].debug(msg,*args,**kwargs)
    except:
        pass

# __                 _  
#  /  _  ._ _  |\/| / \ 
# /_ (/_ | (_) |  | \_X 
#                       

from __init__ import singleton
@singleton
class irp_zmq(object):
    import zmq
    
    irp_context = zmq.Context()
    socket =  irp_context.socket(zmq.REQ)

    port = 5556
    adr = "tcp://*:%s" % port
    print "Debug of IRP process (%s)"%adr
    socket.bind(adr)


def irp_debug(cls):
    name = cls.__name__
    logger = set_loggin_level(name=name,
                              level="DEBUG")
    D_LOGGER[name]=logger

    setattr(cls,"irp_debug",True)

    return cls

def zmq_send_edge(obj,u,v):
    "Add an edge between u and v."

    if hasattr(obj.__class__,"irp_debug"):
        str_="{topic} {obj} {u} {v}".format(topic="edge",
                                            obj=id(obj),
                                            u=u,
                                            v=v)
    
        
        socket = irp_zmq().socket
        socket.send(str_)
        socket.recv()


def zmq_send_node_info(obj, node, mode=1):
    "1: Not provided"
    "2: Already Provided"
    if hasattr(obj.__class__,"irp_debug"):
        str_="{topic} {obj} {node} {mode}".format(topic="mode",
                                                  obj=id(obj),
                                                  node=node,
                                                  mode=mode)
        socket = irp_zmq().socket
        socket.send(str_)
        socket.recv()


