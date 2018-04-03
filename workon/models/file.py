from django.conf import settings
from django.db import models
from django.core.files import File
import workon


__all__ = ['File']


class File(models.Model):

    file = models.FileField("Fichier", upload_to=workon.unique_filename('file/file/%Y/%m/'))
    file_size = models.FloatField("Taille du fichier", null=True, blank=True)
    file_name = models.CharField("Nom original", max_length=254, null=True, blank=True)
    file_field_name = models.CharField("Nom original champ", max_length=254, null=True, blank=True)
    file_charset = models.CharField("Charset", max_length=254, null=True, blank=True)
    file_content_type = models.CharField("Content Type", max_length=254, null=True, blank=True)
    file_content_type_extra = workon.JSONField("Content Type Extra", max_length=254, null=True, blank=True)

    class Meta:
        abstract = True

    # {'file': <_io.BytesIO object at 0x7fc2febced00>, '_name': 'fitneo.png', '_size': 5122, 'content_type': 'image/png', 'charset': None, 'content_type_extra': {}, 'field_name': 'file'}

    def save(self, *args, **kwargs):
        _file = getattr(self.file, '_file', None)
        if _file:            
            self.file_size = getattr(_file, '_size', self.file_size)
            self.file_name = getattr(_file, '_name', self.file_name)
            self.file_charset = getattr(_file, 'charset', self.file_charset)
            self.file_field_name = getattr(_file, 'field_name', self.file_field_name)
            self.file_content_type = getattr(_file, 'content_type', self.file_content_type)
            self.file_content_type_extra = getattr(_file, 'content_type_extra', self.file_content_type_extra)
        super().save(*args, **kwargs)


    def is_image(self, **kwargs):
        return self.file_content_type in ['image/rgb', 'image/gif', 'image/pbm', 'image/pgm', 'image/ppm',
            'image/tiff', 'image/rast', 'image/xbm', 'image/jpeg', 'image/bmp', 'image/png', 'image/x-icon']


    def is_zip(self, **kwargs):
        return self.file_content_type in ['application/zip']

    def is_pdf(self, **kwargs):
        return self.file_content_type in ['application/pdf']

    def is_powerpoint(self, **kwargs):
        return self.file_content_type in ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                                            'application/vnd.openxmlformats-officedocument.presentationml.slideshow']

    def is_word(self, **kwargs):
        return self.file_content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                            'application/vnd.ms-excel', 'vnd.ms-word.document']

    def is_zip(self, **kwargs):
        return self.file_content_type in ['application/zip']

    def is_video(self, **kwargs):
        return self.file_content_type in ['video/webm']