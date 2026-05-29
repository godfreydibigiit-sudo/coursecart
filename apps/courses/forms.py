"""
Forms for course and lesson management.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Lesson


class LessonForm(forms.ModelForm):
    """
    Professional lesson creation form with conditional fields.
    """
    class Meta:
        model = Lesson
        fields = [
            'title', 'lesson_type', 'description', 'notes',
            'youtube_url', 'pdf_file', 'video_file',
            'duration_minutes', 'is_free_preview', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Circuit Basics',
            }),
            'lesson_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of what students will learn...',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Detailed lesson content, instructions, or additional notes...',
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...',
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 480,
            }),
        }

    def clean_youtube_url(self):
        """Validate YouTube URL format."""
        url = self.cleaned_data.get('youtube_url', '')
        if url:
            if 'youtube.com' not in url and 'youtu.be' not in url:
                raise forms.ValidationError(
                    _('Please enter a valid YouTube URL.')
                )
        return url

    def clean(self):
        """Validate that appropriate content is provided for lesson type."""
        cleaned_data = super().clean()
        lesson_type = cleaned_data.get('lesson_type')
        youtube_url = cleaned_data.get('youtube_url')
        video_file = cleaned_data.get('video_file')
        pdf_file = cleaned_data.get('pdf_file')
        
        if lesson_type == 'youtube' and not youtube_url:
            self.add_error('youtube_url', _('YouTube URL is required for YouTube lessons.'))
        
        if lesson_type == 'video' and not video_file:
            self.add_error('video_file', _('Video file is required for video lessons.'))
        
        return cleaned_data