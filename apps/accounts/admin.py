"""
Admin configuration for custom User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import StudentRegistrationForm, InstructorRegistrationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for email-based User model."""
    
    list_display = [
        'email', 'full_name', 'role', 'phone_number',
        'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'full_name', 'phone_number']
    ordering = ['-date_joined']
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('full_name', 'phone_number', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important Dates'), {'fields': ('date_joined', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'phone_number', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'updated_at']
    
    def get_form(self, request, obj=None, **kwargs):
        """Use custom registration forms when adding new users."""
        if not obj:  # Only for creation
            if request.user.is_superuser:
                # Superuser can choose role
                kwargs['form'] = StudentRegistrationForm
        return super().get_form(request, obj, **kwargs)

admin.site.site_header = "Coursecart Admin"
admin.site.site_title = "Coursecart Admin Dashboard"
admin.site.index_title = "Welcome to coursecart System"        