import uuid
from django.core.exceptions import ImproperlyConfigured
from django.views import generic
from django.forms import models as model_forms
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
import workon.utils


__all__ = ['View', 'ModalView']


class View(generic.DetailView):
	pass


class ModalView(generic.DetailView):
	pass
