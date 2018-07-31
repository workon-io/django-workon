from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import workon


__all__ = ['TrackEvent']


class TrackEvent(models.Model):

    timestamp = models.FloatField('TS')
    tracked_at = models.DateTimeField("Tracké à")
    action = models.CharField('Action', max_length=254)

    object_content_type = models.ForeignKey(ContentType, related_name='track_object_content_type', null=True, blank=True, editable=False, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(editable=False, null=True)
    object = GenericForeignKey('object_content_type', 'object_id')
    object_repr = models.CharField(
        "Object representation",
        max_length=250,
        editable=False
    )

    field_name = models.CharField("Field", max_length=254)
    old_value = models.TextField("Old value", null=True, editable=False)
    new_value = models.TextField("New value", null=True, editable=False)
    m2m_pk_set = workon.ArrayField(
        models.PositiveIntegerField('pk'), null=True
    )
    m2m_repr_set = workon.ArrayField(
        models.CharField('Repr', max_length=254), null=True
    )
    m2m_model = None

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Executé par", null=True, blank=True, on_delete=models.SET_NULL)
    user_repr = models.CharField(
        "User representation",
        help_text="User representation, useful if the user is deleted later.",
        max_length=250,
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = 'Model Tracking event'
        verbose_name_plural = 'Model Tracking events'
        ordering = ['-tracked_at']

    def __str__(self):
        return f'{self.action} {str(self.object)}'

    def __init__(self, *args, **kwargs):
        self.m2m_model = kwargs.pop('m2m_model', None)
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.tracked_at:
            self.tracked_at = timezone.now()
        self.timestamp = self.tracked_at.timestamp()
        if self.object:
            self.object_repr = str(self.object)
        if self.user:
            self.user_repr = str(self.user)
        if self.m2m_pk_set and self.m2m_model:
           self.m2m_repr_set = [ str(obj) for obj in self.m2m_model.objects.filter(pk__in=self.m2m_pk_set)]
        super().save(*args, **kwargs)