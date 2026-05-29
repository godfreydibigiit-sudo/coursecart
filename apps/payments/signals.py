"""
Signal handlers for payments app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from apps.notifications.utils import create_notification


@receiver(post_save, sender=Payment)
def handle_payment_status_change(sender, instance, created, **kwargs):
    """
    Create notifications and handle side effects when payment status changes.
    """
    if created:
        # Notify student about payment creation
        create_notification(
            user=instance.student,
            title='Payment Initiated',
            message=f'Your payment of TZS {instance.amount} for "{instance.course.title}" has been initiated.',
            notification_type='payment',
            link=f'/payments/detail/{instance.id}/',
        )
    
    elif instance.status == 'completed' and not instance._state.adding:
        # Notify student about successful payment
        create_notification(
            user=instance.student,
            title='Payment Successful 🎉',
            message=f'Your payment for "{instance.course.title}" was successful! You can now access the course lessons.',
            notification_type='success',
            link=f'/courses/my-courses/',
        )
        
        # Notify instructor about new enrollment
        create_notification(
            user=instance.course.instructor,
            title='New Enrollment!',
            message=f'{instance.student.full_name} has enrolled in your course "{instance.course.title}".',
            notification_type='enrollment',
            link=f'/courses/instructor/courses/{instance.course.slug}/manage/',
        )
    
    elif instance.status == 'failed' and not instance._state.adding:
        # Notify student about payment failure
        create_notification(
            user=instance.student,
            title='Payment Failed ❌',
            message=f'Your payment for "{instance.course.title}" has failed. Please try again.',
            notification_type='error',
            link=f'/payments/checkout/{instance.enrollment.id}/',
        )