"""
Admin configuration for courses app.
"""
from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, LessonCompletion, CourseReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active_courses_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['title', 'order', 'lesson_type', 'is_free_preview']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'instructor', 'category', 'price',
        'status', 'total_enrollments', 'created_at'
    ]
    list_filter = ['status', 'level', 'category', 'created_at']
    search_fields = ['title', 'instructor__full_name', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    raw_id_fields = ['instructor']
    date_hierarchy = 'created_at'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'lesson_type', 'duration_minutes', 'is_free_preview']
    list_filter = ['lesson_type', 'is_free_preview']
    search_fields = ['title', 'course__title']
    raw_id_fields = ['course']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'payment_status',
        'progress_percentage', 'is_completed', 'enrolled_at'
    ]
    list_filter = ['payment_status', 'is_completed', 'enrolled_at']
    search_fields = ['student__email', 'course__title']
    raw_id_fields = ['student', 'course']


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'completed_at']
    raw_id_fields = ['enrollment', 'lesson']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    raw_id_fields = ['student', 'course']