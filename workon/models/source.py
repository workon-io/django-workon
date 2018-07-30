from django.conf import settings
from django.db import models
import workon

__all__ = ['Source']


class Source(models.Model):
    source_from = models.CharField('Source UUID', max_length=1000, db_index=True, null=True, blank=True)
    source_uid =  models.CharField('Source', unique=True, max_length=1000, db_index=True, null=True, blank=True)
    source_data = workon.JSONField(u'Source DATA ', default={})

    class Meta:
        abstract = True
