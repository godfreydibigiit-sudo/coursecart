"""
Payment models for CourseCart simulated payment system.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.courses.models import Enrollment


class Payment(models.Model):
    """
    Payment record for course enrollment.
    Simulates a local payment gateway with status tracking.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')

    class PaymentMethod(models.TextChoices):
        MOBILE_MONEY = 'mobile_money', _('Mobile Money (M-Pesa/Tigo Pesa)')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        CASH = 'cash', _('Cash Payment')

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount = models.DecimalField(
        _('amount (TZS)'),
        max_digits=10,
        decimal_places=2,
    )
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MOBILE_MONEY,
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        blank=True,
        help_text=_('Required for mobile money payments'),
    )
    transaction_id = models.CharField(
        _('transaction ID'),
        max_length=100,
        unique=True,
        blank=True,
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    gateway_response = models.TextField(
        _('gateway response'),
        blank=True,
        help_text=_('Raw response from payment gateway'),
    )
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['status', '-initiated_at']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.student.full_name} - {self.amount} TZS ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Auto-generate transaction ID and set timestamps."""
        if not self.transaction_id:
            self.transaction_id = self._generate_transaction_id()
        
        if self.status == self.PaymentStatus.COMPLETED and not self.processed_at:
            self.processed_at = timezone.now()
        
        super().save(*args, **kwargs)

    def _generate_transaction_id(self):
        """Generate unique transaction ID."""
        import uuid
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"CC-{timestamp}-{unique_id}"

    @property
    def is_completed(self):
        return self.status == self.PaymentStatus.COMPLETED

    @property
    def is_pending(self):
        return self.status == self.PaymentStatus.PENDING

    @property
    def is_failed(self):
        return self.status == self.PaymentStatus.FAILED


class PaymentLog(models.Model):
    """
    Audit log for payment actions and status changes.
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    action = models.CharField(max_length=100)
    status_from = models.CharField(max_length=20, blank=True)
    status_to = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('payment log')
        verbose_name_plural = _('payment logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"Log: {self.action} at {self.created_at}"