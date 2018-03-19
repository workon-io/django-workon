import re


__all__ = ["numbers", "rate_repr", "to_int", "to_float", "str_to_float", "is_float"]


def numbers(value):
    if value is not None:
        value = str(value)
        if value:
            value = re.sub(r"^(-?\d+)(\d{3})", r'\g<1> \g<2>', value)
    return value

def rate_repr(value, decimal=2):
    try:
        value = round(float(value), decimal)
        if value > 0:
            return f'+{value}'
        elif value < 0:
            return f'{value}'
        else:
            return f'~{value}'
    except:
        return 0


def to_int(value):
    number = ''
    for c in value[::-1]:
        if c.isdigit():
            number += c
    return int(number)

def to_float(value, default=None):
    try:
        return float(value.replace(',', '.').replace(' ', ''))
    except:
        return default
    
def str_to_float(str, default=None):
    try:
        return float(str.replace(',', '.').strip())
    except:
        return default

def is_float(var):
    try:
        float(var)
    except (TypeError, ValueError):
        return False
    return True

