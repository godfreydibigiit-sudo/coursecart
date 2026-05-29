"""
App configuration for profiles app.
"""
from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    verbose_name = 'User Profiles'

    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.profiles.signals  # noqa: F401
