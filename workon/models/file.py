from django.conf import settings
from django.db import models
from django.core.files import File
import workon


__all__ = ['File']


class File(models.Model):

    file = models.FileField("Fichier", upload_to=workon.unique_filename('file/file/%Y/%m/'))
    file_size = models.FloatField("Taille du fichier", null=True, blank=True)
    file_name = models.CharField("Nom original", max_length=254, null=True, blank=True)
    file_content_type = models.CharField("Content Type", max_length=254, null=True, blank=True)

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        if isinstance(self.file, File):
            self.file_size = self.file.size
            self.file_name = self.file.name
            self.file_content_type = self.file.content_type
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