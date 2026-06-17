"""
Custom admin dashboard context.
Provides REAL-TIME data for the admin dashboard.
"""
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta


def get_dashboard_context(request):
    """
    Return fresh real-time context data.
    This function is called on EVERY page load - no caching.
    """
    # Import locally to ensure fresh data each time
    from apps.courses.models import Course, Enrollment, Category, Lesson
    from apps.payments.models import Payment
    from apps.accounts.models import User
    
    today = timezone.now().date()
    
    # Get ALL counts fresh from database
    total_students = User.objects.filter(role='student').count()
    total_instructors = User.objects.filter(role='instructor').count()
    total_courses = Course.objects.all().count()
    total_enrollments = Enrollment.objects.all().count()
    completed_enrollments = Enrollment.objects.filter(is_completed=True).count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    avg_rating = Course.objects.filter(status='published').aggregate(
        avg=Avg('reviews__rating')
    )['avg'] or 0
    
    # Print to console for debugging
    print(f"[DASHBOARD] Students: {total_students}, Instructors: {total_instructors}, Courses: {total_courses}, Enrollments: {total_enrollments}")
    
    return {
        'total_users': total_students + total_instructors,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_courses': total_courses,
        'published_courses': Course.objects.filter(status='published').count(),
        'draft_courses': Course.objects.filter(status='draft').count(),
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'active_enrollments': total_enrollments - completed_enrollments,
        'total_payments': Payment.objects.all().count(),
        'completed_payments': Payment.objects.filter(status='completed').count(),
        'total_revenue': total_revenue,
        'average_course_rating': round(float(avg_rating), 1),
        'completion_rate': round((completed_enrollments / max(total_enrollments, 1)) * 100, 1),
        'recent_enrollments': Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5],
        'recent_payments': Payment.objects.select_related('student', 'course').filter(status='completed').order_by('-processed_at')[:5],
        'recent_users': User.objects.all().order_by('-date_joined')[:5],
        'top_courses': Course.objects.filter(status='published').annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5],
    }