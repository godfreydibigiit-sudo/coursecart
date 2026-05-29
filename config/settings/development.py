"""
Development settings for CourseCart platform.
Usage: python manage.py runserver --settings=config.settings.development
"""
from .base import *  # noqa: F403, F401

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-dev-only-key-do-not-use-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend - Print to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar (install django-debug-toolbar separately)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
# INTERNAL_IPS = ['127.0.0.1']