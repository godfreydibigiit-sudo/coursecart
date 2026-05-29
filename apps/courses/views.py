"""
Course views for students and instructors.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify as django_slugify
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Course, Lesson, Enrollment, LessonCompletion, CourseReview
)

from .forms import LessonForm


def generate_unique_slug(title):
    """Generate a unique slug for a course title."""
    slug = django_slugify(title)
    original_slug = slug
    counter = 1
    while Course.objects.filter(slug=slug).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1
    return slug


# ==================== PUBLIC VIEWS ====================

class CourseListView(ListView):
    """
    Public course listing with filters and search.
    """
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(
            status='published'
        ).select_related('instructor', 'category').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-created_at')

        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by level
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)

        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructor__full_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            course_count=Count('courses', filter=Q(courses__status='published'))
        )
        context['current_category'] = self.request.GET.get('category', '')
        context['current_level'] = self.request.GET.get('level', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CourseDetailView(DetailView):
    """Public course detail page."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(
            status='published'
        ).select_related('instructor', 'category').prefetch_related('lessons')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        # Check if student is enrolled - GET FRESH DATA
        if self.request.user.is_authenticated and self.request.user.is_student:
            enrollment = Enrollment.objects.filter(
                student=self.request.user,
                course=course
            ).first()
            
            # Refresh from database to get latest payment status
            if enrollment:
                enrollment.refresh_from_db()
            
            context['enrollment'] = enrollment
            context['is_enrolled'] = enrollment is not None
        else:
            context['is_enrolled'] = False

        # Get preview lessons
        context['preview_lessons'] = course.lessons.filter(is_free_preview=True)[:3]

        # Get reviews
        context['reviews'] = course.reviews.select_related('student').order_by('-created_at')[:10]
        context['avg_rating'] = course.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['review_count'] = course.reviews.count()

        return context


class CategoryCourseListView(ListView):
    """Courses filtered by category."""
    model = Course
    template_name = 'courses/category_courses.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Course.objects.filter(
            category=self.category,
            status='published'
        ).select_related('instructor').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# ==================== ENROLLMENT VIEW ====================

@login_required
def enroll_in_course(request, slug):
    """
    Enroll student in a course.
    Redirects to payment or my-courses page.
    """
    if not request.user.is_student:
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('accounts:login')
    
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Check for existing enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'payment_status': 'pending'}
    )
    
    if not created:
        # Already enrolled
        if enrollment.payment_status == 'completed':
            messages.info(request, f'You are already enrolled in {course.title}!')
            return redirect('courses:my_enrollments')
        elif enrollment.payment_status == 'pending':
            messages.info(request, 'Please complete your payment to access the course.')
            return redirect('payments:checkout', enrollment_id=enrollment.id)
        elif enrollment.payment_status == 'failed':
            messages.info(request, 'Your previous payment failed. Please try again.')
            return redirect('payments:checkout', enrollment_id=enrollment.id)
    
    # Free course - complete immediately
    if course.price == 0:
        enrollment.payment_status = 'completed'
        enrollment.save()
        course.update_enrollment_count()
        if hasattr(course.instructor, 'instructor_profile'):
            course.instructor.instructor_profile.update_stats()
        if hasattr(request.user, 'student_profile'):
            request.user.student_profile.update_enrollment_stats()
        messages.success(request, f'🎉 Successfully enrolled in {course.title}! Start learning now!')
        return redirect('courses:my_enrollments')
    
    # Paid course - redirect to payment
    messages.success(request, f'Enrollment created! Please complete payment of TZS {course.price}.')
    return redirect('payments:checkout', enrollment_id=enrollment.id)


# ==================== STUDENT VIEWS ====================

class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to students only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student

    def handle_no_permission(self):
        messages.error(self.request, _('Only students can access this page.'))
        return redirect('accounts:login')


class MyEnrollmentsView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    """Student's enrolled courses."""
    model = Enrollment
    template_name = 'courses/my_enrollments.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related(
            'course', 
            'course__instructor', 
            'course__category'
        ).prefetch_related(
            'course__lessons'
        ).order_by('-enrolled_at')


