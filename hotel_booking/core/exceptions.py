"""
Custom exceptions for the hotel booking application.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class BookingError(Exception):
    """Base exception for booking-related errors."""
    pass


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    pass


class RoomUnavailableError(BookingError):
    """Raised when a room is not available for booking."""
    pass


class InvalidDateRangeError(BookingError):
    """Raised when booking date range is invalid."""
    pass


class InsufficientPaymentError(PaymentError):
    """Raised when payment amount is insufficient."""
    pass


class PaymentProcessingError(PaymentError):
    """Raised when payment processing fails."""
    pass


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it means the exception wasn't handled by DRF
    if response is None:
        # Handle custom business logic exceptions
        if isinstance(exc, BookingError):
            response = Response({
                'error': 'booking_error',
                'message': str(exc),
                'details': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, PaymentError):
            response = Response({
                'error': 'payment_error',
                'message': str(exc),
                'details': None
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        elif isinstance(exc, ValidationError):
            response = Response({
                'error': 'validation_error',
                'message': 'Invalid data provided',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            # Log unexpected errors
            logger.error(
                f"Unexpected error in {context['view'].__class__.__name__}: {str(exc)}",
                exc_info=True,
                extra={
                    'view': context['view'].__class__.__name__,
                    'request_method': context['request'].method,
                    'request_path': context['request'].path,
                }
            )
            
            response = Response({
                'error': 'internal_error',
                'message': 'An unexpected error occurred',
                'details': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        # Customize the existing DRF error response format
        if hasattr(response, 'data'):
            custom_response_data = {
                'error': 'validation_error',
                'message': 'Request validation failed',
                'details': response.data
            }
            
            # Handle specific error types
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                custom_response_data = {
                    'error': 'authentication_error',
                    'message': 'Authentication credentials were not provided or are invalid',
                    'details': response.data
                }
            elif response.status_code == status.HTTP_403_FORBIDDEN:
                custom_response_data = {
                    'error': 'permission_error',
                    'message': 'You do not have permission to perform this action',
                    'details': response.data
                }
            elif response.status_code == status.HTTP_404_NOT_FOUND:
                custom_response_data = {
                    'error': 'not_found',
                    'message': 'The requested resource was not found',
                    'details': response.data
                }
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                custom_response_data = {
                    'error': 'rate_limit_exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'details': response.data
                }
            
            response.data = custom_response_data
    
    # Add request ID for tracking
    if hasattr(context['request'], 'META'):
        request_id = context['request'].META.get('HTTP_X_REQUEST_ID', 'unknown')
        response.data['request_id'] = request_id
    
    # Add timestamp
    from django.utils import timezone
    response.data['timestamp'] = timezone.now().isoformat()
    
    return response


class ValidationMixin:
    """
    Mixin that provides common validation methods for serializers.
    """
    
    def validate_future_date(self, date_value, field_name="date"):
        """Validate that a date is in the future."""
        from django.utils import timezone
        
        if date_value < timezone.now().date():
            raise ValidationError(f"{field_name.title()} cannot be in the past.")
        return date_value
    
    def validate_date_range(self, start_date, end_date, 
                           start_field="start_date", end_field="end_date"):
        """Validate that end date is after start date."""
        if end_date <= start_date:
            raise ValidationError(
                f"{end_field.replace('_', ' ').title()} must be after "
                f"{start_field.replace('_', ' ').lower()}."
            )
        return start_date, end_date
    
    def validate_positive_number(self, value, field_name="value"):
        """Validate that a number is positive."""
        if value <= 0:
            raise ValidationError(f"{field_name.title()} must be a positive number.")
        return value
    
    def validate_max_length(self, value, max_length, field_name="field"):
        """Validate maximum length of a string."""
        if len(str(value)) > max_length:
            raise ValidationError(
                f"{field_name.title()} cannot exceed {max_length} characters."
            )
        return value
