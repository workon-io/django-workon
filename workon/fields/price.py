from django.db import models
from django import forms
from django.utils.text import capfirst
from workon.forms import PriceField as PriceFormField, PriceInput


__all__ = ['PriceField']


class PriceField(models.DecimalField):
    """
    A text field made to accept hexadecimal color value (#FFFFFF)
    with a color picker widget.
    """
    def __init__(self, *args, **kwargs):
        kwargs['decimal_places'] = kwargs.get('decimal_places', 2)
        kwargs['max_digits'] = kwargs.get('max_digits', 21)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['form_class'] = PriceFormField
        return super().formfield(**kwargs)
