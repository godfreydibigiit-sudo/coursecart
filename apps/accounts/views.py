"""
Authentication views for CourseCart platform.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .forms import UserLoginForm, StudentRegistrationForm, InstructorRegistrationForm
from apps.courses.models import Course, Category
from apps.accounts.models import User


class WelcomeView(TemplateView):
    """
    Landing page for CourseCart.
    Shows featured courses and platform information.
    """
    template_name = 'accounts/welcome.html'

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to their dashboard
        if request.user.is_authenticated:
            if request.user.is_student:
                return redirect('profiles:student_dashboard')
            elif request.user.is_instructor:
                return redirect('profiles:instructor_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
            template_name = 'accounts/welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.courses.models import Course
        
        context['featured_courses'] = Course.objects.filter(
            status='published'
        ).select_related('instructor', 'category').order_by('-created_at')[:8]
        
        return context


def login_view(request):
    """Handle user login with email."""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request,
                _(f'Welcome back, {user.full_name}!')
            )
            
            # Redirect to next page or dashboard
            next_url = request.GET.get('next', user.get_dashboard_url())
            return redirect(next_url)
        else:
            messages.error(request, _('Invalid email or password.'))
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_student_view(request):
    """Handle student registration."""
    if request.user.is_authenticated:
        return redirect('profiles:student_dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                _('Registration successful! Welcome to CourseCart.')
            )
            return redirect('profiles:student_dashboard')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/register_student.html', {'form': form})


def register_instructor_view(request):
    """Handle instructor registration."""
    if request.user.is_authenticated:
        return redirect('profiles:instructor_dashboard')
    
    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                _('Registration successful! Welcome, Instructor.')
            )
            return redirect('profiles:instructor_dashboard')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = InstructorRegistrationForm()
    
    return render(request, 'accounts/register_instructor.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, _('You have been logged out successfully.'))
    return redirect('accounts:login')
