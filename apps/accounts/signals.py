"""
Signal handlers for User model.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


# Placeholder for future profile creation signals
# Will be activated when profiles app is created
"""
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    '''
    Automatically create StudentProfile or InstructorProfile
    when a new user is created.
    '''
    if created:
        if instance.is_student:
            from apps.profiles.models import StudentProfile
            StudentProfile.objects.create(user=instance)
        elif instance.is_instructor:
            from apps.profiles.models import InstructorProfile
            InstructorProfile.objects.create(user=instance)
"""