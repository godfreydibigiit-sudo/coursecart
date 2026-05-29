"""
Payment processing services for CourseCart.
Handles payment simulation, validation, and enrollment activation.
"""
import random
import time
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Payment, PaymentLog


class PaymentServiceError(Exception):
    """Base exception for payment service errors."""
    pass


class DuplicateEnrollmentError(PaymentServiceError):
    """Raised when student is already enrolled in course."""
    pass


class PaymentAlreadyProcessedError(PaymentServiceError):
    """Raised when payment is already completed."""
    pass


class PaymentService:
    """
    Service class for handling payment operations.
    Simulates a local payment gateway.
    """

    @staticmethod
    def create_payment(enrollment, payment_method='mobile_money', phone_number=''):
        """
        Create a new payment record for enrollment.
        
        Args:
            enrollment: Enrollment instance
            payment_method: Payment method choice
            phone_number: Phone number for mobile money
            
        Returns:
            Payment instance
            
        Raises:
            DuplicateEnrollmentError: If payment already exists
            PaymentServiceError: If enrollment is invalid
        """
        # Check for duplicate enrollment payment
        if hasattr(enrollment, 'payment'):
            existing_payment = enrollment.payment
            if existing_payment.status in ['pending', 'processing']:
                return existing_payment
            raise DuplicateEnrollmentError(
                _('Payment already exists for this enrollment.')
            )

        # Validate enrollment
        if enrollment.payment_status != 'pending':
            raise PaymentServiceError(
                _('Invalid enrollment payment status.')
            )

        # Create payment
        payment = Payment.objects.create(
            enrollment=enrollment,
            student=enrollment.student,
            course=enrollment.course,
            amount=enrollment.course.price,
            payment_method=payment_method,
            phone_number=phone_number,
        )

        # Log payment creation
        PaymentService._log_action(
            payment=payment,
            action='payment_created',
            status_to=payment.status,
            message=f'Payment initiated for course: {enrollment.course.title}'
        )

        return payment

    @staticmethod
    def simulate_payment_processing(payment):
        """
        Simulate payment gateway processing.
        In production, this would integrate with M-Pesa, Tigo Pesa, etc.
        
        Args:
            payment: Payment instance
            
        Returns:
            dict: Processing result with status and message
        """
        if payment.status == 'completed':
            raise PaymentAlreadyProcessedError(
                _('This payment has already been completed.')
            )

        # Update status to processing
        old_status = payment.status
        payment.status = 'processing'
        payment.save(update_fields=['status', 'updated_at'])

        PaymentService._log_action(
            payment=payment,
            action='processing_started',
            status_from=old_status,
            status_to='processing',
            message='Payment simulation started'
        )

        # Simulate processing delay
        time.sleep(0.5)

        # Simulate success/failure (90% success rate for demo)
        is_successful = random.random() < 0.9
        
        if is_successful:
            result = PaymentService._complete_payment(payment)
        else:
            result = PaymentService._fail_payment(
                payment,
                'Simulated payment failure: Insufficient funds'
            )

        return result

    @staticmethod
    def _complete_payment(payment):
        """
        Mark payment as completed and activate enrollment.
        Uses direct database update to ensure enrollment is updated.
        """
        from apps.courses.models import Enrollment
        
        old_status = payment.status
        
        # Update payment record
        payment.status = 'completed'
        payment.processed_at = timezone.now()
        payment.gateway_response = (
            f'{{"status": "success", '
            f'"transaction_id": "{payment.transaction_id}", '
            f'"message": "Payment processed successfully"}}'
        )
        payment.save()

        # Log completion
        PaymentService._log_action(
            payment=payment,
            action='payment_completed',
            status_from=old_status,
            status_to='completed',
            message=f'Payment completed successfully. Amount: {payment.amount} TZS'
        )

        # ============================
        # DIRECT DATABASE UPDATE
        # This bypasses model save() completely
        # ============================
        updated = Enrollment.objects.filter(
            id=payment.enrollment.id
        ).update(
            payment_status='completed'
        )
        
        # Force refresh from database
        payment.enrollment.refresh_from_db()
        
        # Verify it actually updated
        if payment.enrollment.payment_status != 'completed':
            # Last resort: raw SQL
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE courses_enrollment SET payment_status = 'completed' WHERE id = %s",
                    [payment.enrollment.id]
                )
            payment.enrollment.refresh_from_db()

        # Update course enrollment count
        payment.course.update_enrollment_count()
        
        # Update instructor stats
        if hasattr(payment.course.instructor, 'instructor_profile'):
            payment.course.instructor.instructor_profile.update_stats()
        
        # Update student profile stats
        if hasattr(payment.student, 'student_profile'):
            payment.student.student_profile.update_enrollment_stats()

        # Send notifications
        from apps.notifications.utils import create_notification
        
        create_notification(
            user=payment.student,
            title='Payment Successful 🎉',
            message=f'Your payment of TZS {payment.amount} for "{payment.course.title}" was successful! Start learning now!',
            notification_type='success',
            link='/courses/my-courses/',
        )
        
        create_notification(
            user=payment.course.instructor,
            title='New Paid Enrollment! 💰',
            message=f'{payment.student.full_name} has paid TZS {payment.amount} and enrolled in "{payment.course.title}".',
            notification_type='enrollment',
            link=f'/courses/instructor/courses/{payment.course.slug}/manage/',
        )

        return {
            'success': True,
            'status': 'completed',
            'message': 'Payment completed successfully! 🎉',
            'transaction_id': payment.transaction_id,
        }
    @staticmethod
    def _fail_payment(payment, reason=''):
        """
        Mark payment as failed.
        Updates enrollment status and notifies student.
        """
        old_status = payment.status
        
        # Update payment record
        payment.status = 'failed'
        payment.gateway_response = (
            f'{{"status": "failed", "reason": "{reason}"}}'
        )
        payment.save()

        # Log failure
        PaymentService._log_action(
            payment=payment,
            action='payment_failed',
            status_from=old_status,
            status_to='failed',
            message=f'Payment failed: {reason}'
        )

        # Update enrollment payment status
        payment.enrollment.payment_status = 'failed'
        payment.enrollment.save(update_fields=['payment_status', 'updated_at'])

        # Notify student about failure
        from apps.notifications.utils import create_notification
        create_notification(
            user=payment.student,
            title='Payment Failed ❌',
            message=(
                f'Your payment of TZS {payment.amount} for '
                f'"{payment.course.title}" has failed. '
                f'Please try again.'
            ),
            notification_type='error',
            link=f'/payments/checkout/{payment.enrollment.id}/',
        )

        return {
            'success': False,
            'status': 'failed',
            'message': reason or 'Payment failed. Please try again.',
            'transaction_id': payment.transaction_id,
        }

    @staticmethod
    def retry_payment(payment):
        """Retry a failed payment."""
        if payment.status not in ['failed', 'cancelled']:
            raise PaymentServiceError(
                _('Only failed or cancelled payments can be retried.')
        )

    # Reset payment status
        payment.status = 'pending'
        payment.gateway_response = ''
        payment.save(update_fields=['status', 'gateway_response'])  # ← FIXED

    # Reset enrollment status
        payment.enrollment.payment_status = 'pending'
        payment.enrollment.save(update_fields=['payment_status'])  # ← FIXED

        PaymentService._log_action(
            payment=payment,
            action='payment_retry',
            status_to='pending',
            message='Payment retry initiated'
    )

        return PaymentService.simulate_payment_processing(payment)
    @staticmethod
    def cancel_payment(payment):
        """Cancel a pending payment."""
        if payment.status not in ['pending', 'processing']:
            raise PaymentServiceError(
                _('Only pending or processing payments can be cancelled.')
            )

        old_status = payment.status
        payment.status = 'cancelled'
        payment.save(update_fields=['status', 'updated_at'])

        PaymentService._log_action(
            payment=payment,
            action='payment_cancelled',
            status_from=old_status,
            status_to='cancelled',
            message='Payment cancelled by user'
        )

        return {
            'success': True,
            'status': 'cancelled',
            'message': 'Payment cancelled.',
        }

    @staticmethod
    def _log_action(payment, action, status_from='', status_to='', message=''):
        """Create payment log entry."""
        PaymentLog.objects.create(
            payment=payment,
            action=action,
            status_from=status_from,
            status_to=status_to,
            message=message,
        )

    @staticmethod
    def get_payment_history(student):
        """Get payment history for a student."""
        return Payment.objects.filter(
            student=student
        ).select_related('course', 'enrollment').order_by('-initiated_at')

    @staticmethod
    def get_payment_stats(student):
        """Get payment statistics for a student."""
        payments = Payment.objects.filter(student=student)
        return {
            'total_payments': payments.count(),
            'completed_payments': payments.filter(status='completed').count(),
            'failed_payments': payments.filter(status='failed').count(),
            'pending_payments': payments.filter(status='pending').count(),
            'total_spent': payments.filter(status='completed').aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
        }