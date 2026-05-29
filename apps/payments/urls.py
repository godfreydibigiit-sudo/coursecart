"""
URL patterns for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Checkout & Payment Flow
    path(
        'checkout/<int:enrollment_id>/',
        views.PaymentCheckoutView.as_view(),
        name='checkout',
    ),
    path(
        'simulate/<int:payment_id>/',
        views.PaymentSimulatorView.as_view(),
        name='payment_simulator',
    ),
    
    # Payment Actions
    path(
        'initiate/<int:enrollment_id>/',
        views.initiate_payment,
        name='initiate_payment',
    ),
    path(
        'process/<int:payment_id>/',
        views.process_simulated_payment,
        name='process_payment',
    ),
    path(
        'retry/<int:payment_id>/',
        views.retry_payment,
        name='retry_payment',
    ),
    path(
        'cancel/<int:payment_id>/',
        views.cancel_payment,
        name='cancel_payment',
    ),
    
    # Payment History & Details
    path(
        'history/',
        views.PaymentHistoryView.as_view(),
        name='payment_history',
    ),
    path(
        'detail/<int:payment_id>/',
        views.PaymentDetailView.as_view(),
        name='payment_detail',
    ),
    
    # AJAX Endpoints
    path(
        'status/<int:payment_id>/',
        views.check_payment_status,
        name='payment_status',
    ),
]