"""
URL patterns for accounts app.
"""
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'accounts'

urlpatterns = [
    # Landing page (this maps to /)
    path('', views.WelcomeView.as_view(), name='welcome'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/student/', views.register_student_view, name='register_student'),
    path('register/instructor/', views.register_instructor_view, name='register_instructor'),
    path('manual/', TemplateView.as_view(template_name='accounts/manual.html'), name='user_manual'),
    path('srs/', TemplateView.as_view(template_name='accounts/srs_document.html'), name='srs_document'),
    path('proposal/', TemplateView.as_view(template_name='accounts/proposal.html'), name='proposal'),
]