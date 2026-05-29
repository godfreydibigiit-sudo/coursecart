"""
Notification models for CourseCart platform.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    User notification model for system events.
    """
    class NotificationType(models.TextChoices):
        INFO = 'info', _('Information')
        SUCCESS = 'success', _('Success')
        WARNING = 'warning', _('Warning')
        ERROR = 'error', _('Error')
        PAYMENT = 'payment', _('Payment')
        ENROLLMENT = 'enrollment', _('Enrollment')
        CERTIFICATE = 'certificate', _('Certificate')
        COURSE_UPDATE = 'course_update', _('Course Update')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(_('title'), max_length=200)
    message = models.TextField(_('message'))
    notification_type = models.CharField(
        _('type'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )
    link = models.CharField(
        _('link'),
        max_length=500,
        blank=True,
        help_text=_('Optional URL to redirect when clicked'),
    )
    is_read = models.BooleanField(_('read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_unread(self):
        """Mark notification as unread."""
        self.is_read = False
        self.read_at = None
        self.save(update_fields=['is_read', 'read_at'])

    @classmethod
    def get_unread_count(cls, user):
        """Get unread notification count for user."""
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def mark_all_as_read(cls, user):
        """Mark all notifications as read for user."""
        from django.utils import timezone
        cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )