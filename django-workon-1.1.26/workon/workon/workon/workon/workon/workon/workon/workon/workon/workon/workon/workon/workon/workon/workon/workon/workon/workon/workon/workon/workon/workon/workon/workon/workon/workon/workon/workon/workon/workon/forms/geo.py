# # encoding: utf-8

# from django import forms
# from django.utils.translation import ugettext_lazy as _

# from ..widgets.geo import LocationInput



# class LocationField(forms.CharField):

#     def __init__(self, *args, **kwargs):
#         if 'widget' not in kwargs:
#             kwargs['widget'] = LocationInput(

#                 attrs={'placeholder': _(u'Saisissez une adresse')}
#             )
#         super(LocationField, self).__init__(*args, **kwargs)

