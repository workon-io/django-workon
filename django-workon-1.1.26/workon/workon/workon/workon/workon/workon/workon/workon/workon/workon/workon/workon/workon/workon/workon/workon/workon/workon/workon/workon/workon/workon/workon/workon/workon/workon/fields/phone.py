# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.validators import validate_international_phonenumber
from phonenumber_field import formfields
from phonenumber_field.phonenumber import PhoneNumber, to_python, string_types


def validate_international_phonenumber(value):
    phone_number = to_python(value)
    if phone_number and not phone_number.is_valid():
        raise ValidationError(
            _('The phone number entered is not valid.'),
            code='invalid_phone_number')

class PhoneNumberDescriptor(object):
    """
    The descriptor for the phone number attribute on the model instance.
    Returns a PhoneNumber when accessed so you can do stuff like::
        >>> instance.phone_number.as_international
    Assigns a phone number object on assignment so you can do::
        >>> instance.phone_number = PhoneNumber(...)
    or
        >>> instance.phone_number = '+414204242'
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = to_python(value)


class PhoneNumberField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid phone number.'),
    }
    default_validators = [validate_international_phonenumber]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.input_type = 'tel'

    def to_python(self, value):
        phone_number = to_python(value)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number

class PhoneNumberField(models.Field):
    attr_class = PhoneNumber
    descriptor_class = PhoneNumberDescriptor
    default_validators = [validate_international_phonenumber]

    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 128)
        super(PhoneNumberField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))

    def get_internal_type(self):
        return "CharField"

    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        if not value:
            if not self.blank:
                return to_python(self.default)
            elif self.blank:
                return to_python(self.default) or ''

        if value != '':
            value = to_python(value)

        if isinstance(value, string_types):
            # it is an invalid phone number
            return value
        format_string = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
        fmt = PhoneNumber.format_map[format_string]
        return value.format_as(fmt)

    def contribute_to_class(self, cls, name):
        super(PhoneNumberField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, self.descriptor_class(self))

    def formfield(self, **kwargs):
        defaults = {
            'form_class': formfields.PhoneNumberField,
        }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)
