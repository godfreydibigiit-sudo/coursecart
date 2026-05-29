"""
Course, Lesson, and Enrollment models for CourseCart.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.db.models import F


class Category(models.Model):
    """
    Course categories (Plumbing, Electrical, Tailoring, etc.).
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True)
    description = models.TextField(_('description'), max_length=500, blank=True)
    icon = models.CharField(
        _('icon'),
        max_length=10,
        blank=True,
        help_text=_('Emoji icon for the category'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('courses:category_detail', kwargs={'slug': self.slug})

    @property
    def active_courses_count(self):
        return self.courses.filter(status='published').count()


class Course(models.Model):
    """
    Course created by instructors.
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        ARCHIVED = 'archived', _('Archived')

    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')

    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=220, unique=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_teaching',
        limit_choices_to={'role': 'instructor'},
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
    )
    description = models.TextField(_('description'))
    short_description = models.CharField(
        _('short description'),
        max_length=300,
        help_text=_('Brief summary shown in course cards'),
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='courses/thumbnails/',
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        _('price (TZS)'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Price in Tanzanian Shillings'),
    )
    duration_weeks = models.PositiveIntegerField(
        _('duration (weeks)'),
        default=4,
        help_text=_('Estimated course duration in weeks'),
    )
    level = models.CharField(
        _('level'),
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    total_lessons = models.PositiveIntegerField(default=0)
    total_enrollments = models.PositiveIntegerField(default=0)
    is_certificate_ready = models.BooleanField(
        _('certificate available'),
        default=False,
        help_text=_('Enable certificate generation upon completion'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.slug})

    def update_lesson_count(self):
        """Update cached lesson count."""
        self.total_lessons = self.lessons.count()
        self.save(update_fields=['total_lessons'])

    def update_enrollment_count(self):
        """Update cached enrollment count."""
        self.total_enrollments = self.enrollments.filter(
            payment_status='completed'
        ).count()
        self.save(update_fields=['total_enrollments'])


class Lesson(models.Model):
    """
    Individual lesson within a course.
    """
    class LessonType(models.TextChoices):
        VIDEO = 'video', _('Video Lesson')
        YOUTUBE = 'youtube', _('YouTube Video')
        DOCUMENT = 'document', _('Document/PDF')
        QUIZ = 'quiz', _('Quiz')

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
    )
    title = models.CharField(_('title'), max_length=200)
    order = models.PositiveIntegerField(_('order'), default=1)
    
    # Lesson type
    lesson_type = models.CharField(
        _('lesson type'),
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.YOUTUBE,
    )
    
    # Content fields
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Brief description of what this lesson covers'),
    )
    notes = models.TextField(
        _('text notes'),
        blank=True,
        help_text=_('Written lesson content (optional)'),
    )
    
    # YouTube
    youtube_url = models.URLField(
        _('YouTube URL'),
        blank=True,
        help_text=_('Paste YouTube video link (e.g., https://www.youtube.com/watch?v=...)'),
    )
    
    # PDF Document
    pdf_file = models.FileField(
        _('PDF notes/document'),
        upload_to='lessons/documents/',
        blank=True,
        null=True,
        help_text=_('Upload PDF notes or slides for students to download'),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    
    # Video upload (optional, for non-YouTube videos)
    video_file = models.FileField(
        _('video file'),
        upload_to='lessons/videos/',
        blank=True,
        null=True,
        help_text=_('Upload video file (or use YouTube URL instead)'),
    )
    
    # Duration
    duration_minutes = models.PositiveIntegerField(
        _('duration (minutes)'),
        default=10,
        help_text=_('Estimated time to complete this lesson'),
    )
    
    # Access control
    is_free_preview = models.BooleanField(
        _('free preview'),
        default=False,
        help_text=_('Allow viewing without enrollment'),
    )
    is_published = models.BooleanField(
        _('published'),
        default=True,
        help_text=_('Make this lesson visible to students'),
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.order}. {self.title}"

    def save(self, *args, **kwargs):
        """Auto-set order if not provided or fix conflicts."""
        if not self.order or self.order == 1:
        # Get the last order number and add 1
            last_lesson = Lesson.objects.filter(
                course=self.course
           ).order_by('-order').first()
            self.order = (last_lesson.order + 1) if last_lesson else 1
        else:
        # Check if this order already exists
            existing = Lesson.objects.filter(
                course=self.course, 
                order=self.order
            ).exclude(pk=self.pk).exists()
        
            if existing:
            # Shift all lessons from this order up by 1
                Lesson.objects.filter(
                    course=self.course,
                    order__gte=self.order
                ).exclude(pk=self.pk).update(
                    order=models.F('order') + 1
            )
    
        super().save(*args, **kwargs)

    def get_youtube_embed_url(self):
        """Convert YouTube URL to embed format."""
        if not self.youtube_url:
            return None
        
        url = self.youtube_url.strip()
        
        if 'embed' in url:
            return url
        
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        
        if 'watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        
        import re
        match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
        if match:
            return f'https://www.youtube.com/embed/{match.group(1)}'
        
        return url

    @property
    def has_video(self):
        """Check if lesson has any video content."""
        return bool(self.youtube_url or self.video_file)

    @property
    def has_document(self):
        """Check if lesson has PDF document."""
        return bool(self.pdf_file)

    @property
    def icon(self):
        """Get emoji icon based on lesson type."""
        icons = {
            'video': '🎬',
            'youtube': '▶️',
            'document': '📄',
            'quiz': '📝',
        }
        return icons.get(self.lesson_type, '📖')


class Enrollment(models.Model):
    """
    Student enrollment in a course.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    is_completed = models.BooleanField(_('course completed'), default=False)
    progress_percentage = models.PositiveIntegerField(
        _('progress'),
        default=0,
        help_text=_('Percentage of lessons completed'),
    )
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('enrollment')
        verbose_name_plural = _('enrollments')
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.course.title}"

    def calculate_progress(self):
        """Calculate completion percentage based on lessons."""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return 0
        
        completed_lessons = self.completed_lessons.count()
        self.progress_percentage = round((completed_lessons / total_lessons) * 100)
        
        if self.progress_percentage == 100 and not self.is_completed:
            self.is_completed = True
            from django.utils import timezone
            self.completed_at = timezone.now()
        
        self.save(update_fields=['progress_percentage', 'is_completed', 'completed_at'])
        return self.progress_percentage


class LessonCompletion(models.Model):
    """
    Track which lessons a student has completed.
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='completed_lessons',
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='completions',
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('lesson completion')
        verbose_name_plural = _('lesson completions')
        unique_together = ['enrollment', 'lesson']
        ordering = ['completed_at']

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.lesson.title}"


class CourseReview(models.Model):
    """
    Student reviews and ratings for courses.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        choices=[(i, str(i)) for i in range(1, 6)],
    )
    comment = models.TextField(_('comment'), max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        unique_together = ['student', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} rated {self.course.title} - {self.rating}⭐"