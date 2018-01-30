# encoding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.localflavor.fr.forms import FRZipCodeField as OriginalFRZipCodeField


class ZipCodeField(OriginalFRZipCodeField):
    default_error_messages = {
        'invalid': _(u"Enterez un code postal au format XXXXX."),
    }

    def __init__(self, max_length=5, min_length=5, *args, **kwargs):
        original_label = kwargs.get('label', _('Code postal'))
        super(ZipCodeField, self).__init__(*args, **kwargs)
        self.label = original_label