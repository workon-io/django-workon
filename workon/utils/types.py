from types import *

def is_lambda(value):
    return isinstance(value, LambdaType)
    
def is_method(value):
    return isinstance(value, MethodType)