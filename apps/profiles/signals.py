"""
Signal handlers for automatic profile creation.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudentProfile, InstructorProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create profile when a new user is registered.
    """
    if created:
        if instance.is_student:
            StudentProfile.objects.create(user=instance)
        elif instance.is_instructor:
            InstructorProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Save profile whenever user is saved.
    """
    if instance.is_student and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.is_instructor and hasattr(instance, 'instructor_profile'):
        instance.instructor_profile.save()