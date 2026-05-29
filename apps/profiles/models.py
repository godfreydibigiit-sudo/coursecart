"""
Profile models for Student and Instructor.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class StudentProfile(models.Model):
    """
    Extended profile for student users.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        primary_key=True,
    )
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/students/',
        blank=True,
        null=True,
    )
    total_courses_enrolled = models.PositiveIntegerField(default=0)
    total_courses_completed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('student profile')
        verbose_name_plural = _('student profiles')
        ordering = ['-created_at']

    def __str__(self):
        return f"Student: {self.user.full_name}"

    @property
    def completion_rate(self):
        """Calculate course completion percentage."""
        if self.total_courses_enrolled == 0:
            return 0
        return round((self.total_courses_completed / self.total_courses_enrolled) * 100)

    def update_enrollment_stats(self):
        """Recalculate enrollment and completion counts."""
        from apps.courses.models import Enrollment
        self.total_courses_enrolled = Enrollment.objects.filter(student=self.user).count()
        self.total_courses_completed = Enrollment.objects.filter(
            student=self.user,
            is_completed=True
        ).count()
        self.save(update_fields=['total_courses_enrolled', 'total_courses_completed'])


class InstructorProfile(models.Model):
    """
    Extended profile for instructor users.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        primary_key=True,
    )
    bio = models.TextField(_('bio'), max_length=1000, blank=True)
    expertise = models.CharField(_('expertise'), max_length=200, blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/instructors/',
        blank=True,
        null=True,
    )
    website = models.URLField(_('website'), blank=True)
    total_courses_created = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
    )
    is_verified = models.BooleanField(_('verified instructor'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('instructor profile')
        verbose_name_plural = _('instructor profiles')
        ordering = ['-created_at']

    def __str__(self):
        return f"Instructor: {self.user.full_name}"

    def update_stats(self):
        """Recalculate instructor statistics."""
        from apps.courses.models import Course
        courses = Course.objects.filter(instructor=self.user)
        self.total_courses_created = courses.count()
        self.total_students = sum(course.total_enrollments for course in courses)
        self.save(update_fields=['total_courses_created', 'total_students'])