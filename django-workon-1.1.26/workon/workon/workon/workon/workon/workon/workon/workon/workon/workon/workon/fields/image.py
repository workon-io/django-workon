import re
import os
from PIL import Image
from io import StringIO
from django import forms
from django.db.models import ImageField as BaseImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile

from workon.forms import CroppedImageField as CroppedImageFormField
from workon.forms import ImageField as ImageFormField, ImageInput

IMAGE_FIELD_DELIMITER = "?"


__all__ = ['ImageField', 'CroppedImageField']


class CroppedImageFieldFile(ImageFieldFile):

    stashed_name = None

    def __init__(self, instance, field, name):

        if not hasattr(instance, field.name + '_stashed_name'):
            setattr(instance, field.name + '_stashed_name', name)
        self.stashed_name = getattr(instance, field.name + '_stashed_name')
        super().__init__( instance, field, name)

    def get_origial_file(self):
        return getattr(self.instance, self.field.image_field, None)

    def save(self, coords, original_file, instance, image_field, save=True):

        coords = coords.split('?')[-1]

        if re.search(r"\d+_\d+_\d+_\d+", coords):

            file_name, file_ext = os.path.splitext(original_file.name)
            if file_ext in ['.jpg', '.jpeg']:
                FTYPE = 'JPEG'
            elif file_ext == '.gif':
                FTYPE = 'GIF'
            elif file_ext == '.png':
                FTYPE = 'PNG'
            else:
                FTYPE = 'PNG'

            if self.stashed_name:
                self.storage.delete(self.stashed_name)
            cropped_filename = IMAGE_FIELD_DELIMITER.join([original_file.name, coords])

            o_coords = coords.split('_')
            if len(o_coords) == 4:
                x, y, w, h = map(int, o_coords)
                try:
                    original_im = Image.open(self.storage.open(original_file.name, 'r'))
                    cropped_im_tmp = StringIO()
                    cropped_im = original_im.crop((x, y, x+w, y+h))
                    cropped_im.save(cropped_im_tmp, FTYPE)
                    cropped_im_tmp.seek(0)

                    self.storage.save(cropped_filename, ContentFile(cropped_im_tmp.read()))
                    cropped_im_tmp.close()
                except:
                    pass

            self.filename = cropped_filename
            self.name = cropped_filename#cropped_filename
            setattr(self.instance, self.field.name, cropped_filename)

        else:
            cropped_filename = original_file.name
            self.filename = cropped_filename
            self.name = cropped_filename#cropped_filename
            setattr(self.instance, self.field.name, cropped_filename)

        if save:
            self.instance.save()



class CroppedImageField(BaseImageField):
    attr_class = CroppedImageFieldFile
    image_field = None

    def __init__(self, *args, **kwargs):
        if kwargs.get('original'):
            self.image_field = kwargs.pop('original')
        if kwargs.get('image_field'):
            self.image_field = kwargs.pop('image_field')

        kwargs['max_length'] = 255

        super().__init__(*args, **kwargs)


        # override this to allow saves even if the image file doesn't change (to update crop coordinates)
    def pre_save(self, model_instance, add):
        original_file = getattr(model_instance, self.image_field)#self.attname)
        cropped_file = getattr(model_instance, self.attname)
        coords = cropped_file.name
        if original_file and cropped_file:
            # cropped_file.delete()
            # self.storage.delete(cropped_file.stashed_name)

            cropped_file.save(coords, original_file, instance=model_instance, image_field=self.image_field, save=False)
        return cropped_file.name



    def formfield(self, **kwargs):
        defaults = {
            'form_class': CroppedImageFormField,
            'label': self.image_field
            # 'widget' : forms.widgets.HiddenInput(attrs={
            #     'class': 'image-ratio',
            # })
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)



class ImageField(BaseImageField):
    def formfield(self, **kwargs):
        kwargs['form_class'] = ImageFormField
        kwargs['widget'] = ImageInput
        return super().formfield(**kwargs)
