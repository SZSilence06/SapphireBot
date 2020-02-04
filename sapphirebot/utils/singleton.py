# coding=utf-8
from threading import Lock
import inspect

class SingletonExistedError(Exception):
    def __init__(self, classType):
        super(SingletonExistedError, self).__init__('trying to construct instance of singleton class ' + classType.__name__ + ' while an instance has already existed!')
 
def __get_instance(classType):
    if classType._instance is None:
        classType._lock.acquire()
        if classType._instance is None:
            classType._instance = classType()
        classType._lock.release()
    return classType._instance
 
def __singleton_init_decorator(init_func):
    def __singleton_init(self):
        # check whether instance has existed
        if self._instance is not None:
            raise SingletonExistedError(type(self))
 
        # set instance of the class and ancestor singletons to self
        for baseClass in inspect.getmro(type(self)):
            if '_instance' in baseClass.__dict__:
                baseClass._instance = self
 
        init_func(self)
    return __singleton_init
 
 
def singleton(classType):
    classType._instance = None
    classType._lock = Lock()
    classType.get_instance = classmethod(__get_instance)
    classType.__init__ = __singleton_init_decorator(classType.__init__)
    return classType