import logging
from django.conf import settings

# Get logger for the bookings app
logger = logging.getLogger('bookings')


def log_booking_activity(booking, action, user=None, details=None):
    """Log booking-related activities."""
    extra_data = {
        'booking_id': booking.id,
        'booking_number': booking.booking_number,
        'hotel_id': booking.hotel.id,
        'user_id': booking.user.id,
        'action': action,
        'actor_id': user.id if user else None,
    }
    
    if details:
        extra_data['details'] = details
    
    logger.info(
        f"Booking {action}: {booking.booking_number}",
        extra=extra_data
    )


def log_payment_activity(payment, action, user=None, details=None):
    """Log payment-related activities."""
    extra_data = {
        'payment_id': payment.id,
        'booking_id': payment.booking.id,
        'booking_number': payment.booking.booking_number,
        'amount': str(payment.amount),
        'payment_method': payment.payment_method,
        'action': action,
        'actor_id': user.id if user else None,
    }
    
    if details:
        extra_data['details'] = details
    
    logger.info(
        f"Payment {action}: {payment.id} for booking {payment.booking.booking_number}",
        extra=extra_data
    )


def log_system_error(error, context=None):
    """Log system errors with context."""
    extra_data = {'error_type': type(error).__name__}
    
    if context:
        extra_data.update(context)
    
    logger.error(
        f"System error: {str(error)}",
        extra=extra_data,
        exc_info=True
    )
