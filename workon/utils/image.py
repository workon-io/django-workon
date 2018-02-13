import os, datetime, re, base64, uuid, urllib
from io import StringIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import get_storage_class
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles import finders
from django.templatetags.static import static 


__all__ = ["base64image_iter", "thumbnail", "thumbnail_static", "static"]


base64img_finder = re.compile(r'(data\:image\/(\w+)\;base64\,([\w\+\/\d\=\n]+))')

def base64image_iter(text, uploaded_file=False):

    for m in base64img_finder.finditer(text):

        src = m.group(1)
        image_type = m.group(2).lower()
        base64img = m.group(3)
        if image_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico']:
            image = base64.decodestring(bytes(base64img, 'utf-8'))
            if uploaded_file:
                image = SimpleUploadedFile('%s.png' % str(uuid.uuid4()), image, content_type='image/%s' % image_type)
            yield src, image


class SafeStaticFilesStorage(get_storage_class(settings.STATICFILES_STORAGE)):
    def path(self, name):
        return os.path.join(self.location, name)



def thumbnail(*args, **options):
    from sorl.thumbnail.shortcuts import get_thumbnail
    return get_thumbnail(*args, **options)


def thumbnail_static(file_, geometry, **options):
    from sorl.thumbnail.shortcuts import get_thumbnail
    from sorl.thumbnail.images import ImageFile, DummyImageFile

    storage = SafeStaticFilesStorage()
    try:
        file_ = ImageFile(staticfiles_storage.open(file_))
    except:
        absolute_path = finders.find(file_)
        if not absolute_path:
            raise Exception(f'{file_} not found.')
        file_ = ImageFile(open(absolute_path))
    file_.storage = storage
    return get_thumbnail(file_, geometry, **options)
