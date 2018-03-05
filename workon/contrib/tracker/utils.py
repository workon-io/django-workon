from django.conf import settings


__all__ = ['track']


if 'workon.contrib.tracker' not in settings.INSTALLED_APPS:

    def track(*args, **kwargs):
        raise Exception('workon.contrib.tracker missing from settings.INSTALLED_APPS')

else:
    import time
    import datetime
    from operator import itemgetter

    def track(*fields, save=True):
        """
        Tracks property changes on a model instance.
        
        The changed list of properties is refreshed on model initialization
        and save.
        
        >>> @track_data('name')
        >>> class Post(models.Model):
        >>>     name = models.CharField(...)
        >>> 
        >>> post.name = "new name"
        >>> post.save()
        >>> post.track_changes()
        >>>
        >>> post.get_tracked_events()
        """

        UNSAVED = dict()
        from django.db.models.signals import post_init, post_save, m2m_changed
        from django.contrib.postgres.fields import JSONField
        from django.db.models import Model, ManyToManyField
        from django.utils import timezone
        from django.contrib.contenttypes.fields import GenericRelation
        from workon.contrib.tracker.models import TrackEvent

        def _store(self):
            "Updates a local copy of attributes values"
            if self.id:
                self.__initial_data = dict((f, getattr(self, f)) for f in fields)
            else:
                self.__initial_data = UNSAVED

        def inner(cls):

            def get_tracked_events(self, group_by=None, **kwargs):

                # content_type = ContentType.objects.get_for_model(self)
                # queryset = TrackEvent.objects.filter(content_type__pk=content_type.id, object_id=self.pk).filter(**kwargs)

                queryset = self.generic_tracked_events.filter(**kwargs)

                if group_by == 'timestamp':
                    events = {}
                    for event in queryset.order_by('-tracked_at'):
                        events.setdefault(event.timestamp, []).append(event)
                    return events

                else:
                    return queryset.order_by('-tracked_at')
            cls.get_tracked_events = get_tracked_events


            cls.add_to_class('generic_tracked_events', GenericRelation(
                TrackEvent,
                content_type_field='object_content_type',
                object_id_field='object_id',
            ))

            cls.__initial_data = {} 

            def track_changes(self, user=None):
                ts = time.time()
                changes = self.get_tracked_changes()
                if changes:
                    if save:
                        for field, change in changes.items():
                            change.user = user
                            change.save()
                _store(self)
                return changes
            cls.track_changes = track_changes

            def get_tracked_changes(self):
               return getattr(self, '__tracked_changes', dict())
            cls.get_tracked_changes = get_tracked_changes

            def _post_init(sender, instance, **kwargs):
                _store(instance)
            post_init.connect(_post_init, sender=cls, weak=False)

            def _post_save(sender, instance, **kwargs):
                ts = time.time()
                changes = instance.get_tracked_changes()
                for field_name, old_value in getattr(instance, '__initial_data', dict()).items():
                    if old_value != getattr(instance, field_name):
                        changes[field_name] = TrackEvent(
                            object=instance, 
                            field_name=field_name,
                            action='field_post_save',
                            old_value=old_value, 
                            new_value=getattr(instance, field_name)
                        )
                setattr(instance, '__tracked_changes', changes)
            post_save.connect(_post_save, sender=cls, weak=False)

            for f in fields:
                if isinstance(cls._meta.get_field(f), ManyToManyField):
                    def get_m2m_changed(field_name):
                        def _m2m_changed(sender, instance, action, **kwargs):
                            ts = time.time()
                            changes = instance.get_tracked_changes()
                            if action.startswith('post_'):
                                changes[field_name] = TrackEvent(
                                    object=instance, 
                                    field_name=field_name,
                                    action=f'm2m_{action}', 
                                    m2m_pk_set=list(kwargs.get('pk_set')),
                                    m2m_model=kwargs.get('model')
                                )
                            setattr(instance, '__tracked_changes', changes)
                        return _m2m_changed

                    m2m_changed.connect(get_m2m_changed(f), sender=getattr(cls, f).through, weak=False)

            return cls
        return inner