"""
Notification views for CourseCart platform.
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """
    List all notifications for the logged-in user.
    """
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.get_unread_count(self.request.user)
        return context


class UnreadNotificationsView(LoginRequiredMixin, ListView):
    """
    Show only unread notifications.
    """
    model = Notification
    template_name = 'notifications/unread_notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).order_by('-created_at')


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.mark_as_read()

    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': Notification.get_unread_count(request.user),
        })

    # Redirect to notification link or back to list
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:notification_list')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read."""
    Notification.mark_all_as_read(request.user)
    messages.success(request, _('All notifications marked as read.'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': 0,
        })

    return redirect('notifications:notification_list')


@login_required
def unread_count(request):
    """
    AJAX endpoint to get unread notification count.
    Used for navbar badge updates.
    """
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'unread_count': count,
        'has_unread': count > 0,
    })


@login_required
@require_POST
def delete_notification(request, notification_id):
    """Delete a notification."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': Notification.get_unread_count(request.user),
        })

    messages.success(request, _('Notification deleted.'))
    return redirect('notifications:notification_list')


@login_required
def navigate_notification(request, notification_id):
    """
    Mark notification as read and redirect to its link.
    """
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.mark_as_read()

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:notification_list')