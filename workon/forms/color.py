
import re
import os
import logging
import json

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import CharField
from django.forms.fields import RegexField
from django.template.loader import render_to_string
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class ColorField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = ColorInput(attrs={'placeholder': '#xxxxxx'})
        super(ColorField, self).__init__(*args, **kwargs)


class ColorInput(forms.widgets.TextInput):

    class Media:
        css = {
            'all': (settings.STATIC_URL + 'workon/css/colpick/colpick.css',)
        }
        js = (settings.STATIC_URL + 'workon/js/colorpicker.js',)

    input_type = 'text'

    def __init__(self, *args, **kwargs):

        options = kwargs.pop('options', {})
        super(ColorInput, self).__init__(*args, **kwargs)

        attrs = {
            'data-colorpicker-input': json.dumps(options),
            #'style': 'border-right: 30px solid black'
        }
        self.attrs.update(attrs)

    def render_script(self, id):
        return ""
        # return '''<script type="text/javascript">

        #             $('#%(id)s').on('mousedown', function() {
        #                 if(!this.colpick) {
        #                     $(this).colpick({
        #                         layout: 'hex',
        #                         submit: 0,
        #                         livePreview: false,
        #                         onChange: function(hsb,hex,rgb,el,bySetColor) {
        #                             $(el).css('border-right-color','#'+hex);
        #                             if(!bySetColor) $(el).val('#'+hex);
        #                             $(el).trigger('change')
        #                         }
        #                     }).keyup(function(){
        #                         $(this).colpickSetColor(this.value.replace('#', ''));
        #                     });
        #                     this.colpick = true;
        #                 }
        #             }).on('mouseup', function() {
        #                 $(this).trigger('change')
        #             });
        #             $('#%(id)s').bind('inview', function() {
        #                 $(this).css('border-right-color',$(this).val());
        #             }).css('border-right-color',$('#%(id)s').val());
        #         </script>
        #         ''' % { 'id' : id }


    def render(self, name, value, attrs={}):
        if 'id' not in attrs:
            attrs['id'] = "id_%s" % name
        attrs['style'] = 'border-bottom: 5px solid %s' % (value if value else '#000')
        render = super(ColorInput, self).render(name, value, attrs)
        return mark_safe("%s%s" % (render, self.render_script(attrs['id'])))








RGB_REGEX = re.compile('^#?((?:[0-F]{3}){1,2})$', re.IGNORECASE)
class RGBColorField(CharField):
    widget = ColorInput
    default_validators = [RegexValidator(regex=RGB_REGEX)]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(RGBColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
            'form_class': RegexField,
            'widget': self.widget,
            'regex': RGB_REGEX
        })
        return super(RGBColorField, self).formfield(**kwargs)

    def south_field_triple(self):
        return 'libs.forms.fields.color.RGBColorField', [], {}

    def deconstruct(self):
        name, path, args, kwargs = super(RGBColorField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^libs\.forms\.fields\.color\.RGBColorField"])
except ImportError:
    pass
