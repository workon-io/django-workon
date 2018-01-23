import datetime
from django import forms
from django.db import models
from django.views import generic
from django.shortcuts import render
from django.utils.html import mark_safe
from django.utils import six
from django.utils.text import slugify
from django.forms.fields import CallableChoiceIterator
from django.core.exceptions import FieldDoesNotExist
import workon.utils
import workon.conf


__all__ = ['ListColumn', 'ListCol', 'ListFilter', 'ListAction', 'List', 'TableList']


    









class ModelListChoiceField(forms.ModelChoiceField):

    empty_label= ''

    pass

class ListChoiceField(forms.ChoiceField):
    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        if callable(value):
            value = CallableChoiceIterator(value)
        else:
            value = list(value)
        self._choices = self.widget.choices = [('', ' -- '), ] + list(value)
    choices = property(_get_choices, _set_choices)


class ListMultipleChoiceField(forms.MultipleChoiceField):
    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        if callable(value):
            value = CallableChoiceIterator(value)
        else:
            value = list(value)
        self._choices = self.widget.choices = list(value)
    choices = property(_get_choices, _set_choices)
















class ListAction():
    def __init__(self, name, label=None, col=2):
        self.name = name
        self.meta = {
            'class': f'col s12 m{col}',
            'label': label or name,
        }










class ListFilter():
    def __init__(self, name, label=None, col=2, choices=None, classes='', multiple=False, default=None, field_class=None, field_kwargs=None):
        self.name = name
        field_kwargs = field_kwargs if field_kwargs else {}
        field_kwargs['required'] = False
        field_kwargs['initial'] = default
        if label:
            label = mark_safe(label)
        field_kwargs['label'] = label
        if not field_class:
            if choices is not None:
                if isinstance(choices, models.QuerySet):
                    field_class = ModelListChoiceField
                    field_kwargs['queryset'] = choices
                    field_kwargs['empty_label'] = ''
                else:
                    if multiple == True:
                        field_class = ListMultipleChoiceField
                    else:
                        field_class = ListChoiceField
                    field_kwargs['choices'] = choices
            else:
                field_class = forms.CharField
        self.form_field_kwargs = field_kwargs
        self.form_field_class = field_class
        self.meta = {
            'class': f'{classes}',
            'label': label or name,
        }



