import pickle
from celery import Celery
from datetime import date
    
celery = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

def serializingTask(function):
    @celery.task  
    def wrapper(string):
        (args, kargs) = pickle.loads(string)
        return function(*args, **kargs)
    delay = wrapper.delay
    wrapper.delay = lambda *args, **kargs: delay(pickle.dumps((args, kargs)))
    wrapper.direct = function
    return wrapper

@celery.task
def add(x, y):
    print(x)
    return x + y

@serializingTask
def findIt(start, end):
    format = '%d.%m.%Y'
    print(start.strftime(format))
    print(end.strftime(format))
    pass