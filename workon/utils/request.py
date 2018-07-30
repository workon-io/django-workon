from django.http import HttpRequest
import workon


__all__ = ['contribute_to_request']

def get_memoized_method(r, method, attr_name):
    if not hasattr(r, attr_name):
        setattr(r, attr_name, method(r))
    return getattr(r, attr_name)

def contribute_to_request(name, method, cache=None, memoized=True):

    if memoized == True:
        setattr(HttpRequest, name, lambda r: get_memoized_method(r, method, f'{name}__memoized_result') )

    elif cache:
        setattr(HttpRequest, name, lambda r: workon.cache_get_or_set(f'workon_httprequest_cached_{name}', method(r), cache))
    else:
        setattr(HttpRequest, name, method)