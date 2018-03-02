import datetime
import workon
from django.db import models
from django.utils import formats
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache


__all__ = ['Event']


class Event(models.Model):

    start_at = models.DateTimeField("Début", null=True, blank=True)
    end_at = models.DateTimeField("Fin", null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ("start_at", )


class ICSEvent(Event):
    
    class Meta:
        abstract = True

    def get_ics_description(self):
        return "---"

    def get_ics_summary(self):
        return "---"

    def get_ics_receivers(self):
        return [ ]

    def to_calendar_json(self, **kwargs):
        data = dict(
            id=self.id,
            summary=self.get_ics_summary(),
            description=self.get_ics_description(),
            save_url= (
                'calendar:%s-update' % self.__class__.__name__.lower(),
                { 'pk': self.pk }
            ),
            start_at=formats.date_format(self.start_at, 'c') if self.end_at else None,
            end_at=formats.date_format(self.end_at, 'c') if self.end_at else None,
        )
        data.update(**kwargs)
        return data


    def get_ics(self, cancel=False):
        receivers = self.get_ics_receivers()
        if receivers:

            return workon.utils.ics(
                self.start_at - datetime.timedelta(hours=1),
                self.end_at - datetime.timedelta(hours=1),
                summary=self.get_ics_summary(),
                description=self.get_ics_description(),
                uid='ITTEK_%s_%s' % (self.__class__.__name__.upper(), self.pk),
                users=receivers,
                organizer="support@it-tek.fr"
            ), receivers
        else:
            return None, receivers

    def enqueue_notify_ics(self, cancel=False, tester=None):

        ### Prevent multiple email sending, causes to m2m changed
        last_task_id_cache_key = 'enqueued_%s_%s_notify_task_id' % (self.__class__.__name__.lower(), self.pk)
        last_task_id = cache.get(last_task_id_cache_key)
        if last_task_id:
            from celery.task.control import revoke
            revoke(last_task_id, terminate=True)

        task = tasks.notify_ics.apply_async((self._meta.app_label, self.__class__.__name__.lower(), self.pk, cancel, tester), countdown=10)
        cache.set(last_task_id_cache_key, task.id, 120)

    def notify_ics(self, cancel=False, tester=None):

        ical, receivers = self.get_ics(cancel=cancel)
        if ical:
            workon.utils.send_email(
                u"IT'TEK - Support : %s" % self.get_ics_summary(),
                u"IT'TEK - Support <support@it-tek.fr>",
                [user.email for user in receivers],
                content=ical,
                content_type='text/calendar',
                # files=[("intervention.ics", cal.to_ical(), 'text/calendar')]
            )

