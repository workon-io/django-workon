from django.db import models
from workon.forms.tree import TreeModelChoiceField

class TreeManyToManyField(models.ManyToManyField):

    def formfield(self, **kwargs):
        defaults = {
            'form_class': TreeModelChoiceField
        }
        return super().formfield(**defaults)

class TreeForeignKey(models.ForeignKey):

    def formfield(self, **kwargs):
        # defaults = {
        #     'form_class': TreeModelChoiceField
        # }
        return super().formfield(**kwargs)