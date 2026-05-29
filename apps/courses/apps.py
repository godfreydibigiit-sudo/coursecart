"""
App configuration for courses app.
"""
from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.courses'
    verbose_name = 'Course Management'

    def ready(self):
        """Import signals when app is ready."""
        import apps.courses.signals  # noqa: F401
