import os
import copy
import uuid
from urllib.parse import urlparse
from collections import OrderedDict as SortedDict
import json

from django import forms
from django.conf import settings
from django.contrib.admin import widgets as admin_widgets
from django.forms.utils import flatatt
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags, escape
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_text
from django.templatetags.static import static



TINYMCE_BASE_PATH = 'workon/js/vendors/tinymce/'
DEFAULT_TINYMCE_URL = getattr(settings, 'TINYMCE_URL', f"https://cdnjs.cloudflare.com/ajax/libs/tinymce/4.7.6/tinymce.min.js")
DEFAULT_CONFIG = {

    # 'base': f'/{TINYMCE_BASE_PATH}',
    # 'document_base_url': TINYMCE_BASE_PATH,
    'plugins': [
        "advlist autolink lists link image charmap print preview anchor \
        searchreplace visualblocks code fullscreen textcolor \
        insertdatetime media table  paste imagetools "
    ],
    'force_br_newlines': False,
    'force_p_newlines': False,
    'forced_root_block': '',
    "fontsize_formats": "8pt 10pt 12pt 14pt 18pt 24pt 36pt",
    "external_plugins": {
        #"nanospell": STATIC_URL + "js/tinymce/plugins/nanospell/plugins.js",
        "comments": f"{TINYMCE_BASE_PATH}contrib/plugins/comments/plugins.js",
        "base64img": f"{TINYMCE_BASE_PATH}contrib/plugins/base64img/plugins.js",
        "placeholder": f"{TINYMCE_BASE_PATH}contrib/plugins/placeholder/plugins.js",
    },
    'content_css' : ",".join([
        #"https://fonts.googleapis.com/css?family=Rubik:300,400",
        #"css/front.css",
    ]),
    # "gecko_spellcheck" : True,
    # "browser_spellcheck" : True,
    # "nanospell_server": "django",
    # 'paste_as_text': True,
    # 'theme': "modern",
    #'menubar': 'view',
    'menubar': False,
    'contextmenu': None,
    'toolbar': "undo redo | styleselect removeformat | bold italic | forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image base64img media | code",
    'statusbar': True,
    'branding': False,
    #'relative_urls': False,  # use absolute urls when inserting links/images

    'visualblocks_default_state': settings.DEBUG,
    'end_container_on_empty_block': settings.DEBUG,

    'height' : '600',
    'style_formats': [
        { 'title': "Titres", 'items': [
            { 'title': u'Titre 1', 'block': 'h1', 'classes': 'title title1' },
            { 'title': u'Titre 2', 'block': 'h2', 'classes': 'title title2' },
            { 'title': u'Titre 3', 'block': 'h3', 'classes': 'title title3' },
            { 'title': u'Titre 4', 'block': 'h4', 'classes': 'title title4' },
            { 'title': u'Titre 5', 'block': 'h5', 'classes': 'title title5' },
            { 'title': u'Titre 6', 'block': 'h6', 'classes': 'title title6' },
        ]},
        { 'title': "Textes", 'items': [
            { 'title': u'Texte 1', 'block': 'p', 'classes': 'text text1' },
            { 'title': u'Texte 2', 'block': 'p', 'classes': 'text text2' },
            { 'title': u'Texte 3', 'block': 'p', 'classes': 'text text3' },
            { 'title': u'Texte 4', 'block': 'p', 'classes': 'text text4' },
            { 'title': u'Texte 5', 'block': 'p', 'classes': 'text text5' },
            { 'title': u'Texte 6', 'block': 'p', 'classes': 'text text6' },
            { 'title': u'Image à droite', 'inline': 'img', 'classes': 'image-right', 'selector': 'img' },
            { 'title': u'Image à gauche', 'inline': 'img', 'classes': 'image-left', 'selector': 'img' }
        ]},
        { 'title': "Citations", 'items': [
            { 'title': u'Bloc citation', 'block': 'blockquote', 'classes': 'citation' },
            { 'title': u'Text citation', 'inline': 'blockquote', 'classes': 'citation' },
        ]},
        { 'title': "Blocs", 'items': [
            { 'title': u'Ligne', 'block': 'div', 'classes': 'row' },
            { 'title': u'Colonne 50%', 'block': 'div', 'classes': 'col-md-6' },
            { 'title': u'Colonne 50%', 'block': 'div', 'classes': 'col-md-6' },
        ]},
        { 'title': "Images", 'items': [
            { 'title': u'Image à droite', 'inline': 'img', 'classes': 'image-right', 'selector': 'img' },
            { 'title': u'Image à gauche', 'inline': 'img', 'classes': 'image-left', 'selector': 'img' }
        ]},
    ],
}
TINYMCE_CONFIG = getattr(
    settings, 'WORKON', {}
).get('TINYMCE', {}).get('DEFAULT_CONFIG', getattr(settings, 'WORKON_TINYMCE_DEFAULT_CONFIG', DEFAULT_CONFIG))

