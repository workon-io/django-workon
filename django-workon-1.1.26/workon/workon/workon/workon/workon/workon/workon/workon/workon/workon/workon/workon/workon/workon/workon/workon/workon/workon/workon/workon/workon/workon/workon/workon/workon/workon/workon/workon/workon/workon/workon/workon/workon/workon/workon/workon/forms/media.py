# encoding: utf-8

import re
import os
import logging
import json

from django.conf import settings
from django import forms
from django.template import Context
from django.forms.widgets import FILE_INPUT_CONTRADICTION, CheckboxInput, FileInput
from django.template.loader import render_to_string
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.core.files.uploadedfile import InMemoryUploadedFile
try:
    from sorl.thumbnail.shortcuts import get_thumbnail
except:
    def get_thumbnail(image_url, *args, **kwargs):
        return image_url


logger = logging.getLogger(__name__)


EMBED_TYPES = {
    'youtube': [
        [
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?\s"]{11})',

            '<iframe class="contrib-media" src="'
            'https://www.youtube.com/embed/\\6?controls=0&amp;showinfo=0"'
            'scrolling="no" frameborder="no" allowfullscreen></iframe>'
        ]
    ],
    'soundcloud': [
        [
            r'(http[s]?\:\/\/w\.soundcloud\.com\/player\/\?url=([^"]+))',
            '<iframe class="contrib-media" src="https://w.soundcloud.com/player/?url=\\2" scrolling="no" frameborder="no" allowfullscreen></iframe>'
        ],
        [
            r'(http[s]?\:\/\/soundcloud\.com\/[\d\w\-_]+/[\d\w\-_]+)',
            '<iframe class="contrib-media" src="https://w.soundcloud.com/player/?url=\\1" scrolling="no" frameborder="no" allowfullscreen></iframe>'
        ]
    ],
    'vimeo': [
        [
            r'(http[s]?\:\/\/(player\.)?vimeo\.com\/([\/\w]+)\/([\d]+))',
            """<iframe class="contrib-media" src="https://player.vimeo.com/video/\\4" scrolling="no" frameborder="no" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>"""
        ]
    ]
}


class MediaInput(forms.widgets.ClearableFileInput):
    template_name = 'contrib/forms/_media_input.html'
    change_message = "Changer"
    empty_message = "Changer"
    class Media:
        css = {
            'all': (
                'contrib/forms/media.css',
            )
        }
        js = (
            'contrib/packages/media.js',
            'contrib/forms/media.js',
        )


    def __init__(self, *args, **kwargs):
        self.authorized_types = []
        if kwargs.get('authorized_types'):
            self.authorized_types = kwargs.pop('authorized_types')
        super(MediaInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        # print "MediaInput.render : ", name, type(value), value, self.is_initial(value)
        if value is None:
            value = ''

        field = super(MediaInput, self).render(name, value, attrs=attrs)

        in_memory = False


        if isinstance(value, InMemoryUploadedFile):
            in_memory = True

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        checkbox_name = self.clear_checkbox_name(name)
        checkbox_id = self.clear_checkbox_id(checkbox_name)
        context = {
            'only_file': len(self.authorized_types) == 1 and 'image' in self.authorized_types,
            'required': self.is_required,
            'field': field,
            'name': name,
            'value': value,
            'id': final_attrs['id'],
            'final_attrs': flatatt(final_attrs),
            'change_message': self.change_message,
            'empty_message': self.empty_message,
            'embed_types': json.dumps(EMBED_TYPES)
        }
        if not self.is_required:
            context['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
        return render_to_string(self.template_name, Context(context))


    # def decompress(self, value):
    #     if value:
    #         return value.split(' ')
    #     return [None, None]

    def value_from_datadict(self, data, files, name):
        # print 'MediaInput.value_from_datadict : ', name, (files.get(name, None), data.get(name, None))
        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):
            return False


        if files:
            return files.get(name, None)
        else:
            return data.get(name, None)

        # return files.get(name, None), data.get(name, None)


class MediaField(forms.FileField):
    # widget = MediaInput
    default_error_messages = {
        'invalid_image': "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
    }

    def __init__(self, *args, **kwargs):

        # required = kwargs.get('required', False)
        #widget = kwargs.pop('widget', None)
        # widget = MediaInput( attrs={
        #     'class': 'contrib-media_field',
        #     # 'data-contrib-media_field': self.image_field,
        #     # 'style': 'display:none;',
        # })
        # kwargs['widget'] = widget
        # kwargs['label'] = ""

        super(MediaField, self).__init__(*args, **kwargs)


    def to_python(self, data):
        # print 'MediaFormField.to_python : ', data, type(data)
        return data

    def has_changed(self, initial, data):
        # print 'MediaFormField.has_changed:', data, type(data)
        if data is None:
            return super(MediaField, self).has_changed(initial, data)
        return True

    def bound_data(self, data, initial):
        # print 'MediaFormField.bound_data:', data, type(data), initial, type(initial)
        if data in [False, None] and initial:
            return initial
        return data

    def clean(self, data, initial=None):
        if data is False:
            if not self.required:
                return False
            data = None
        if not data and initial:
            return initial
        return super(MediaField, self).clean(data)