from django.db import models
from django.contrib.postgres.fields import JSONField


__all__ = [
    'Geo',
]


class Geo(models.Model):

    geo_address = models.CharField(u'Adresse géolocalisée', max_length=254, blank=True, null=True)
    geo_latitude = models.FloatField(u'lat', blank=True, null=True, db_index=True)
    geo_longitude = models.FloatField(u'lon', blank=True, null=True, db_index=True)
    geo_formatted_address = models.CharField(u'Adresse géocodée & formattée', max_length=254, blank=True, null=True)
    geo_data = JSONField(u'Geodata', default={}, blank=True, null=True)

    google_place_id = models.CharField(u'Google place ID', max_length=254, blank=True, null=True)
    google_place_result = JSONField(u'Google place Result', blank=True, null=True)

    class Meta:
        abstract = True
