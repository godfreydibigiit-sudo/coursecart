"""
URL patterns for courses app.
"""
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Public routes
    path('', views.CourseListView.as_view(), name='course_list'),
    path('category/<slug:slug>/', views.CategoryCourseListView.as_view(), name='category_detail'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # Student routes
    path('my-courses/', views.MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('course/<slug:course_slug>/lesson/<int:lesson_pk>/', views.LessonView.as_view(), name='lesson_view'),
    path('course/<slug:course_slug>/lesson/<int:lesson_pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('course/<slug:course_slug>/review/', views.add_review, name='add_review'),
    
    # Instructor routes
    path('instructor/courses/', views.InstructorCourseListView.as_view(), name='instructor_course_list'),
    path('instructor/courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('instructor/courses/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('instructor/courses/<slug:slug>/manage/', views.InstructorCourseManageView.as_view(), name='instructor_course_manage'),
    path('instructor/courses/<slug:course_slug>/lessons/add/', views.LessonCreateView.as_view(), name='lesson_create'),
    path(
        'course/<slug:slug>/enroll/', 
        views.enroll_in_course, 
        name='enroll_course'
    ),
    path('course/<slug:slug>/enroll/', views.enroll_in_course, name='enroll_course'),
]