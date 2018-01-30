from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.admin import widgets as admin_widgets
from django.forms.utils import flatatt
from django.utils.html import strip_tags
from django.utils.html import escape
from django.template import Context
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext as _
import json
try:
    from django.utils.encoding import smart_text as smart_unicode
except ImportError:
    try:
        from django.utils.encoding import smart_unicode
    except ImportError:
        from django.forms.util import smart_unicode


class CodeField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(CodeField, self).__init__(*args, **kwargs)


class CodeInput(forms.Textarea):


    def __init__(self, *args, **kwargs):
        self.mode = kwargs.get('attrs', {}).get('mode', 'python')
        super().__init__(*args, **kwargs)

    def render_script(self, id):
        return u'''
                <div id="%(id)s_ace_editor"></div>
                <script type="text/javascript">
                    var %(id)s_ed = ace.edit("%(id)s_ace_editor");
                    %(id)s_ed.setTheme("ace/theme/monokai");
                    %(id)s_ed.getSession().setMode("ace/mode/%(mode)s");
                    //%(id)s_ed.setPrintMarginColumn(150)
                    %(id)s_ed.setOptions({
                        maxLines: Infinity
                    });
                    %(id)s_ed.on("change", function(e) {
                        $('#%(id)s').val(%(id)s_ed.getValue());
                    });
                    %(id)s_ed.setValue($('#%(id)s').val());
                    %(id)s_ed.resize();

                </script>
                ''' % { 'id' : id.replace('-', '_'), 'mode': self.mode }


    def render(self, name, value, attrs={}):
        if 'id' not in attrs:
            attrs['id'] = "id_%s" % name
        attrs['style'] = "display:none;"
        render = super().render(name, value, attrs)
        return mark_safe("%s%s" % (render, self.render_script(attrs['id'])))