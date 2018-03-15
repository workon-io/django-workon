from django.db import models
from django import forms
from django.utils.text import capfirst
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


__all__ = ['PercentField']


class PercentField(models.PositiveIntegerField):
    """
    Positive integer with percent validators
    """
    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [MaxValueValidator(100), MinValueValidator(0)]
        super().__init__(*args, **kwargs)

    # def formfield(self, **kwargs):
    #     kwargs['form_class'] = PriceFormField
    #     return super(PriceField, self).formfield(**kwargs)
