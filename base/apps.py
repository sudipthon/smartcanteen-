from django.apps import AppConfig
from . import signals

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
    
    def ready(self):
        import base.signals  # noqa