from django.db import models


__all__ = ['Unique', 'Singleton']


class Unique(models.Model):

    _cache = None

    class Meta:
        abstract = True

    @classmethod
    def get(cls):
        if cls._cache is None:
            instance = cls._meta.default_manager.first()
            if not instance:
                instance = cls()
            cls._cache = instance
        return cls._cache

    def save(self, *args, **kwargs):
        previous = self._meta.default_manager.first()
        if previous:
            self.pk = previous.pk
        super().save(*args, **kwargs)
        self._meta.model._cache = self

class Singleton(Unique): 

    class Meta:
        abstract = True