"""
Admin configuration for profile models.
"""
from django.contrib import admin
from .models import StudentProfile, InstructorProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'location', 'total_courses_enrolled',
        'total_courses_completed', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__full_name', 'location']
    raw_id_fields = ['user']
    readonly_fields = ['total_courses_enrolled', 'total_courses_completed', 'created_at', 'updated_at']


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'expertise', 'total_courses_created',
        'total_students', 'is_verified', 'average_rating'
    ]
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'expertise']
    raw_id_fields = ['user']
    readonly_fields = ['total_courses_created', 'total_students', 'average_rating', 'created_at', 'updated_at']
