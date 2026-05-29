"""
Authentication and registration forms for CourseCart.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User


class UserLoginForm(AuthenticationForm):
    """
    Login form using email instead of username.
    """
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        }),
    )

    error_messages = {
        'invalid_login': _('Invalid email or password. Please try again.'),
        'inactive': _('This account is inactive. Please contact support.'),
    }

    def clean(self):
        """Validate and authenticate user."""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data


class StudentRegistrationForm(forms.ModelForm):
    """
    Registration form for students.
    """
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'At least 8 characters',
        }),
        min_length=8,
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your password',
        }),
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+255 7XX XXX XXX',
            }),
        }

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def clean_phone_number(self):
        """Validate phone number format (Tanzania)."""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic Tanzania phone validation
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) < 9 or len(digits) > 15:
                raise forms.ValidationError(_('Enter a valid phone number.'))
        return phone

    def clean(self):
        """Check that passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match.'))
        
        return cleaned_data

    def save(self, commit=True):
        """Create student user with hashed password."""
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class InstructorRegistrationForm(forms.ModelForm):
    """
    Registration form for instructors.
    """
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'At least 8 characters',
        }),
        min_length=8,
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your password',
        }),
    )
    expertise = forms.CharField(
        label=_('Area of Expertise'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Plumbing, Electrical, Tailoring',
        }),
        help_text=_('What vocational skill do you teach?'),
        required=False,
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+255 7XX XXX XXX',
            }),
        }

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def clean(self):
        """Check that passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match.'))
        
        return cleaned_data

    def save(self, commit=True):
        """Create instructor user with hashed password."""
        user = super().save(commit=False)
        user.role = User.Role.INSTRUCTOR
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user