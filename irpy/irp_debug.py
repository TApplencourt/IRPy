#                          
# |   _   _   _  o ._   _  
# |_ (_) (_| (_| | | | (_| 
#         _|  _|        _| 
#         


from collections import defaultdict
import logging

D_LOGGER = defaultdict(lambda: logging.getLogger())

def set_loggin_level(name, level):

    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()

        str_ = '[%(relativeCreated)d ms] %(levelname)s - %(message)s'
        formatter = logging.Formatter(str_)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)

    return logger

def irp_logger(obj):
    return D_LOGGER[obj.__class__.__name__]

# __                 _  
#  /  _  ._ _  |\/| / \ 
# /_ (/_ | (_) |  | \_X 
#                       

from __init__ import singleton
@singleton
class irp_zmq(object):

    def __init__(self):

        import zmq
        irp_context = zmq.Context()
        self.socket =  irp_context.socket(zmq.REQ)
    
        adr_template= "tcp://*"
        port = self.socket.bind_to_random_port(adr_template,
                                               min_port=6001,max_port=7001,max_tries=100)
    
        adr = "{0}:{1}".format(adr_template,port)
        print "Debug of IRP process (%s)"%adr


        

def debug(cls):
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


