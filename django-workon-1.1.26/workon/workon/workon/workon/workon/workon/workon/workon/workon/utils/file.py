import os, uuid, datetime

from django.utils.encoding import force_str, force_text
from django.utils.deconstruct import deconstructible

__all__ = ["UniqueFilename", "unique_filename"]

@deconstructible
class UniqueFilename(object):
    path = "example/{0}/{1}{2}"

    def __init__(self, sub_path, original_filename_field=None):
        self.sub_path = sub_path
        self.original_filename_field = original_filename_field

    def __call__(self, instance, filename):
        if self.original_filename_field and hasattr(instance, self.original_filename_field):
            setattr(instance, self.original_filename_field, filename)
        parts = filename.split('.')
        extension = parts[-1]
        directory_path = os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.sub_path))))
        unique_name = u"{0}.{1}".format(uuid.uuid4(), extension)
        return os.path.join(directory_path, unique_name)

# retro compatibility for older uses as function
class unique_filename(UniqueFilename):
    pass