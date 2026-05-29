"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'title', 'notification_type',
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, 'Selected notifications marked as read.')

    @admin.action(description='Mark selected notifications as unread')
    def mark_as_unread(self, request, queryset):
        for notification in queryset:
            notification.mark_as_unread()
        self.message_user(request, 'Selected notifications marked as unread.')
