
# from tinymce.models import HTMLField as TinyMceHTMLField

from django.db import models
from workon.forms import (
    DateTimeField as DateTimeFormField,
    DateField as DateFormField,
    TimeField as TimeFormField,
    DateInput,
    DateTimeInput,
    TimeInput
)

class DateTimeField(models.DateTimeField):
    """
    A large string field for HTML content. It uses the TinyMCE widget in
    forms.
    """

    def formfield(self, *args, **kwargs):
        kwargs['form_class'] = DateTimeFormField
        #kwargs['widget'] = DateTimeFormField

        return super().formfield(*args, **kwargs)


class DateField(models.DateField):


    def formfield(self, *args, **kwargs):
        kwargs['form_class'] = DateFormField
        # kwargs['widget'] = DateInput

        return super().formfield(*args, **kwargs)

class TimeField(models.TimeField):


    def formfield(self, *args, **kwargs):
        kwargs['form_class'] = TimeFormField
        # kwargs['widget'] = DateInput

        return super().formfield(*args, **kwargs)
