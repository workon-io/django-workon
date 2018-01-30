import re
import os
import logging
import locale
import json
import datetime, time


from django import forms
from django.conf import settings
from django.db.models import CharField
from django.core.exceptions import ValidationError
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class BusinessHoursField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = BusinessHoursInput(
                expanded=kwargs.pop('expanded', False),
            )
        super().__init__(*args, **kwargs)



class BusinessHoursInput(forms.widgets.TextInput):

    class Media:
        css = {
            'all': (settings.STATIC_URL + 'contrib/vendors/pretty-json/pretty-json.css',)
        }
        js = (settings.STATIC_URL + 'contrib/packages/json.js',)


    def __init__(self, *args, **kwargs):
        self.expanded = kwargs.pop('expanded', False)
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        if 'id' not in attrs:
            attrs['id'] = "id_%s" % name

        obj = json.dumps(value, ensure_ascii=False)


        return '''<div id="%(id)s" ></div><script type="text/javascript">

                    var node = new PrettyJSON.view.Node({
                        el: $('#%(id)s'),
                        data: JSON.parse(%(obj)s),
                    });
                    %(expandAll)s
                </script>
                ''' % {
                    'id' : attrs['id'],
                    'obj': obj,
                    'expandAll': 'node.expandAll();' if self.expanded else '',
                 }