class LessonView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    """View individual lesson (requires enrollment & payment)."""
    model = Lesson
    template_name = 'courses/lesson_view.html'
    context_object_name = 'lesson'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Lesson.objects.select_related('course'),
            pk=self.kwargs['lesson_pk'],
            course__slug=self.kwargs['course_slug']
        )

    def dispatch(self, request, *args, **kwargs):
        lesson = self.get_object()
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=lesson.course
        )

        if enrollment.payment_status != 'completed':
            messages.error(request, _('Please complete payment to access lessons.'))
            return redirect('payments:checkout', enrollment_id=enrollment.id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        enrollment = Enrollment.objects.get(
            student=self.request.user,
            course=lesson.course
        )

        context['is_completed'] = LessonCompletion.objects.filter(
            enrollment=enrollment,
            lesson=lesson
        ).exists()
        context['all_lessons'] = lesson.course.lessons.order_by('order')
        context['enrollment'] = enrollment
        context['prev_lesson'] = lesson.course.lessons.filter(
            order__lt=lesson.order
        ).order_by('-order').first()
        context['next_lesson'] = lesson.course.lessons.filter(
            order__gt=lesson.order
        ).order_by('order').first()

        return context


@login_required
def mark_lesson_complete(request, course_slug, lesson_pk):
    """Mark a lesson as completed."""
    if not request.user.is_student:
        return HttpResponseForbidden()

    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, pk=lesson_pk)
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=lesson.course
        )

        completion, created = LessonCompletion.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        if created:
            messages.success(request, _('Lesson marked as complete! 🎉'))
        else:
            messages.info(request, _('Lesson already completed.'))

        next_lesson = lesson.course.lessons.filter(
            order__gt=lesson.order
        ).order_by('order').first()

        if next_lesson:
            return redirect('courses:lesson_view', course_slug=course_slug, lesson_pk=next_lesson.pk)
        else:
            messages.success(request, _('Congratulations! You completed all lessons! 🏆'))
            return redirect('courses:my_enrollments')

    return redirect('courses:lesson_view', course_slug=course_slug, lesson_pk=lesson_pk)


@login_required
def add_review(request, course_slug):
    """Add a review for a completed course."""
    if not request.user.is_student:
        return HttpResponseForbidden()

    course = get_object_or_404(Course, slug=course_slug)
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course,
        is_completed=True
    )

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if rating:
            review, created = CourseReview.objects.update_or_create(
                student=request.user,
                course=course,
                defaults={'rating': int(rating), 'comment': comment}
            )
            messages.success(request, _('Thank you for your review! ⭐'))
        else:
            messages.error(request, _('Please provide a rating.'))

    return redirect('courses:course_detail', slug=course_slug)


# ==================== INSTRUCTOR VIEWS ====================

class InstructorRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to instructors only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor

    def handle_no_permission(self):
        messages.error(self.request, _('Only instructors can access this page.'))
        return redirect('accounts:login')


class InstructorCourseListView(LoginRequiredMixin, InstructorRequiredMixin, ListView):
    """Instructor's created courses."""
    model = Course
    template_name = 'courses/instructor/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(
            instructor=self.request.user
        ).prefetch_related('enrollments').order_by('-created_at')


class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """Create a new course."""
    model = Course
    template_name = 'courses/instructor/course_form.html'
    fields = [
        'title', 'category', 'description', 'short_description',
        'thumbnail', 'price', 'duration_weeks', 'level', 'is_certificate_ready'
    ]

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        form.instance.slug = generate_unique_slug(form.instance.title)
        form.instance.status = 'published'
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Course "{}" created and published! Add lessons now.').format(self.object.title)
        )
        return response

    def get_success_url(self):
        return reverse_lazy('courses:instructor_course_manage', kwargs={'slug': self.object.slug})


class CourseUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    """Edit existing course."""
    model = Course
    template_name = 'courses/instructor/course_form.html'
    fields = [
        'title', 'category', 'description', 'short_description',
        'thumbnail', 'price', 'duration_weeks', 'level', 'status', 'is_certificate_ready'
    ]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _('Course updated successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:instructor_course_manage', kwargs={'slug': self.object.slug})


class LessonCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """Add a lesson to a course."""
    model = Lesson
    template_name = 'courses/instructor/lesson_form.html'
    form_class = LessonForm
    # Remove fields attribute since we're using form_class

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(
            Course, 
            slug=kwargs['course_slug'], 
            instructor=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['existing_lessons'] = self.course.lessons.order_by('order')
        return context

    def form_valid(self, form):
        form.instance.course = self.course
        response = super().form_valid(form)
        messages.success(
            self.request, 
            _('Lesson "{}" added successfully! 🎉').format(self.object.title)
        )
        return response

    def get_success_url(self):
        return reverse_lazy(
            'courses:instructor_course_manage', 
            kwargs={'slug': self.course.slug}
        )

class InstructorCourseManageView(LoginRequiredMixin, InstructorRequiredMixin, DetailView):
    """Manage course (lessons, enrollments)."""
    model = Course
    template_name = 'courses/instructor/course_manage.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).prefetch_related(
            'lessons', 'enrollments__student'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons'] = self.object.lessons.order_by('order')
        context['enrollments'] = self.object.enrollments.filter(
            payment_status='completed'
        ).select_related('student__student_profile')
        return context