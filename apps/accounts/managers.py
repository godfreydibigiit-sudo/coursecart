"""
Custom User manager for email-based authentication.
"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager where email is the unique identifier
    and username is not used at all.
    """

    def create_user(self, email, full_name, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, full_name, password, **extra_fields)

    def students(self):
        """Return only student users."""
        return self.get_queryset().filter(role=self.model.Role.STUDENT)

    def instructors(self):
        """Return only instructor users."""
        return self.get_queryset().filter(role=self.model.Role.INSTRUCTOR)