"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import Payment, PaymentLog

from django.utils.translation import gettext_lazy as _ 


class PaymentLogInline(admin.TabularInline):
    model = PaymentLog
    extra = 0
    readonly_fields = ['action', 'status_from', 'status_to', 'message', 'created_at']
    fields = ['action', 'status_from', 'status_to', 'message', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'student', 'course', 'amount',
        'payment_method', 'status', 'transaction_id', 'initiated_at'
    ]
    list_filter = ['status', 'payment_method', 'initiated_at']
    search_fields = [
        'student__email', 'student__full_name',
        'course__title', 'transaction_id'
    ]
    readonly_fields = [
        'transaction_id', 'gateway_response',
        'initiated_at', 'processed_at', 'updated_at'
    ]
    raw_id_fields = ['student', 'course', 'enrollment']
    inlines = [PaymentLogInline]
    date_hierarchy = 'initiated_at'
    
    fieldsets = (
        (_('Payment Details'), {
            'fields': (
                'enrollment', 'student', 'course',
                'amount', 'payment_method', 'phone_number'
            )
        }),
        (_('Transaction Info'), {
            'fields': (
                'transaction_id', 'status', 'gateway_response'
            )
        }),
        (_('Timestamps'), {
            'fields': (
                'initiated_at', 'processed_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'action', 'status_from', 'status_to', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['payment__transaction_id', 'message']
    readonly_fields = ['payment', 'action', 'status_from', 'status_to', 'message', 'ip_address', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False