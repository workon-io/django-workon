from django.db import models
from workon.forms.tree import TreeModelChoiceField, TreeModelMultipleChoiceField

__all__ = ['TreeManyToManyField', 'TreeForeignKey']

class TreeManyToManyField(models.ManyToManyField):

    def formfield(self, **kwargs):
        kwargs.update({
            'form_class': TreeModelMultipleChoiceField
        })
        return super().formfield(**kwargs)

class TreeForeignKey(models.ForeignKey):

    def formfield(self, **kwargs):
        kwargs.update({
            'form_class': TreeModelChoiceField
        })
        return super().formfield(**kwargs)