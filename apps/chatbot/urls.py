from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/suggestions/', views.suggested_questions, name='suggested_questions'),
    path('api/health/', views.health_check, name='health_check'),
]