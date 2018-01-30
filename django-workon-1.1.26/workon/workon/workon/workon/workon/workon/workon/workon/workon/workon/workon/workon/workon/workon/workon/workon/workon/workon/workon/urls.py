
"""
Django-Select2 URL configuration.
Add `django_select` to your ``urlconf`` **if** you use any 'Model' fields::
    url(r'^internal/', include('workon.urls')),
"""
from django.conf.urls import url

from workon.views.select2 import AutoResponseView

urlpatterns = [
    url(r"^fields/auto.json$", AutoResponseView.as_view(), name="django_select2-json"),
]