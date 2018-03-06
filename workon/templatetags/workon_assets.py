import os
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.conf import settings


__all__ = ['lazy_register']
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/workon')
STATIC_JS_PATH = os.path.join(STATIC_PATH, 'js')
STATIC_JS_NAME = 'workon/js'


def lazy_register(register):


    @register.inclusion_tag('workon/assets/javascripts.html')
    def javascripts(*names, **kwargs):
        global_async = kwargs.get('async', False)
        externals = ''
        internals = ''
        paths = [
        ]
        for name in names:
            if name == 'workon':                
                paths += [
                    f'{STATIC_JS_NAME}/vendors/jquery.js',
                    f'{STATIC_JS_NAME}/vendors/jquery-migrate.js',
                    f'{STATIC_JS_NAME}/vendors/jquery-ui.js',
                    f'{STATIC_JS_NAME}/vendors/moment.min.js',
                ]

                for path in os.listdir(os.path.join(STATIC_JS_PATH, name)):
                    if path.endswith('.js'):
                        paths.append(os.path.join(f'{STATIC_JS_NAME}/{name}', path))

                # paths += [

                #     f'{STATIC_JS_NAME}/plugins/tinymce/tinymce.min.js',
                # ]
                
            elif name == 'slick':               
                paths.append(f'{STATIC_JS_NAME}/plugins/slick.js')

            elif name == 'chart':               
                paths.append(f'{STATIC_JS_NAME}/plugins/chart.js')

            elif name == 'json':               
                paths.append(f'{STATIC_JS_NAME}/plugins/json.js')

            # elif name == 'tinymce':               
            #     paths.append(f'{STATIC_JS_NAME}/vendors/tinymce/tinymce.min.js')

            elif name == 'dropzone':               
                paths.append(f'{STATIC_JS_NAME}/plugins/dropzone.js')

            elif name == 'code':               
                paths.append(f'{STATIC_JS_NAME}/plugins/code.js')

            elif name == 'isotope':               
                paths.append(f'{STATIC_JS_NAME}/plugins/isotope.js')

            else:
                paths.append(name)

        for path in paths:
            if path.startswith('http') or path.startswith('//'):
                externals += f'<script type="text/javascript" src="{path}"></script>'
            else:
                internals += f'<script type="text/javascript" src="{static(path)}"></script>'

        return {
            'externals': mark_safe(externals),
            'internals': mark_safe(internals),
        }

    PACKAGES_CSS = {
        'workon': 'workon/css/workon.css',
        'materialize-icons': [
            'https://fonts.googleapis.com/icon?family=Material+Icons',
        ],
    }
    @register.inclusion_tag('workon/assets/stylesheets.html')
    def stylesheets(*names):
        internals = ''
        externals = ''
        if not names:
            names = PACKAGES_CSS.keys()
        packages = []
        for name in names:
            paths = PACKAGES_CSS.get(name)
            if paths:
                if isinstance(paths, list):
                    packages += paths
                else:
                    packages.append(paths)
            elif name == "slick":
                packages.append(name)
            else:
                packages.append(name)
        for path in packages:
            if path.startswith('http') or path.startswith('//'):
                externals += f'<link type="text/css" rel="stylesheet"  href="{path}" media="screen,projection" />'
            else:
                internals += f'<link type="text/css" rel="stylesheet"  href="{static(path)}" media="screen,projection" />'
        return {
            'externals': mark_safe(externals),
            'internals': mark_safe(internals)
        }

    @register.inclusion_tag('workon/assets/messages.html')
    def messages(messages):
        return {
            'messages': messages
        }
