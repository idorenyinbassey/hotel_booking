from rest_framework import serializers
from django.core.validators import validate_email
from django.utils import timezone
from datetime import datetime, timedelta


class BookingValidationMixin:
    """Mixin for booking validation logic."""
    
    def validate_dates(self, attrs):
        """Validate check-in and check-out dates."""
        check_in_date = attrs.get('check_in_date')
        check_out_date = attrs.get('check_out_date')
        
        if not check_in_date or not check_out_date:
            raise serializers.ValidationError(
                "Both check-in and check-out dates are required."
            )
        
        # Check if dates are in the future
        today = timezone.now().date()
        if check_in_date < today:
            raise serializers.ValidationError(
                "Check-in date cannot be in the past."
            )
        
        # Check if check-out is after check-in
        if check_out_date <= check_in_date:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        
        # Check maximum stay duration (e.g., 30 days)
        max_duration = timedelta(days=30)
        if check_out_date - check_in_date > max_duration:
            raise serializers.ValidationError(
                f"Maximum stay duration is {max_duration.days} days."
            )
        
        return attrs
    
    def validate_room_availability(self, attrs):
        """Validate room availability for the given dates."""
        room = attrs.get('room')
        check_in_date = attrs.get('check_in_date')
        check_out_date = attrs.get('check_out_date')
        
        if not all([room, check_in_date, check_out_date]):
            return attrs
        
        # Check for overlapping bookings
        from .models import Booking
        
        overlapping_bookings = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'checked_in'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        )
        
        # Exclude current booking if updating
        if hasattr(self, 'instance') and self.instance:
            overlapping_bookings = overlapping_bookings.exclude(
                pk=self.instance.pk
            )
        
        if overlapping_bookings.exists():
            raise serializers.ValidationError(
                "Room is not available for the selected dates."
            )
        
        return attrs
    
    def validate_occupancy(self, attrs):
        """Validate number of guests against room capacity."""
        room = attrs.get('room')
        adults = attrs.get('adults', 0)
        children = attrs.get('children', 0)
        
        if not room:
            return attrs
        
        total_guests = adults + children
        max_occupancy = room.room_type.max_occupancy
        
        if total_guests > max_occupancy:
            raise serializers.ValidationError(
                f"Room capacity is {max_occupancy} guests. "
                f"You have selected {total_guests} guests."
            )
        
        return attrs


class EnhancedBookingSerializer(serializers.ModelSerializer, BookingValidationMixin):
    """Enhanced booking serializer with comprehensive validation."""
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs = self.validate_dates(attrs)
        attrs = self.validate_room_availability(attrs)
        attrs = self.validate_occupancy(attrs)
        return attrs
    
    def validate_special_requests(self, value):
        """Validate special requests field."""
        if value and len(value) > 500:
            raise serializers.ValidationError(
                "Special requests cannot exceed 500 characters."
            )
        return value


class ContactInfoValidator:
    """Validator for contact information."""
    
    @staticmethod
    def validate_phone_number(phone_number):
        """Validate phone number format."""
        import re
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone_number)
        
        # Check length (should be between 10-15 digits)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10-15 digits."
            )
        
        return phone_number
    
    @staticmethod
    def validate_email_domain(email):
        """Validate email domain against blacklist."""
        validate_email(email)
        
        # Add domain blacklist if needed
        blacklisted_domains = ['tempmail.com', '10minutemail.com']
        domain = email.split('@')[1].lower()
        
        if domain in blacklisted_domains:
            raise serializers.ValidationError(
                "Email from this domain is not allowed."
            )
        
        return email
