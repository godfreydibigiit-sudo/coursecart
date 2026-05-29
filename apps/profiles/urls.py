"""
URL patterns for profiles app.
"""
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Dashboard redirect
    path('', views.DashboardRedirectView.as_view(), name='dashboard'),
    
    # Student routes
    path('student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('student/edit/', views.StudentProfileUpdateView.as_view(), name='student_profile_edit'),
    
    # Instructor routes
    path('instructor/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('instructor/edit/', views.InstructorProfileUpdateView.as_view(), name='instructor_profile_edit'),
]