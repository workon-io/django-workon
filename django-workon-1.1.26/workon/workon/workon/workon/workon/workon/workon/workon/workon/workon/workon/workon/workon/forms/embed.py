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


class EmbedInput(forms.widgets.Textarea):

    def __init__(self, *args, **kwargs):
        self.authorized_types = []
        if kwargs.get('authorized_types'):
            self.authorized_types = kwargs.pop('authorized_types')
        super().__init__(*args, **kwargs)


class EmbedField(forms.CharField):
    # widget = EmbedInput
    default_error_messages = {
        'invalid_image': "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
    }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)