def is_absolute(url):
    return bool(urlparse(url).netloc)


class HtmlField(forms.CharField):
    def __init__(self, *args, **kwargs):

        attrs = kwargs.get('attrs', {})
        if not attrs.get('placeholder'):
            attrs['placeholder'] = kwargs.get('label', '')

        kwargs['widget'] = HtmlInput(
            tinymce=kwargs.pop('tinymce', None),
            inline=kwargs.pop('inline', False),
            attrs=kwargs.get('attrs', attrs)
        )
        super().__init__(*args, **kwargs)


class HtmlInput(forms.Textarea):

    class Media:
        js = [
            DEFAULT_TINYMCE_URL,
        ]
        css = {
            # 'all': ('js/forms/html.css', )
        }

    def __init__(self, attrs=None, tinymce=None, inline=False):
        super().__init__(attrs=attrs)
        tinymce = tinymce or {}
        self.tinymce = tinymce
        self.inline = inline


    # USE BLEACH FOR FUTURE
    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if value and self.tinymce and self.tinymce.get('apply_format') == "text":
            value = strip_tags(value.replace('<br />', '\n').replace('<br/>', '\n'))
        return value


    def get_config_json(self, config):
        # Fix for js functions
        js_functions = {}
        for k in ('paste_preprocess', 'paste_postprocess'):
            if k in config:
               js_functions[k] = config[k]
               del config[k]
        config_json = json.dumps(config)
        for k in js_functions:
            index = config_json.rfind('}')
            config_json = config_json[:index]+', '+k+':'+js_functions[k].strip()+config_json[index:]
        return config_json

    def get_tinymce_config(self, name, attrs):
        config = copy.deepcopy(TINYMCE_CONFIG)
        config.update(self.tinymce)
        # if mce_config['mode'] == 'exact':
        #
        config['tinymce_url'] = static(DEFAULT_TINYMCE_URL) if not DEFAULT_TINYMCE_URL.startswith('http') else DEFAULT_TINYMCE_URL
        config['mode'] = 'exact'
        config['elements'] = attrs['id']
        if not config.get('placeholder_disabled') == True:
            config['placeholder'] = attrs.get('placeholder', '')
        else:
            config['placeholder'] = None


        config['language'] = None
        config['language_url'] = static(f'{TINYMCE_BASE_PATH}/langs/fr_FR.js')

        if self.inline:
            config['inline'] = True
            config['content_css'] = None
            config['elements'] = "div_inline_%s" % name

            config['force_br_newlines'] = False
            config['force_p_newlines'] = False
            config['forced_root_block'] = ''

        if config.get('content_css', None):
            content_css_new = []
            for url in config['content_css'].split(','):
                url = url.strip()
                if not is_absolute(url):
                    content_css_new.append(os.path.join(settings.STATIC_URL, url))
                else:
                    content_css_new.append(url)
            config['content_css'] = ",".join(content_css_new)

        if 'external_plugins' in config:

            for key, url in config['external_plugins'].items():
                url = url.strip()
                if not is_absolute(url):
                    config['external_plugins'][key] = os.path.join(settings.STATIC_URL, url)

        return config

    def render(self, name, value, attrs=None):

        if value is None:
            value = ''
        value = smart_text(value)
        flatattrs = self.build_attrs(attrs)
        flatattrs['name'] = name


        if self.tinymce and self.tinymce.get('apply_format') == "text":
            value = strip_tags(value).replace('\n', '<br />').replace('\n', '<br />')

        config = {
            'inline': self.inline,
            'type' : 'tinymce',
            'id' : attrs['id'],
            'name' : name,
            'settings' : self.get_tinymce_config(name, attrs)
        }
        flatattrs['data-form-widget-html'] = self.get_config_json(config)


        if self.inline:

            html = [u"""<div class="contrib-tinymce_inline">
                <div style="overflow: hidden;">
                    <textarea%s>%s</textarea>
                </div>
                <div id="div_inline_%s" placeholder="%s">%s</div>
            </div>
            """ % (name, flatattrs.get('placeholder'), mark_safe(value), flatatt(flatattrs), escape(value))]
            return mark_safe('\n'.join(html))

        else:
            html =  ['<textarea%s style="max-height: 1px !important; opacity: 0; height: 1px; position: relative; top: 10px; padding:0px; border:0px;">%s</textarea>' % (flatatt(flatattrs), escape(value))]
            return mark_safe('\n'.join(html))
