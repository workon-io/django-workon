import os
import uuid
import datetime
import colorsys
import random
import hashlib

from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_str, force_text
from django.utils.deconstruct import deconstructible


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 52428800
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 5242880)

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data




@deconstructible
class UniqueFilename(object):
    path = "students/{0}/{1}{2}"

    def __init__(self, sub_path, original_filename_field=None):
        self.sub_path = sub_path
        self.original_filename_field = original_filename_field

    def __call__(self, instance, filename):
        if self.original_filename_field and hasattr(instance, self.original_filename_field):
            setattr(instance, self.original_filename_field, filename)
        parts = filename.split('.')
        extension = parts[-1]
        directory_path = os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.sub_path))))
        unique_name = "{0}.{1}".format(uuid.uuid4(), extension)
        return os.path.join(directory_path, unique_name)

# retro compatibility for older uses as function
class unique_filename(UniqueFilename):
    pass