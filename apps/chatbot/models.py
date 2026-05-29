from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ChatInteraction(models.Model):
    """
    Records every chat interaction for learning and improvement.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_interactions'
    )
    session_id = models.CharField(max_length=100, blank=True)
    user_message = models.TextField()
    bot_response = models.TextField()
    intent_detected = models.CharField(max_length=100, blank=True)
    strategy_used = models.CharField(max_length=50, blank=True)
    response_time_ms = models.IntegerField(default=0)
    was_helpful = models.BooleanField(null=True, blank=True)
    user_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('chat interaction')
        verbose_name_plural = _('chat interactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['intent_detected', '-created_at']),
            models.Index(fields=['was_helpful']),
        ]

    def __str__(self):
        return f"Chat: {self.user_message[:50]}..."


class KnowledgeEntry(models.Model):
    """
    Learned knowledge from successful interactions.
    """
    class Category(models.TextChoices):
        COURSES = 'courses', _('Courses')
        PAYMENTS = 'payments', _('Payments')
        ENROLLMENT = 'enrollment', _('Enrollment')
        CERTIFICATES = 'certificates', _('Certificates')
        PLATFORM = 'platform', _('Platform Help')
        INSTRUCTOR = 'instructor', _('Instructor')
        GENERAL = 'general', _('General')

    question_pattern = models.CharField(max_length=500)
    keywords = models.CharField(max_length=300, blank=True)
    intent = models.CharField(max_length=50, choices=Category.choices)
    response_variations = models.JSONField(default=list)
    usage_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('knowledge entry')
        verbose_name_plural = _('knowledge entries')
        ordering = ['-success_count']

    def __str__(self):
        return f"Knowledge: {self.question_pattern[:60]}"

    @property
    def success_rate(self):
        if self.usage_count == 0:
            return 0
        return round((self.success_count / self.usage_count) * 100)

    def get_best_response(self):
        """Return the most successful response variation."""
        if self.response_variations:
            # Sort by success rate if available
            return self.response_variations[0].get('text', '')
        return ''


class ThinkingStep(models.Model):
    """
    Simulates AI thinking process for display to users.
    """
    intent = models.CharField(max_length=50)
    step_order = models.IntegerField(default=1)
    message = models.CharField(max_length=200)
    duration_ms = models.IntegerField(default=800)

    class Meta:
        verbose_name = _('thinking step')
        verbose_name_plural = _('thinking steps')
        ordering = ['intent', 'step_order']

    def __str__(self):
        return f"Step {self.step_order}: {self.message}"