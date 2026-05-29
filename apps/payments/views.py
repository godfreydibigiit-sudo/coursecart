"""
Payment views for CourseCart payment simulation.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import DetailView, ListView, TemplateView
from django.urls import reverse
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Payment, PaymentLog
from .services import (
    PaymentService,
    PaymentServiceError,
    DuplicateEnrollmentError,
    PaymentAlreadyProcessedError,
)
from apps.courses.models import Enrollment


class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to students only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student

    def handle_no_permission(self):
        messages.error(self.request, _('Only students can access this page.'))
        return redirect('accounts:login')


class PaymentCheckoutView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    """
    Payment checkout page.
    Shows payment details and initiates payment.
    """
    model = Enrollment
    template_name = 'payments/checkout.html'
    context_object_name = 'enrollment'
    pk_url_kwarg = 'enrollment_id'

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.object

        # Check if payment already exists
        existing_payment = getattr(enrollment, 'payment', None)
        context['existing_payment'] = existing_payment
        context['has_completed_payment'] = (
            existing_payment and existing_payment.is_completed
        )

        return context


class PaymentSimulatorView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    """
    Payment simulation page.
    Shows processing animation and returns result.
    """
    model = Payment
    template_name = 'payments/payment_simulator.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'

    def get_queryset(self):
        return Payment.objects.filter(student=self.request.user)


class PaymentHistoryView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    """Payment history for student."""
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return Payment.objects.filter(
            student=self.request.user
        ).select_related('course').order_by('-initiated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = PaymentService.get_payment_stats(self.request.user)
        return context


class PaymentDetailView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    """Payment receipt/detail page."""
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'

    def get_queryset(self):
        return Payment.objects.filter(
            student=self.request.user
        ).select_related('course', 'enrollment').prefetch_related('logs')


# ==================== FUNCTION-BASED VIEWS ====================

@login_required
@require_POST
def initiate_payment(request, enrollment_id):
    """
    Initiate payment for an enrollment.
    Creates payment record and redirects to simulation.
    """
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        student=request.user,
        payment_status='pending'
    )

    try:
        payment = PaymentService.create_payment(
            enrollment=enrollment,
            payment_method=request.POST.get('payment_method', 'mobile_money'),
            phone_number=request.POST.get('phone_number', ''),
        )
        messages.success(request, _('Payment initiated! Redirecting to payment gateway...'))
        return redirect('payments:payment_simulator', payment_id=payment.id)

    except DuplicateEnrollmentError:
        existing_payment = getattr(enrollment, 'payment', None)
        if existing_payment and existing_payment.is_completed:
            messages.info(request, _('Payment already completed for this course.'))
            return redirect('courses:my_enrollments')
        elif existing_payment:
            return redirect('payments:payment_simulator', payment_id=existing_payment.id)

    except PaymentServiceError as e:
        messages.error(request, str(e))
        return redirect('payments:checkout', enrollment_id=enrollment_id)

@login_required
@require_POST
def process_simulated_payment(request, payment_id):
    """
    AJAX endpoint to process simulated payment.
    Returns JSON response with payment result.
    """
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user
    )

    try:
        result = PaymentService.simulate_payment_processing(payment)

        # Create notification message
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])

        return JsonResponse(result)

    except PaymentAlreadyProcessedError as e:
        return JsonResponse({
            'success': True,
            'status': 'completed',
            'message': str(e),
            'transaction_id': payment.transaction_id,
        })

    except PaymentServiceError as e:
        return JsonResponse({
            'success': False,
            'status': 'error',
            'message': str(e),
        }, status=400)


@login_required
@require_POST
def retry_payment(request, payment_id):
    """Retry a failed payment."""
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user
    )

    try:
        PaymentService.retry_payment(payment)
        messages.info(request, _('Payment retry initiated.'))
        return redirect('payments:payment_simulator', payment_id=payment.id)

    except PaymentServiceError as e:
        messages.error(request, str(e))
        return redirect('payments:payment_detail', payment_id=payment.id)


@login_required
@require_POST
def cancel_payment(request, payment_id):
    """Cancel a pending payment."""
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user
    )

    try:
        result = PaymentService.cancel_payment(payment)
        messages.info(request, result['message'])
    except PaymentServiceError as e:
        messages.error(request, str(e))

    return redirect('payments:checkout', enrollment_id=payment.enrollment.id)


@login_required
def check_payment_status(request, payment_id):
    """
    AJAX endpoint to check payment status.
    Used for polling during simulation.
    """
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user
    )

    return JsonResponse({
        'status': payment.status,
        'transaction_id': payment.transaction_id,
        'is_completed': payment.is_completed,
        'is_failed': payment.is_failed,
        'is_pending': payment.is_pending,
    })