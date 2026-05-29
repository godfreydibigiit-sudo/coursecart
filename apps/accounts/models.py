"""
Custom User model and role-based profiles for CourseCart.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based access (Student or Instructor).
    Email is the unique identifier instead of username.
    """
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        INSTRUCTOR = 'instructor', _('Instructor')
        ADMIN = 'admin', _('Administrator')

    email = models.EmailField(_('email address'), unique=True, db_index=True)
    full_name = models.CharField(_('full name'), max_length=150)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    def get_dashboard_url(self):
        """Return appropriate dashboard URL based on user role."""
        if self.is_instructor:
            return 'profiles:instructor_dashboard'
        return 'profiles:student_dashboard'
