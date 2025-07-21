from rest_framework import serializers
from django.utils import timezone
from .models import Booking, Payment
from hotels.serializers import HotelListSerializer, RoomSerializer
from hotels.models import Room


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""
    
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_method', 'transaction_id', 
                  'status', 'payment_date', 'notes']
        read_only_fields = ['payment_date']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for the Booking model."""
    
    hotel_details = HotelListSerializer(source='hotel', read_only=True)
    room_details = RoomSerializer(source='room', read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'user', 'hotel', 'hotel_details', 'room', 'room_details',
                  'check_in_date', 'check_out_date', 'adults', 'children', 'special_requests',
                  'status', 'payment_status', 'booking_source', 'total_price', 'paid_amount',
                  'confirmed_at', 'checked_in_at', 'checked_out_at', 'cancelled_at',
                  'duration_days', 'balance_due', 'is_upcoming', 'is_active', 'created_at']
        read_only_fields = ['booking_number', 'confirmed_at', 'checked_in_at', 
                           'checked_out_at', 'cancelled_at', 'paid_amount']
    
    def validate(self, data):
        # Check that check_out_date is after check_in_date
        if data.get('check_in_date') and data.get('check_out_date'):
            if data['check_out_date'] <= data['check_in_date']:
                raise serializers.ValidationError({
                    "check_out_date": "Check-out date must be after check-in date."
                })
        
        # Check that check_in_date is not in the past
        if data.get('check_in_date') and data['check_in_date'] < timezone.now().date():
            raise serializers.ValidationError({
                "check_in_date": "Check-in date cannot be in the past."
            })
        
        # Check room availability
        if self.instance is None:  # Only for new bookings
            room = data.get('room')
            check_in_date = data.get('check_in_date')
            check_out_date = data.get('check_out_date')
            
            if room and check_in_date and check_out_date:
                # Check if room is available for the given dates
                overlapping_bookings = Booking.objects.filter(
                    room=room,
                    check_in_date__lt=check_out_date,
                    check_out_date__gt=check_in_date,
                    status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED, Booking.STATUS_CHECKED_IN]
                )
                
                if overlapping_bookings.exists():
                    raise serializers.ValidationError({
                        "room": "This room is not available for the selected dates."
                    })
        
        return data
    
    def create(self, validated_data):
        # Calculate total price based on room rate and duration
        room = validated_data.get('room')
        check_in_date = validated_data.get('check_in_date')
        check_out_date = validated_data.get('check_out_date')
        
        duration = (check_out_date - check_in_date).days
        base_price = room.room_type.base_price
        total_price = base_price * duration
        
        # Set the user to the current user if not provided
        if 'user' not in validated_data and self.context.get('request'):
            validated_data['user'] = self.context['request'].user
        
        # Set the hotel based on the room
        validated_data['hotel'] = room.hotel
        
        # Set the total price
        validated_data['total_price'] = total_price
        
        return super().create(validated_data)


class BookingCreateSerializer(BookingSerializer):
    """Serializer for creating bookings."""
    
    class Meta(BookingSerializer.Meta):
        fields = ['room', 'check_in_date', 'check_out_date', 'adults', 'children', 'special_requests']


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking status."""
    
    class Meta:
        model = Booking
        fields = ['status']
    
    def validate_status(self, value):
        valid_transitions = {
            Booking.STATUS_PENDING: [Booking.STATUS_CONFIRMED, Booking.STATUS_CANCELLED],
            Booking.STATUS_CONFIRMED: [Booking.STATUS_CHECKED_IN, Booking.STATUS_CANCELLED, Booking.STATUS_NO_SHOW],
            Booking.STATUS_CHECKED_IN: [Booking.STATUS_CHECKED_OUT],
            Booking.STATUS_CHECKED_OUT: [],
            Booking.STATUS_CANCELLED: [],
            Booking.STATUS_NO_SHOW: [],
        }
        
        current_status = self.instance.status
        if value not in valid_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}. "
                f"Valid transitions are: {', '.join(valid_transitions[current_status])}"
            )
        
        return value
    
    def update(self, instance, validated_data):
        status = validated_data.get('status')
        
        if status == Booking.STATUS_CONFIRMED:
            instance.confirm()
        elif status == Booking.STATUS_CHECKED_IN:
            instance.check_in()
        elif status == Booking.STATUS_CHECKED_OUT:
            instance.check_out()
        elif status == Booking.STATUS_CANCELLED:
            instance.cancel()
        elif status == Booking.STATUS_NO_SHOW:
            instance.mark_as_no_show()
        
        return instance


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'payment_method', 'transaction_id', 'notes']
    
    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')
        
        if booking and amount:
            if amount <= 0:
                raise serializers.ValidationError({
                    "amount": "Payment amount must be greater than zero."
                })
            
            if amount > booking.balance_due:
                raise serializers.ValidationError({
                    "amount": f"Payment amount cannot exceed the balance due ({booking.balance_due})."
                })
        
        return data
    
    def create(self, validated_data):
        validated_data['status'] = Payment.STATUS_COMPLETED
        return super().create(validated_data)