class ListForm(forms.Form):
    def __init__(self, filters_instances,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['page'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        for fi in filters_instances:
            field_kwargs = fi.form_field_kwargs
            self.fields[fi.name] = fi.form_field_class(**field_kwargs)
            self.fields[fi.name].meta = fi.meta





class ListColumn():
    def __init__(self, name, label=None, classes='', attrs='', ellipsis=False, col=None):
        self.name = name
        self.label = label
        self.classes = classes
        self.attrs = attrs
        self.ellipsis = ellipsis

    def __str__(self):
        return str(self.label) if self.label else ''

class ListCol(ListColumn): pass






class List(generic.FormView):

    template_name = workon.conf.LIST_TEMPLATE
    results_template_name = workon.conf.LIST_RESULTS_TEMPLATE
    row_template_name = workon.conf.LIST_ROW_TEMPLATE
    layout_template_name = workon.conf.LIST_LAYOUT_TEMPLATE

    list_id = 'filtered_list'
    list_class = ''
    filters = []
    actions = []
    columns = []
    filters_instances = []
    columns_instances = []
    form_class = None
    model = None

    def make_column_instance(self, col, **kwargs):
        if isinstance(col, ListCol):
            col = col

        elif isinstance(col, dict):
            col = ListCol(**col)

        elif isinstance(col, tuple):
            col = self.make_column_instance(col[0], label=col[-1])

        elif isinstance(col, six.string_types):
            if self.model and not 'label' in kwargs:
                try:
                    kwargs['label'] = self.model._meta.get_field(col).verbose_name
                except FieldDoesNotExist:
                    pass
            col = ListCol(col, **kwargs)
        return col

    def make_filter_instance(self, fi, **kwargs):
        if isinstance(fi, ListFilter):
            fi = fi

        elif isinstance(fi, dict):
            fi = ListFilter(**fi)

        elif isinstance(fi, tuple):
            fi = self.make_filter_instance(fi[0], label=fi[-1])

        elif isinstance(fi, six.string_types):
            name_ftype = fi.split('::', 1)
            ftype = name_ftype[-1]
            name = name_ftype[0]
            if not 'label' in kwargs:
                kwargs['label'] = name
            if len(name_ftype) == 2:
                if ftype == "int":
                    kwargs['field_class'] = forms.IntegerField
                elif ftype in ["bool", "boolean"]:
                    kwargs['field_class'] = forms.BooleanField
                elif ftype in ["date"]:
                    kwargs['field_class'] = workon.forms.DateField
                elif ftype in ["datetime"]:
                    kwargs['field_class'] = workon.forms.DateTimeField
                elif ftype in ["time"]:
                    kwargs['field_class'] = workon.forms.TimeField
            fi = ListFilter(name, **kwargs)
        return fi

    def render_cell(self, column_instance, obj):
        data = dict(
            attrs='',
            classes='',
            column=column_instance
        )
        name = column_instance.name 
        value_method = getattr(self, f'get_col_{name}_value', None)
        if value_method:
            value = value_method(obj)
        else:
            value = getattr(obj, name, None)
            if column_instance.ellipsis:
                data['attrs'] += f'data-tooltip="{value}"'
        if value is None or value is "":
            value = f'''<i class="icon disabled">block</i>'''
        elif isinstance(value, bool):
            value = f'''<i class="icon {'success' if value else 'error'}">{'check' if value else 'close'}</i>'''
        elif isinstance(value, datetime.date):
            value = value.strftime("%d %b <sup>%Y</sup> <sub>à %H:%M</sub>").replace('<sub>à 00:00</sub>', '')
        elif isinstance(value, six.string_types):
            value = value
        data['value'] = value 

        class_method = getattr(self, f'get_col_{name}_class', None)
        if class_method:
            data['classes'] += class_method(obj)

        attrs_method = getattr(self, f'get_col_{name}_attrs', None)
        if attrs_method:
            data['attrs'] += attrs_method(obj)

        # data['attrs'] = " ".join([f'{name}="{value}"' for name, value in data['attrs'].items()]) 
        return data


    def get_form(self):

        self.columns_instances = [ self.make_column_instance(fi) for fi in getattr(self, 'fields', self.columns)]
        self.filters_instances = [ self.make_filter_instance(fi) for fi in self.filters]

        if not self.form_class:
            self.form = ListForm(self.filters_instances, **self.get_form_kwargs())
        else:
            self.form = self.form_class(**self.get_form_kwargs())
        self.form_initialize(self.form)
        return self.form

    def form_initialize(self, form):
        return form
        
    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('GET'):
            kwargs.update({
                'initial': self.request.GET,
            })

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_extra_actions(self, obj):
        return ''

    def get_row_id(self, obj):
        if hasattr(obj, 'pk'):
            return f'{obj}_{obj.pk}'
        else:
            return str(obj)

    def get_row_class(self, obj):
        return ''
        
    def get_row_style(self, obj):
        return ''

    def get_row_attrs(self, obj):
        if workon.conf.LIST_ROW_UPDATE_ON_DOUBLE_CLICK:
            update_url = self.get_row_update_url(obj)
            if update_url:
                return f'''\
                            {self.get_row_update_on_double_click_method(obj)}="{update_url}" \
                            data-tooltip='{{ 
                                "content": "Double-clic pour éditer" ,
                                "position": "left" 
                            }}' '''
        return ''

    def get_row_create_url(self, obj):
        return None

    def get_row_view_method(self, obj):
        return workon.conf.LIST_ROW_VIEW_METHOD

    def get_row_view_url(self, obj):
        return getattr(obj, 'view_url', lambda: None)()

    def get_row_update_method(self, obj):
        return workon.conf.LIST_ROW_UPDATE_METHOD

    def get_row_update_url(self, obj):
        return getattr(obj, 'update_url', lambda: None)()

    def get_row_update_on_double_click_method(self, obj):
        return workon.conf.LIST_ROW_UPDATE_ON_DOUBLE_CLICK_METHOD

    def get_row_delete_method(self, obj):
        return workon.conf.LIST_ROW_DELETE_METHOD

    def get_row_delete_url(self, obj):
        return getattr(obj, 'delete_url', lambda: None)()


    def get_template_names(self):
        return self.results_template_name if self.request.is_ajax() else self.template_name

    def get_queryset(self):
        qs = []
        if getattr(self, 'model', None):
            qs = self.model.objects.all()
        return self.filter(qs, self.F)

    def filter(self, qs, filters=None):
        if hasattr(self, 'model'):
            pass
        return qs 

    def get_row_update_method(self, obj):
        return ""


    def get_rows(self):
        self.rows = []
        self.queryset = getattr(self, 'queryset', [])
        # data = getattr(self.form, 'cleaned_data', { f.name: '' for f in self.filters_instances })
        for obj in self.queryset:
            cells = []
            for column_instance in self.columns_instances:
                cells.append(self.render_cell(column_instance, obj))

            row = {
                'object': obj,
                'id': self.get_row_id(obj),
                'attrs': self.get_row_attrs(obj),
                'class': self.get_row_class(obj),
                'style': self.get_row_style(obj),
                'cells': cells,
                'update_method': self.get_row_update_method(obj),
                'delete_method': self.get_row_delete_method(obj),
                'view_method': self.get_row_view_method(obj),
                'extra_actions': self.get_extra_actions(obj),
            }
            self.rows.append(row)
        return self.rows

    def get_breadbrumbs(self):
        return []


    def form_valid(self, form):
        self.data = self.F = form.cleaned_data
        self.queryset = self.get_queryset()
        action = self.request.GET.get('_action')
        if action and hasattr(self, f'action_{action}'):
            response = getattr(self, f'action_{action}')(self.queryset)
            if not response:
                self.queryset = self.get_queryset()
            else:
                return response
        return self.render_valid(form)

    def render_valid(self, form):
        # try:
        self.queryset = workon.utils.DiggPaginator(self.queryset, 50, body=6, padding=2).get_queryset_for_page(self.data.get('page'))
        # except:
        #     self.queryset = qs
        return render(self.request, self.get_template_names(), self.get_context_data())        

    def form_invalid(self, form):
        return self.form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        create_method = getattr(self, 'get_create_method', None)
        ctx['create_method'] = create_method() if create_method else None
        create_url = getattr(self, 'get_create_url', None)
        ctx['create_url'] = create_url() if create_url else None 

        ctx['breadcrumbs'] = self.get_breadbrumbs()
        ctx['columns'] = self.columns_instances
        ctx['actions'] = self.actions
        ctx['rows'] = self.get_rows()
        ctx['list_results_template'] = self.results_template_name
        ctx['list_row_template'] = self.row_template_name
        ctx['layout_template'] = self.layout_template_name
        ctx['list_id'] = self.list_id
        ctx['list_class'] = self.list_class
        ctx['queryset'] = getattr(self, 'queryset', [])

        return ctx

class RowList(List):
    template_name = "workon/views/list/list.html"
    results_template_name = "workon/views/list/_list.html"
    row_template_name = "workon/views/list/_row.html"
    
    row_nums = 12
    row_tag = 'span'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['row_nums'] = self.row_nums
        ctx['row_tag'] = self.row_tag
        return ctx


class TableList(List):

    template_name = "workon/views/list/list.html"
    results_template_name = "workon/views/list/_list.html"
    row_template_name = "workon/views/list/_row.html"