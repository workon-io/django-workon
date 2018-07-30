import os
import uuid
import datetime
import threading

from django.utils.encoding import force_str, force_text
from django.utils.deconstruct import deconstructible

__all__ = ["UniqueFilename", "unique_filename", "sizify", "listdir", "isdir", "isfile"]

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

def sizify(value):
    """
    Simple kb/mb/gb size snippet for templates:

    {{ product.file.size|sizify }}
    """
    #value = ing(value)
    try:
        if value < 512000:
            value = value / 1024.0
            ext = 'kb'
        elif value < 4194304000:
            value = value / 1048576.0
            ext = 'mb'
        else:
            value = value / 1073741824.0
            ext = 'gb'
        return '%s %s' % (str(round(value, 2)), ext)
    except Exception as e:
        return None


def listdir(path, timeout=1):
    contents = []
    t = threading.Thread(target=lambda: contents.extend(os.listdir(path)))
    t.daemon = True  # don't delay program's exit
    t.start()
    t.join(timeout)
    if t.is_alive():
        return []
    return contents


def isdir(path, timeout=1):
    results = { 'value': False }
    t = threading.Thread(target=lambda: results.update({ 'value': os.path.isdir(path) }))
    t.daemon = True  # don't delay program's exit
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False
    return results['value']

def isfile(path, timeout=1):
    results = { 'value': False }
    t = threading.Thread(target=lambda: results.update({ 'value': os.path.isfile(path) }))
    t.daemon = True  # don't delay program's exit
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False
    return results['value']