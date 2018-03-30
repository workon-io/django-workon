import json
import re
import os
from urllib.parse import urlparse, urlencode, parse_qs, urlsplit, urlunsplit
from django.conf import settings
from django import template, forms
from django.templatetags.static import static
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.templatetags.static import StaticNode, static as original_static, do_static as original_do_static
from django.core.files.storage import get_storage_class, FileSystemStorage
from django import forms
import workon.utils


__all__ = ['lazy_register']


def lazy_register(register):


    @register.simple_tag
    def field(field, **kwargs):
        return render_field(field, **kwargs)

    @register.simple_tag
    def form(form, **kwargs):
        return render_form(form, **kwargs)

    def add_input_classes(field, **kwargs):

        label = kwargs.get('label', field.label)
        if label == False:
            label = None
        placeholder = kwargs.pop('placeholder', None)
        if placeholder == True:
            placeholder = field.label

        widget_classes = f"field field_{field.name} {kwargs.pop('classes', '')}"

        if not is_checkbox(field) and not is_multiple_checkbox(field) and not is_radio(field) \
            and not is_file(field):
            classes = ""
            if is_textarea(field):
                classes = "materialize-textarea"
            field_classes = field.field.widget.attrs.get('class', classes)
            if field.errors:
                field_classes+= ' invalid'
            field.field.widget.attrs['class'] = field_classes

            if hasattr(field.field, 'max_length'):
                field.field.widget.attrs['data-length'] = field.field.max_length

        if hasattr(field.field.widget, 'clear_checkbox_label'):
            field.checkbox_name = field.field.widget.clear_checkbox_name(field.name)
            field.checkbox_id = field.field.widget.clear_checkbox_id(field.checkbox_name)

        if is_select(field):
            field.field.widget.attrs['data-select'] = '-'

        if placeholder and not label:
            field.field.widget.attrs['placeholder'] = placeholder
            # field.field.widget.attrs['data-tooltip'] = placeholder

        for name, value in kwargs.items():
            field.field.widget.attrs[name] = value

        field.real_value = field.value()

        if field.errors:
            widget_classes += ' field-error'

        field.label = label
        field.classes = widget_classes
        field.error_classes = "field-error"
        field.help_classes = "field-help"
        field.label_classes = "field-label"
        template_name = f'workon/forms/fields/_{field.field.widget.__class__.__name__.lower()}.html'
        try:
            field.template = get_template(template_name)
            if settings.DEBUG:
                print(f"WO FIELD TPL for {field.name}: {template_name}")
        except:
            if settings.DEBUG:
                print(f"WO FIELD TPL for {field.name}: {template_name}")
            field.template = get_template('workon/forms/fields/_unknow.html')




    def render_field(field, **kwargs):
        element_type = field.__class__.__name__.lower()
        if element_type == 'boundfield':
            add_input_classes(field, **kwargs)
            kwargs['field'] = field
            return field.template.render(kwargs)

    def render_form(form, **kwargs):
        html = ''
        for field in form:
            html += render_field(field)
        return mark_safe(html)

    def form_as_app(self):
        return render_form(self)

    forms.Form.as_app = form_as_app

    @register.filter
    def is_checkbox(field):
        return isinstance(field.field.widget, forms.CheckboxInput)

    @register.filter
    def is_textarea(field):
        return isinstance(field.field.widget, forms.Textarea)


    @register.filter
    def is_multiple_checkbox(field):
        return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


    @register.filter
    def is_radio(field):
        return isinstance(field.field.widget, forms.RadioSelect)

    @register.filter
    def is_date_input(field):
        return isinstance(field.field.widget, forms.DateInput)


    @register.filter
    def is_file(field):
        return isinstance(field.field.widget, forms.FileInput) or \
                isinstance(field.field.widget, forms.FileInput)


    @register.filter
    def is_select(field):
        return isinstance(field.field.widget, forms.Select)


    @register.filter
    def is_checkbox_select_multiple(field):
        return isinstance(field.field.widget, forms.CheckboxSelectMultiple)

