from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task


@shared_task
def send_booking_confirmation_email(booking_id):
    """Send booking confirmation email to customer."""
    from .models import Booking
    
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Confirmation - {booking.booking_number}'
        html_message = render_to_string('bookings/emails/booking_confirmation.html', {
            'booking': booking,
            'user': booking.user,
        })
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Confirmation email sent for booking {booking.booking_number}"
        
    except Booking.DoesNotExist:
        return f"Booking with id {booking_id} does not exist"


@shared_task
def send_booking_reminder_email(booking_id):
    """Send booking reminder email 24 hours before check-in."""
    from .models import Booking
    
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Check-in Reminder - {booking.booking_number}'
        html_message = render_to_string('bookings/emails/booking_reminder.html', {
            'booking': booking,
            'user': booking.user,
        })
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Reminder email sent for booking {booking.booking_number}"
        
    except Booking.DoesNotExist:
        return f"Booking with id {booking_id} does not exist"


@shared_task
def send_payment_receipt_email(payment_id):
    """Send payment receipt email to customer."""
    from .models import Payment
    
    try:
        payment = Payment.objects.get(id=payment_id)
        booking = payment.booking
        
        subject = f'Payment Receipt - {booking.booking_number}'
        html_message = render_to_string('bookings/emails/payment_receipt.html', {
            'payment': payment,
            'booking': booking,
            'user': booking.user,
        })
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Receipt email sent for payment {payment.id}"
        
    except Payment.DoesNotExist:
        return f"Payment with id {payment_id} does not exist"
