from django import forms
from django.forms import SelectMultiple
try:
    from django.contrib.postgres.fields import ArrayField
except ImportError:
    
    class ArrayField(object):
        pass


__all__ = ['ArrayField', 'ArrayChoiceField']


class ArraySelectMultiple(SelectMultiple):

    def value_omitted_from_data(self, data, files, name):
        return False

 
class ArrayChoiceField(ArrayField):
    """
    A field that allows us to store an array of choices.
     
    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.
    """
 
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.TypedMultipleChoiceField,
            'choices': self.base_field.choices,
            'coerce': self.base_field.to_python,
            'widget': ArraySelectMultiple
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(workon.ArrayField, self).formfield(**defaults)