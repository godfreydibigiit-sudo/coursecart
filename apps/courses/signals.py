"""
Signal handlers for courses app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lesson, LessonCompletion, Enrollment


@receiver(post_save, sender=Lesson)
def update_course_lesson_count(sender, instance, created, **kwargs):
    """Update course's total_lessons when a lesson is added."""
    instance.course.update_lesson_count()


@receiver(post_delete, sender=Lesson)
def update_course_lesson_count_on_delete(sender, instance, **kwargs):
    """Update course's total_lessons when a lesson is deleted."""
    instance.course.update_lesson_count()


@receiver(post_save, sender=LessonCompletion)
def update_enrollment_progress(sender, instance, created, **kwargs):
    """Update enrollment progress when a lesson is completed."""
    if created:
        instance.enrollment.calculate_progress()


@receiver(post_save, sender=Enrollment)
def update_course_enrollment_count(sender, instance, **kwargs):
    """Update course's enrollment count."""
    if instance.payment_status == 'completed':
        instance.course.update_enrollment_count()