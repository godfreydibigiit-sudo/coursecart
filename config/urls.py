"""
URL configuration for vocational_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
Root URL configuration for CourseCart platform.
"""
"""
Root URL configuration for CourseCart platform.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('chatbot/', include('apps.chatbot.urls', namespace='chatbot')),
    
    # Landing Page (root URL)
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Profiles (Dashboards)
    path('dashboard/', include('apps.profiles.urls', namespace='profiles')),
    
    # Courses
    path('courses/', include('apps.courses.urls', namespace='courses')),
    
    # Payments
    path('payments/', include('apps.payments.urls', namespace='payments')),
    
    # Notifications
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)