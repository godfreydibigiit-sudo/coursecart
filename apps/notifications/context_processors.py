"""
Context processors for notifications app.
"""
from .models import Notification


def notification_context(request):
    """
    Add unread notification count to all templates.
    Usage: {{ notification_unread_count }} in templates
    """
    if request.user.is_authenticated:
        unread_count = Notification.get_unread_count(request.user)
        return {
            'notification_unread_count': unread_count,
            'has_unread_notifications': unread_count > 0,
        }
    return {
        'notification_unread_count': 0,
        'has_unread_notifications': False,
    }