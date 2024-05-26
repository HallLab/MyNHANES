from django.apps import AppConfig


class NhanesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nhanes'

    def ready(self):
        import nhanes.signals  # noqa F401
