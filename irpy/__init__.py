from collections import defaultdict
from threading import Lock

D_LOCK = defaultdict(lambda: defaultdict(lambda: Lock()))

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

def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance
