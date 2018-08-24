import json
import re
import os
import workon
from django.conf import settings


register = workon.TemplateLibrary()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, os.environ.get(name, ''))

@register.filter
def from_settings(name):
    return getattr(settings, name, os.environ.get(name, ''))

@register.filter(name='divide_by')
def divide_by(value, arg):
    try:
        return int(int(value) / int(arg))
    except (ValueError, ZeroDivisionError):
        return None

@register.filter(name='range')
def range_filter(x):
    return range(x)
    
@register.filter(name='int')
def intval(value):
    try:
        return int(value)
    except ValueError:
        return None

@register.filter(name='numbers')
def numbers(value):
    return workon.numbers(value)
    
@register.filter(name='percent')
def percent(value, decimal=2):
    return workon.percent(value, decimal=decimal)

# @register.simple_tag(name='delta_percent')
# def delta_percent(value, old_value, decimal=2):
#     return percent(((value - old_value)  /  old_value) if old_value else None, decimal)

@register.filter
def get(object, name, default=None):
    return object.get(name, default)

@register.filter(name="getattr")
def get_attr(object, name, default=None):
    return getattr(object, name, default)

@register.filter()
def currency(value):
    return workon.currency(value if value else 0)

@register.filter()
def pluralize(value, suffix="s"):
    return suffix if value else ""

@register.filter()
def typeof(obj):
    return type(obj)

@register.filter
def startswith(str, compare):
    return str.startswith(compare)

@register.filter
def jsonify(obj):
    return workon.jsonify(obj)

@register.filter(name='zfill')
def zfill(obj, number):
    return str(obj).zfill(number)

@register.filter(name='sizify')
def sizify(value):
    return workon.sizify(value)

@register.filter
def sanitize(html):
    workon.sanitize(html)


from workon.templatetags.workon_urls import lazy_register
lazy_register(register)


from workon.templatetags.workon_compress import lazy_register
lazy_register(register)


from workon.templatetags.workon_assets import lazy_register
lazy_register(register)


from workon.templatetags.workon_form import lazy_register
lazy_register(register)


from workon.templatetags.workon_metas import lazy_register
lazy_register(register)


from workon.templatetags.workon_thumbnail import lazy_register
lazy_register(register)