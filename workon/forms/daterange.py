
import datetime
from django import forms
from django.utils import formats, six
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.encoding import force_str, force_text
from django.core.exceptions import ValidationError

# class DateRangeValue(object):
#     def __init__(self, start, end):
#         self.start = start
#         self.end = end

class DateRangeInput(forms.DateInput):

    def __init__(self, date_ranges, allow_custom, attrs=None, options=None, format=None):
        self.date_ranges = date_ranges
        self.allow_custom = allow_custom
        self.options = options or {}       
        self.options.update({
            'locale': {
                'format': 'DD/MM/YYYY',
                'daysOfWeek': [ "Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"  ],
                'autoApply': True,
                'autoUpdateInput': False,
                'alwaysShowCalendars': True,
                'applyLabel': "Ok",
                'cancelLabel': "Annuler",
                'fromLabel': "De",
                'toLabel': "Jusqu'a",
                'customRangeLabel': "Choisir une période >",
                'monthNames': [
                    "Janvier",
                    "Février",
                    "Mars",
                    "Avril",
                    "Mai",
                    "Juin",
                    "Juillet",
                    "Août",
                    "Septembre",
                    "Octobre",
                    "Novembre",
                    "Décembre"
                ],
                'firstDay': 1
            }
        })

        final_attrs = {'class': 'vDateField', 'size':'10'}
        if attrs is not None:
            final_attrs.update(attrs)

        # widgets = (
        #     forms.DateInput(attrs=final_attrs, format=format),
        #     forms.DateInput(attrs=final_attrs, format=format),
        #     )
        super().__init__(attrs=attrs)


    def format_value(self, values):

        if isinstance(values, six.text_type):
            value = values.strip()        
            values = value.split(' - ')
            if len(values) == 2:
                return f'{values[0]} - {values[1]}'

        if isinstance(values, list):
            # localize_input() returns str on Python 2.
            try:
                st = force_text(formats.localize_input(values[0], self.format or formats.get_format(self.format_key)[0]))
                et = force_text(formats.localize_input(values[1], self.format or formats.get_format(self.format_key)[0]))
                # print(values, f'{st} - {et}', self.format or formats.get_format(self.format_key)[0])
                return f'{st} - {et}'
            except:
                pass
        return f''



class DateRangeField(forms.DateField):

    def __init__(self, date_ranges=(), allow_custom=False, format=None, options=None, *args, **kwargs):
        
        widget = kwargs.get('widget', DateRangeInput)

        if isinstance(widget, type):
            kwargs['widget'] = widget(date_ranges, allow_custom, format=format, options=options)

        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value and isinstance(self.initial, six.text_type):
            value = self.initial

        if isinstance(value, six.text_type):
            values = value.strip().split(' - ')
            if len(values) == 2:
                return [super().to_python(values[0]), super().to_python(values[1])]

        if not self.required:
            return [None, None]

        raise ValidationError(self.error_messages['invalid'], code='invalid')

    def prepare_value(self, value):
        if not value:
            if isinstance(self.initial, six.text_type):
                return self.initial
        return value