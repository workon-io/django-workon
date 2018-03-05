'''Public utilities'''
from workon.contrib.cleaner.cache import make_cleanup_cache as _make_cleanup_cache


def refresh(instance):
    '''Refresh the cache for an instance'''
    return _make_cleanup_cache(instance)