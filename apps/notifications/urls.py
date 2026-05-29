"""
URL patterns for notifications app.
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # List views
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path(
        'unread/',
        views.UnreadNotificationsView.as_view(),
        name='unread_notifications',
    ),
    
    # Actions
    path(
        'mark-read/<int:notification_id>/',
        views.mark_notification_read,
        name='mark_notification_read',
    ),
    path(
        'mark-all-read/',
        views.mark_all_read,
        name='mark_all_read',
    ),
    path(
        'delete/<int:notification_id>/',
        views.delete_notification,
        name='delete_notification',
    ),
    path(
        'navigate/<int:notification_id>/',
        views.navigate_notification,
        name='navigate_notification',
    ),
    
    # AJAX Endpoints
    path(
        'unread-count/',
        views.unread_count,
        name='unread_count',
    ),
]