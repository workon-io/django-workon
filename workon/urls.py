
"""
Django-Select2 URL configuration.
Add `django_select` to your ``urlconf`` **if** you use any 'Model' fields::
    url(r'^internal/', include('workon.urls')),
"""
try:
    from django.urls import path, re_path
except:
    from django.conf.urls import url as re_path

from workon.views.select2 import AutoResponseView

urlpatterns = [
    re_path(r"^fields/auto.json$", AutoResponseView.as_view(), name="django_select2-json"),
]