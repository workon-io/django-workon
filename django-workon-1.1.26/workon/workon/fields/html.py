
# from tinymce.models import HTMLField as TinyMceHTMLField

from django.db import models
from workon.forms import HtmlInput


# class HTMLField(TinyMceHTMLField):
#     pass

class HTMLField(models.TextField):
    """
    A large string field for HTML content. It uses the TinyMCE widget in
    forms.
    """
    def __init__(self, *args, **kwargs):

        self.tinymce = kwargs.pop('tinymce', None)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):

        defaults = { 'widget': HtmlInput }
        defaults.update(kwargs)

        # As an ugly hack, we override the admin widget
        # if defaults['widget'] == admin_widgets.AdminTextareaWidget:
        #     defaults['widget'] = tinymce_widgets.AdminTinyMCE

        defaults['widget'] = HtmlInput(attrs={'placeholder': self.verbose_name}, tinymce=self.tinymce)

        return super().formfield(**defaults)

class HtmlField(HTMLField):
    pass
