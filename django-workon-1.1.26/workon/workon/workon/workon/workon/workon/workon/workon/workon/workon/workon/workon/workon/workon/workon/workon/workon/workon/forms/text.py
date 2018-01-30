
from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from .html import HtmlInput, HtmlField

class TextField(HtmlField):
    def __init__(self, *args, **kwargs):
        super(TextField, self).__init__(*args, **kwargs)

class TextInput(HtmlInput):

    def __init__(self, *args, **kwargs):
        kwargs['inline'] = True
        super(TextInput, self).__init__(*args, **kwargs)

    def get_tinymce_config(self, name,  attrs):
        config = super(TextInput, self).get_tinymce_config(name, attrs)
        config['toolbar'] = 'undo redo'
        return config