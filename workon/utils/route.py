import sys
from django.conf.urls import url, re_path
from django.contrib.auth.decorators import login_required as login_required_statement, user_passes_test
from django.http.request import HttpRequest
from django.urls import reverse, exceptions
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

staff_required_statement = user_passes_test(lambda u: u.is_staff)
superuser_required_statement = user_passes_test(lambda u: u.is_superuser)

__all__ = ['route']

_previous_route_url = None


def route(  
    pattern,
    name=None,
    attach=HttpRequest,
    attach_attr=None,
    view=None,
    view_kwargs={},
    args=(),
    kwargs={},
    fail_as_previous=False,
    login_required=False,
    staff_required=False,
    superuser_required=False,
    custom_required=None,
    csrf_exempt=None,
):
    global _previous_route_url

    caller_filename = sys._getframe(1).f_code.co_filename
    containers = [caller_filename]

    splitted = caller_filename.rsplit('/', 1)
    if len(splitted) > 1:
        caller_filename = f'{splitted[0]}/__init__.py'
        containers.append(caller_filename)
        
    # splitted = caller_filename.rsplit('/views/')
    # if len(splitted) > 1:
    #     caller_filename = f'{splitted[0]}/views/__init__.py'


    pattern = pattern
    # if not pattern.endswith('$'):
    #     pattern = f'{pattern}$'
    if name:
        url_name  = name.split(':')[-1]
    else:
        url_name = None
    modules = []
    for m in sys.modules.values():
        if m and '__file__' in m.__dict__:
            for caller_filename in containers:
                if m.__file__.startswith(caller_filename):
                    modules.append(m)
            # break

    if name and attach:
        def reversor(attached):
            future_args = ( method(attached) for method in args )
            future_kwargs = { attr: method(attached) for attr, method in kwargs.items() }
            if hasattr(attached, f'{attach_attr}_url_previous'):
                try:
                    return reverse(name, args=future_args, kwargs=future_kwargs)
                except exceptions.NoReverseMatch:
                    previous = getattr(attached, f'{attach_attr}_url_previous')
                    future_args = ( method(attached) for method in previous[1] )
                    future_kwargs = { attr: method(attached) for attr, method in previous[2].items() }
                    # query = previous[3]
                    return reverse(previous[0], args=future_args, kwargs=future_kwargs)
            else:
                return reverse(name, args=future_args, kwargs=future_kwargs)

        attach_attr = name.replace('-', '_').replace(':', '_') if not attach_attr else attach_attr
        setattr(attach, f'{attach_attr}_url' , reversor)
        if fail_as_previous:
            setattr(attach, f'{attach_attr}_url_previous' , _previous_route_url)

        _previous_route_url = (name, args, kwargs)

    def _wrapper(class_or_method):

        if modules:
            for module in modules:
                if 'urlpatterns' not in module.__dict__:
                    module.urlpatterns = []

            if hasattr(class_or_method, 'as_view'):
                view = class_or_method.as_view()
            else:
                view = class_or_method

            if login_required:
                view = login_required_statement(view)
            if staff_required:
                view = staff_required_statement(view)
            if superuser_required:
                view = superuser_required_statement(view)
            if custom_required:
                view = user_passes_test(custom_required)(view)

            for module in modules:
                # if csrf_exempt:
                #     module.urlpatterns += [ re_path(pattern, csrf_exempt(view), name=url_name ) ]
                # else:
                module.urlpatterns += [ re_path(pattern, view, name=url_name ) ]

            # print('PATTERNS', module, module.__dict__.get('urlpatterns'))
            # print('\n')

        return class_or_method

    return _wrapper
