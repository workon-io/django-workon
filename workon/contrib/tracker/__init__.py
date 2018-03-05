from django.apps import AppConfig


default_app_config = 'workon.contrib.tracker.DefaultConfig'


class DefaultConfig(AppConfig):
    name = 'workon.contrib.tracker'
    label = 'workon_tracker'
    verbose_name = "Tracker for model instance changes"