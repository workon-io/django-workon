import json
import datetime
import time
import re
import os
import logging
import warnings
from functools import reduce
from django import forms
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.template import Context
from django.forms.widgets import FileInput as OriginalFileInput
from django.template.loader import render_to_string
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils import datetime_safe, formats, six, translation
from django.utils.translation import ugettext_lazy as _, ungettext_lazy


__all__ = [
    'DateField', 
    'DateTimeField', 
    'TimeField', 
    'DateTimeInput', 
    'DateInput', 
    'TimeInput'
]


class DateField(forms.DateField):

    default_error_messages = {
        'invalid': _('Enter a valid date.'),
    }

    def __init__(self, *args, **kwargs):

        # self.input_formats = formats.get_format('DATE_INPUT_FORMATS')
        if 'widget' not in kwargs:
            kwargs['widget'] = DateInput(
                # format="%d/%m/%Y",
                attrs={'placeholder': _('jj/mm/aaaa')})
            # kwargs['input_formats'] = ['%m/%d/%Y']
        super().__init__(*args, **kwargs)


class DateTimeField(forms.DateTimeField):

    def __init__(self, *args, **kwargs):
        # self.input_formats = formats.get_format('DATETIME_INPUT_FORMATS')

        if 'widget' not in kwargs:
            kwargs['widget'] = DateTimeInput(
                # format="%d/%m/%Y %H:%M:%S",
                attrs={'placeholder': _('jj/mm/aaaa')})
            #kwargs['input_formats'] = ['%d/%m/%Y %H:%M']
        super().__init__(*args, **kwargs)

class TimeField(forms.DateTimeField):

    def __init__(self, *args, **kwargs):
        # self.input_formats = formats.get_format('TIME_INPUT_FORMATS')
        if 'widget' not in kwargs:
            kwargs['widget'] = TimeInput(
                # format="%d/%m/%Y %H:%M:%S",
                attrs={'placeholder': _('hh:mm')})
            #kwargs['input_formats'] = ['%d/%m/%Y %H:%M']
        super().__init__(*args, **kwargs)



FORMAT_MAP = {
    'd': r'%d',
    'm': r'%m',
    'Y': r'%Y',
    'H': r'%H',
    'i': r'%M',
    's': r'%S'
}
# FORMAT_MAP_REVERSE = {v:k for k,v in FORMAT_MAP.items()}

def _py_datetime_format_to_js(format_string):
    return (
        format_string is not None and
        reduce(
            lambda format_string, args: format_string.replace(*reversed(args)),
            FORMAT_MAP.items(),
            format_string
        ) or
        None
    )


def _js_datetime_format_to_py(format_string):
    return (
        format_string is not None and
        reduce(
            lambda format_string, args: format_string.replace(*args),
            FORMAT_MAP.items(),
            format_string
        ) or
        None
    )

class BaseDateInput(forms.DateTimeInput):
    # Build a widget which uses the locale datetime format but without seconds.
    # We also use data attributes to pass these formats to the JS datepicker.

    timepicker = False
    # class Media:
    #     css = {
    #         'all': ('contrib/vendors/datetimepicker/jquery.datetimepicker.css',)
    #     }
    #     js = ('contrib/vendors/datetimepicker/jquery.datetimepicker.js',)

    input_type = 'text'
    # @property
    # def media(self):
    #     return forms.Media(
    #         # js=[
    #         #     # 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.13.0/locale/fr.js',
    #         #     'contrib/packages/datetime.js'
    #         # ],
    #         # css={'all': ["contrib/vendors/datetimepicker/jquery.datetimepicker.css"]}
    #     )

    def __init__(self, *args, **kwargs):

        include_seconds = kwargs.pop('include_seconds', False)
        datetime = kwargs.get('attrs', {}).get('datetime', None)
        options = kwargs.pop('options', {
            'lang': translation.get_language(),
            'timepicker': self.timepicker,
            'datepicker': self.datepicker,
            'mask': False
        })
        formats_set = {
            datetime and _js_datetime_format_to_py(datetime) or None,
            kwargs.get('format_string', None),
            options.get('format')
        } - {None}  # and this is why (*)
        if len(formats_set) is 0:
            self.format_string =  formats.get_format(self.format_key)[0]
        elif len(formats_set) is 1:
            self.format_string = formats_set.pop()
        else:
            self.format_string = formats_set.pop()
            warnings.warn('format is set more than once', UserWarning)

        self.format_py = _js_datetime_format_to_py(self.format_string)
        self.format_js = _py_datetime_format_to_js(self.format_string)

        if self.format_string:
            options.update({'format': self.format_js})
        options.update({'language': translation.get_language()})

        super().__init__(*args, **kwargs)
        attrs = {
            'data-datetime-widget': json.dumps(options),
            'type': 'text',
            'autocomplete': 'off'
        }
        self.attrs.update(attrs)

    def format_value(self, value):
        return formats.localize_input(value, self.format_string)

    def render(self, name, value, attrs={}, **kwargs):
        renderer = kwargs.get('renderer', None)
        if 'id' not in attrs:
            attrs['id'] = "id_%s" % name
        render = super(BaseDateInput, self).render(name, value, attrs, **kwargs)
        return mark_safe("%s" % (render))


class DateInput(BaseDateInput):
    timepicker = False
    datepicker = True
    format_key = 'DATE_INPUT_FORMATS'


class DateTimeInput(BaseDateInput):
    timepicker = True
    datepicker = True
    format_key = 'DATETIME_INPUT_FORMATS'

class TimeInput(BaseDateInput):
    timepicker = True
    datepicker = False
    format_key = 'TIME_INPUT_FORMATS'