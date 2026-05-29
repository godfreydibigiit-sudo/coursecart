"""
Dashboard and profile management views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .models import StudentProfile, InstructorProfile


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """
    Redirect users to their appropriate dashboard based on role.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_student:
            return redirect('profiles:student_dashboard')
        elif request.user.is_instructor:
            return redirect('profiles:instructor_dashboard')
        return redirect('accounts:login')


class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Student dashboard showing enrolled courses and progress.
    """
    template_name = 'profiles/student_dashboard.html'

    def test_func(self):
        return self.request.user.is_student

    def handle_no_permission(self):
        messages.error(self.request, _('Access denied. Student account required.'))
        return redirect('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(StudentProfile, user=self.request.user)
        
        from apps.courses.models import Enrollment
        enrollments = Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor').order_by('-enrolled_at')
        
        context.update({
            'profile': profile,
            'enrollments': enrollments,
            'active_enrollments': enrollments.filter(is_completed=False),
            'completed_enrollments': enrollments.filter(is_completed=True),
        })
        return context


class InstructorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Instructor dashboard showing created courses and student counts."""
    template_name = 'profiles/instructor_dashboard.html'

    def test_func(self):
        return self.request.user.is_instructor

    def handle_no_permission(self):
        messages.error(self.request, _('Access denied. Instructor account required.'))
        return redirect('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Force refresh instructor stats
        profile = get_object_or_404(InstructorProfile, user=self.request.user)
        profile.update_stats()  # ← RECALCULATE STATS
        
        from apps.courses.models import Course, Enrollment
        
        courses = Course.objects.filter(
            instructor=self.request.user
        ).prefetch_related('enrollments').order_by('-created_at')
        
        # Calculate actual student counts
        total_students = 0
        for course in courses:
            # Count only completed payments
            enrolled = course.enrollments.filter(payment_status='completed').count()
            total_students += enrolled
        
        context.update({
            'profile': profile,
            'courses': courses,
            'published_courses': courses.filter(status='published'),
            'draft_courses': courses.filter(status='draft'),
            'total_students': total_students,  # ← REAL STUDENT COUNT
        })
        return context


class StudentProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit student profile."""
    model = StudentProfile
    template_name = 'profiles/student_profile_edit.html'
    fields = ['bio', 'location', 'date_of_birth', 'avatar']
    success_url = reverse_lazy('profiles:student_dashboard')

    def test_func(self):
        return self.request.user.is_student

    def get_object(self, queryset=None):
        return get_object_or_404(StudentProfile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully!'))
        return super().form_valid(form)


class InstructorProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit instructor profile."""
    model = InstructorProfile
    template_name = 'profiles/instructor_profile_edit.html'
    fields = ['bio', 'expertise', 'location', 'avatar', 'website']
    success_url = reverse_lazy('profiles:instructor_dashboard')

    def test_func(self):
        return self.request.user.is_instructor

    def get_object(self, queryset=None):
        return get_object_or_404(InstructorProfile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully!'))
        return super().form_valid(form)
