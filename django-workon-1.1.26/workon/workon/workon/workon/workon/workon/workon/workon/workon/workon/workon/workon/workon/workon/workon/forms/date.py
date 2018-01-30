# encoding: utf-8

import json
import datetime
import time
import re
import os
import logging

from django import forms
from django.core.validators import EMPTY_VALUES
from django.template import Context
from django.forms.widgets import FileInput as OriginalFileInput
from django.template.loader import render_to_string
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils import datetime_safe, formats, six
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

logger = logging.getLogger(__name__)


class DateField(forms.DateField):

    default_error_messages = {
        'invalid': _('Enter a valid date.'),
    }

    def __init__(self, *args, **kwargs):

        # self.input_formats = formats.get_format('DATE_INPUT_FORMATS')
        if 'widget' not in kwargs:
            kwargs['widget'] = DateInput(
                # format="%d/%m/%Y",
                attrs={'placeholder': 'jj/mm/aaaa'})
            # kwargs['input_formats'] = ['%m/%d/%Y']
        super().__init__(*args, **kwargs)


class DateTimeField(forms.DateTimeField):

    def __init__(self, *args, **kwargs):
        # self.input_formats = formats.get_format('DATETIME_INPUT_FORMATS')

        if 'widget' not in kwargs:
            kwargs['widget'] = DateTimeInput(
                # format="%d/%m/%Y %H:%M:%S",
                attrs={'placeholder': 'jj/mm/aaaa'})
            #kwargs['input_formats'] = ['%d/%m/%Y %H:%M']
        super().__init__(*args, **kwargs)

class TimeField(forms.DateTimeField):

    def __init__(self, *args, **kwargs):
        # self.input_formats = formats.get_format('TIME_INPUT_FORMATS')
        if 'widget' not in kwargs:
            kwargs['widget'] = TimeInput(
                # format="%d/%m/%Y %H:%M:%S",
                attrs={'placeholder': 'hh:mm'})
            #kwargs['input_formats'] = ['%d/%m/%Y %H:%M']
        super().__init__(*args, **kwargs)

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

        # if self.datepicker and not self.timepicker:
        #     kwargs['format'] = '%d/%m/%Y'
        # elif not self.datepicker and self.timepicker:
        #     kwargs['format'] = '%H:%M'
        # else:
        #     kwargs['format'] = '%d/%m/%Y %H:%M'

        options = kwargs.pop('options', {
            'lang': 'fr',
            'timepicker': self.timepicker,
            'datepicker': self.datepicker,
            'mask': False,
            'format': ('%s %s' % (
                'd/m/Y' if self.datepicker else ' ',
                'H:i' if self.timepicker else ' ',
            )).strip()
            #'format': 'd.m.Y'
        })
        super().__init__(*args, **kwargs)


        attrs = {
            'data-datetime-widget': json.dumps(options),
            'type': 'text'
        }
        self.attrs.update(attrs)



    def render(self, name, value, attrs={}):
        # print value
        # if value:
        #     if isinstance(value, six.string_types):
        #         value = datetime.datetime.strptime(value, self.format)

        #     if isinstance(value, datetime.datetime) or isinstance(value, datetime.time) or isinstance(value, datetime.date):
        #         value = value.strftime(self.format).strip()
        # # print value

        if 'id' not in attrs:
            attrs['id'] = "id_%s" % name
        render = super(BaseDateInput, self).render(name, value, attrs)
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