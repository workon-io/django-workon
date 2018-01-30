import uuid
from django.core.exceptions import ImproperlyConfigured
from django.views import generic
from django.forms import models as model_forms
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
import workon.utils


__all__ = ['Save', 'ModalSave', 'JsonSave', 'SaveField']


class SaveField():
    def __init__(self, name, label=None, col=12):
        self.name = name
        self.label = label
        self.meta = {
            'class': f'col s12 m{col}',
            'label': label or name,
        }


class Save(generic.UpdateView):

    layout_template_name = "workon/save/layout.html"
    template_name = "workon/views/save/save.html"
    result_template_name = "workon/views/list/_row.html"
    fields = None
    form_classes = ''
    modal_classes = ''

    def get_form_id(self):
        return uuid.uuid1()

    # def get_form_kwargs(self):
    #     """Return the keyword arguments for instantiating the form."""
    #     kwargs = super().get_form_kwargs()
    #     if hasattr(self, 'object'):
    #         kwargs.update({'instance': self.object})
    #     return kwargs

    def get_form_class(self):

        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured("Specifying both 'fields' and 'form_class' is not permitted.")
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                model = self.object.__class__
            else:
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured("Using ModelFormMixin (base class of %s) without the 'fields' attribute is prohibited." % self.__class__.__name__)

            fields = []
            for i, field in enumerate(self.fields):
                if isinstance(field, SaveField):
                    fields.append(field.name)
                elif isinstance(field, dict):
                    self.fields[i] = field = SaveField(**field)
                    fields.append(field.name)
                else:
                    fields.append(field)
            return model_forms.modelform_factory(model, fields=fields)


    def form_initialize(self, form):
        return form

    def get_form(self, *args, **kwargs):

        self.form = super().get_form(*args, **kwargs)
        self.form_id = self.get_form_id()
        for name, field in self.form.fields.items():
            if hasattr(self, f'get_field_{name}'):
                self.form.fields[name] = getattr(self, f'get_field_{name}')()
           
        self.form_initialize(self.form)
        for field in self.form.fields.values():
            field.meta = {
                'class': f'col s12',
                'label': field.label,
            }
        for field in self.fields:
            if isinstance(field, SaveField):
                if self.form.fields.get(field.name):
                    self.form.fields[field.name].label = (field.label or self.form.fields[field.name].label).capitalize()
                    self.form.fields[field.name].meta.update(field.meta)

        return self.form

    @property
    def save_and_continue(self):
        return bool(self.request.POST.get('_save_and_continue'))

    def get_object(self, *args, **kwargs):
        if hasattr(self, '_object'):
            return getattr(self, '_object')
        self.created = False
        try:
            self.object = super().get_object()
        except AttributeError:
            self.object = self.model()
            self.created = True

        setattr(self, '_object', self.object)
        return self.object

    def get_save_url(self):
        return self.request.get_full_path()

    def render_form(self, **kwargs):
        return workon.render_content(self.request, self.template_name, self.get_context_data(**{
            'form': self.form
        }, **kwargs))

    def render_row(self, obj):
        return workon.render_content(self.request, self.result_template_name, {
            'row': {
                'object': obj,
                'id': f'{obj}_{obj.pk}'
            }
        })

    def get_success_message(self, obj):
        return f'{obj} enregistré'

    def get_valid_json(self, obj, **kwargs):
        success_message = self.get_success_message(obj)
        json = {
            'notice': {
                'content': success_message,
                'classes': 'success'
            }
        }
        if self.save_and_continue:
            form = self.get_form()
            form.instance = obj
            json['replace'] = self.render_form(**kwargs)
        else:
            messages.success(self.request, success_message)
            json['redirect'] = self.request.META['HTTP_REFERER']

        json.update(kwargs)
        return json
        # [
        #     workon.utils.render_content(self.request, self.result_template_name, {
        #         'row': {
        #             'object': obj,
        #             'id': obj
        #         }
        #     }),
        # ]

    def render_valid(self, obj, **kwargs):
        return JsonResponse(self.get_valid_json(obj, **kwargs))

    def form_valid(self, *args, **kwargs):
        self.save()
        return self.render_valid(obj)

    def save(self, *args, **kwargs):
        obj = self.form.save()

    def render_modal_title(self):
        return str(self.object)

    def render_script(self):
        return ""

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['save_url'] = self.get_save_url()
        ctx['form_classes'] = self.form_classes
        ctx['modal_classes'] = self.modal_classes
        ctx['extra_script'] = self.render_script() 
        ctx['layout_template'] = self.layout_template_name
        ctx['form_id'] = self.form_id
        ctx['title'] = self.render_modal_title()
        return ctx


class JsonSave(Save):

    def get_valid_json(self, obj, **kwargs):
        success_message = self.get_success_message(obj)
        json = {
            'notice': {
                'content': success_message,
                'classes': 'success'
            }
        }
        if self.save_and_continue:
            form = self.get_form()
            form.instance = obj
            json['replace'] = self.render_form(**kwargs)
        else:
            messages.success(self.request, success_message)
            json['redirect'] = self.request.META['HTTP_REFERER']

        json.update(kwargs)
        return json

    def render_valid(self, obj, **kwargs):
        return JsonResponse(self.get_valid_json(obj, **kwargs))

    def form_valid(self, *args, **kwargs):
        obj = self.form.save()
        return self.render_valid(obj)

class ModalSave(JsonSave):
    template_name = "workon/views/save/_modal.html"
    
    def get_valid_json(self, obj, **kwargs):
        success_message = self.get_success_message(obj)
        json = {
            'notice': {
                'content': success_message,
                'classes': 'success'
            }
        }
        if self.save_and_continue:
            form = self.get_form()
            form.instance = obj
            json['replaceModal'] = self.render_form(**kwargs)
        else:
            messages.success(self.request, success_message)
            json['redirect'] = self.request.META['HTTP_REFERER']

        json.update(kwargs)
        return json

    def render_valid(self, obj, **kwargs):
        return JsonResponse(self.get_valid_json(obj, **kwargs))
