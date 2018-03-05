from django.apps import AppConfig


default_app_config = 'workon.contrib.cleaner.DefaultConfig'


class DefaultConfig(AppConfig):
    name = 'workon.contrib.cleaner'
    label = 'workon_cleaner'
    verbose_name = "File and Image Cleaner"

    def ready(self):
        from workon.contrib.cleaner import cache, handlers
        cache.prepare()
        handlers.connect()