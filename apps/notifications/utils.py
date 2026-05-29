"""
Utility functions for creating notifications.
"""
from .models import Notification


def create_notification(user, title, message, notification_type='info', link=''):
    """
    Create a notification for a user.
    
    Args:
        user: User instance
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        link: Optional URL link
        
    Returns:
        Notification instance or None
    """
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )
        return notification
    except Exception:
        # Silently fail if notification creation fails
        # Don't let notification errors break the main flow
        return None


def notify_student_enrollment(enrollment):
    """Notify student about successful enrollment."""
    create_notification(
        user=enrollment.student,
        title='Enrollment Successful! 🎓',
        message=f'You have successfully enrolled in "{enrollment.course.title}". Start learning now!',
        notification_type='success',
        link=f'/courses/course/{enrollment.course.slug}/',
    )


def notify_instructor_new_student(enrollment):
    """Notify instructor about new student enrollment."""
    create_notification(
        user=enrollment.course.instructor,
        title='New Student Enrolled!',
        message=f'{enrollment.student.full_name} has enrolled in your course "{enrollment.course.title}".',
        notification_type='enrollment',
        link=f'/courses/instructor/courses/{enrollment.course.slug}/manage/',
    )


def notify_course_completion(enrollment):
    """Notify student about course completion."""
    create_notification(
        user=enrollment.student,
        title='Course Completed! 🏆',
        message=f'Congratulations! You have completed "{enrollment.course.title}".',
        notification_type='success',
        link=f'/courses/my-courses/',
    )


def notify_certificate_issued(enrollment):
    """Notify student when certificate is issued."""
    create_notification(
        user=enrollment.student,
        title='Certificate Issued! 📜',
        message=f'Your certificate for "{enrollment.course.title}" is now available.',
        notification_type='certificate',
        link=f'/courses/my-courses/',
    )


def notify_course_published(course):
    """Notify instructor when course is published."""
    create_notification(
        user=course.instructor,
        title='Course Published! 🚀',
        message=f'Your course "{course.title}" is now live and available to students.',
        notification_type='success',
        link=f'/courses/course/{course.slug}/',
    )