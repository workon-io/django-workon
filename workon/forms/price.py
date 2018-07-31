import os
import logging
import locale
import json
from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import flatatt
from decimal import *

try:
    from babel.numbers import format_number, format_decimal, format_percent
except:
    def format_number(value, **kwargs):
        return locale.currency(value)
        
    def format_decimal(value, **kwargs):
        return locale.currency(value)

    def format_percent(value, **kwargs):
        return locale.currency(value)



DEFAULT_CURRENCY = 'EUR'
# Send in data way to assets/js/input_format.js
CURRENCY_PATTERNS = {
    'EUR': { 'format': u'%s €', 'locale': 'fr_FR', 'spacing': ' ', 'decimal': ',', 'placeholder': 'EUR' },
    'USD': { 'format': u'$%s', 'locale': 'en_US', 'spacing': ',', 'decimal': '.', 'placeholder': 'USD' },
}

def price_format_decimal_to_currency(value, currency='EUR'):
    if value:
        try:
            if currency in CURRENCY_PATTERNS.keys():
                value = CURRENCY_PATTERNS[currency]['format'] % format_number(value, locale = CURRENCY_PATTERNS[currency]['locale'])
            else:
                return value
        except:
            return value
    return value

def price_format_currency_to_decimal(value, currency='EUR'):
    if value == None:
        return None
    value = str(value)
    if value.strip() == '':
        return None

    float_value = ""
    float_lock = False
    for c in value[::-1]:
        if c.isdigit():
            float_value += c
        if not float_lock and (c == '.' or c == ','):
            float_value += '.'
            float_lock = True

    try:
        return float(float_value[::-1]);
    except:
        return None


# In relation to assets/js/input_format.js
class PriceField(forms.DecimalField):

    currency = DEFAULT_CURRENCY

    def __init__(self, *args, **kwargs):
        self.currency = kwargs['currency'] = kwargs['currency'] if 'currency' in kwargs else self.currency
        del kwargs['currency']

        if 'widget' not in kwargs:
            kwargs['widget'] = PriceWidget(
                currency=self.currency,
                attrs={
                    'placeholder': self.currency,
                    'data-price-widget': '1',
                    'data-currency': self.currency,
                    'data-currency-patterns': json.dumps(CURRENCY_PATTERNS)
                })
        super(PriceField, self).__init__(*args, **kwargs)

    default_error_messages = {
        'invalid': 'This is not a decimal.',
    }
    def to_python(self, value):
        # if not value.isdigit():
        #     raise ValidationError(self.error_messages['invalid'])

        float_value = price_format_currency_to_decimal(value, self.currency)
        # print super(PriceField, self).to_python(float_value)
        return super(PriceField, self).to_python(float_value)


class PriceWidget(forms.widgets.TextInput):

    class Media:
        # css = {
        #     'all': ('pretty.css',)
        # }
        js = ('contrib/forms/price.js', )

    currency = DEFAULT_CURRENCY

    def __init__(self, *args, **kwargs):
        if 'currency' in kwargs:
            self.currency = kwargs['currency']
            del kwargs['currency']
        attrs = {
            'placeholder': self.currency,
            'data-price-widget': 'price-formated',
            'data-currency': self.currency,
            'data-currency-patterns': json.dumps(CURRENCY_PATTERNS)
        }
        attrs.update(kwargs.get('attrs', {}))
        kwargs['attrs'] = attrs
        super(PriceWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = price_format_decimal_to_currency(value, self.currency)
        return super(PriceWidget, self).render(name, value, attrs)

    # def _has_changed(self, initial, data):
    #     return super(PriceWidget, self)._has_changed(self._format_value(initial), data)

class PriceInput(PriceWidget):
    pass