import re
import os
import logging
from django.conf import settings
from django import forms as base_forms
from django.template import Context
from django.forms.widgets import ClearableFileInput
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.forms.utils import flatatt

try:
    from sorl.thumbnail.shortcuts import get_thumbnail
except:
    def get_thumbnail(image_url, *args, **kwargs):
        return image_url

logger = logging.getLogger(__name__)

class ImageInput(ClearableFileInput):
    # template_name = 'workon/forms/clearable_file_input.html'
    attrs = {'accept': 'image/*'}


    # def get_context(self, name, value, attrs):

    #     context = super().get_context(name, value, attrs)
    #     image_url = self.format_value(value)
    #     image_original_url = None
    #     image_thumb = None
    #     if image_url:
    #         image_original_url = os.path.join(settings.MEDIA_URL, image_url.name)
    #         try:
    #             image_thumb = get_thumbnail(image_url, 'x150', crop='center', upscale=True, format='PNG')
    #         except IOError as inst:
    #             logger.error(inst)
    #     context.update({
    #         'image_thumb': image_thumb,
    #         'image_url': image_url,
    #         'image_original_url': image_original_url,
    #         'image_id': f'{attrs["id"]}-image',
    #         'name': f'{name}',
    #     })
    #     return context



# unsable ?????????????????
class ImageField(base_forms.ImageField):
    widget = ClearableFileInput
    def __init__(self, *args, **kwargs):

        widget = ImageInput
        kwargs['widget'] = widget

        super(ImageField, self).__init__(*args, **kwargs)


class CroppedImageInput(base_forms.widgets.TextInput):
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'workon/forms/image_cropped.css',
            )
        }
        js = (
            settings.STATIC_URL + 'workon/forms/image_cropped.js',
            # settings.STATIC_URL + 'js/cropper.js',
        )

class CroppedImageField(base_forms.CharField):
    widget = CroppedImageInput
    default_error_messages = {
        'invalid_image': 'Upload a valid image. The file you uploaded was either not an image or a corrupted image.',
    }
    image_field = None


    def __init__(self, *args, **kwargs):

        required = kwargs.get('required', False)
        widget = kwargs.pop('widget', None)
        self.image_field = kwargs.pop('label')

        # print widget == AdminFileWidget, isinstance(widget, AdminFileWidget), widget
        # print


        # if widget:
        # if widget == AdminFileWidget or isinstance(widget, AdminFileWidget):
        widget = CroppedImageInput( attrs={
            'class': 'image-croppable',
            'data-workon-croppedimage': self.image_field,
            'style': 'display:none;',
        })
        kwargs['widget'] = widget
        kwargs['label'] = ''

        super(CroppedImageField, self).__init__(*args, **kwargs)


    def to_python(self, data):
        return super(CroppedImageField, self).to_python(data)