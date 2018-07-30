import uuid
from django.core.exceptions import ImproperlyConfigured
from django.views import generic
from django.forms import models as model_forms
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
import workon.views
import workon.utils


__all__ = ['View', 'ModalView']


class View(generic.DetailView):
    
    def get_template_names(self):
        if self.request.is_ajax():
            return getattr(self, 'ajax_template_name', 
                        getattr(self, 'template_name_ajax', 
                            getattr(self, 'xhr_template_name', 
                                getattr(self, 'template_name_xhr', 
                                    getattr(self, 'template_name')
                                )
                            )

                        )
                    )
        else:
            return self.template_name



class ModalView(View):
    pass
