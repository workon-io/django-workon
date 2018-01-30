from django import forms
from django.db.models import CharField

class InfoField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = InfoInput(
                text=kwargs.pop('text', ""),
            )
        super(InfoField, self).__init__(*args, **kwargs)


class InfoInput(forms.widgets.HiddenInput):

    def __init__(self, *args, **kwargs):
        self.text = kwargs.pop('text', "")
        super(InfoInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        if 'id' not in attrs:
            attrs['id'] = "id_%s" % name
        return '''<div id="%(id)s" >%(value)s</div>
                ''' % {
                    'id' : attrs['id'],
                    'value': value,
                    'text': self.text,
                 }
