"""
Service layer for business logic separation.
This prepares the application for potential microservices architecture.
"""

from django.db import transaction
from django.utils import timezone
from typing import Optional, List, Dict
from .models import Booking, Payment, Hotel, Room
from .exceptions import BookingError, PaymentError


class BookingService:
    """Service class for booking-related business logic."""
    
    @staticmethod
    @transaction.atomic
    def create_booking(user, hotel_id: int, room_id: int, 
                      check_in_date, check_out_date, 
                      adults: int, children: int = 0,
                      special_requests: str = '') -> Booking:
        """
        Create a new booking with all validations.
        """
        try:
            hotel = Hotel.objects.get(id=hotel_id, is_active=True)
            room = Room.objects.get(id=room_id, hotel=hotel, is_available=True)
            
            # Calculate total price
            duration = (check_out_date - check_in_date).days
            total_price = room.room_type.base_price * duration
            
            # Create booking
            booking = Booking.objects.create(
                user=user,
                hotel=hotel,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                adults=adults,
                children=children,
                special_requests=special_requests,
                total_price=total_price,
                status=Booking.STATUS_PENDING
            )
            
            # Send confirmation email (async)
            from .tasks import send_booking_confirmation_email
            send_booking_confirmation_email.delay(booking.id)
            
            return booking
            
        except Hotel.DoesNotExist:
            raise BookingError("Hotel not found or not available")
        except Room.DoesNotExist:
            raise BookingError("Room not found or not available")
    
    @staticmethod
    @transaction.atomic
    def confirm_booking(booking_id: int, manager_user) -> Booking:
        """Confirm a booking (hotel manager action)."""
        try:
            booking = Booking.objects.get(id=booking_id)
            
            if booking.status != Booking.STATUS_PENDING:
                raise BookingError(f"Cannot confirm booking in {booking.status} status")
            
            booking.confirm()
            
            # Log activity
            from core.logging import log_booking_activity
            log_booking_activity(
                booking, 'CONFIRMED', 
                user=manager_user,
                details={'confirmed_by': manager_user.email}
            )
            
            return booking
            
        except Booking.DoesNotExist:
            raise BookingError("Booking not found")
    
    @staticmethod
    def get_available_rooms(hotel_id: int, check_in_date, 
                          check_out_date) -> List[Room]:
        """Get available rooms for given dates."""
        # Get all rooms for the hotel
        rooms = Room.objects.filter(
            hotel_id=hotel_id, 
            is_available=True
        ).select_related('room_type')
        
        # Filter out rooms with conflicting bookings
        available_rooms = []
        for room in rooms:
            conflicting_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'checked_in'],
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            if not conflicting_bookings.exists():
                available_rooms.append(room)
        
        return available_rooms


class PaymentService:
    """Service class for payment-related business logic."""
    
    @staticmethod
    @transaction.atomic
    def process_payment(booking_id: int, amount: float, 
                       payment_method: str, 
                       transaction_id: Optional[str] = None) -> Payment:
        """Process a payment for a booking."""
        try:
            booking = Booking.objects.get(id=booking_id)
            
            if amount <= 0:
                raise PaymentError("Payment amount must be positive")
            
            if amount > booking.balance_due:
                raise PaymentError("Payment amount exceeds balance due")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                status=Payment.STATUS_COMPLETED
            )
            
            # Update booking payment status
            booking.record_payment(amount)
            
            # Send receipt email
            from .tasks import send_payment_receipt_email
            send_payment_receipt_email.delay(payment.id)
            
            return payment
            
        except Booking.DoesNotExist:
            raise PaymentError("Booking not found")


class HotelService:
    """Service class for hotel-related business logic."""
    
    @staticmethod
    def search_hotels(location: str = None, 
                     check_in_date=None, check_out_date=None,
                     guests: int = 1, amenities: List[int] = None,
                     min_price: float = None, max_price: float = None) -> List[Hotel]:
        """
        Advanced hotel search with availability check.
        """
        queryset = Hotel.objects.filter(is_active=True).select_related('location')
        
        # Location filter
        if location:
            queryset = queryset.filter(
                location__city__icontains=location
            ) | queryset.filter(
                location__country__icontains=location
            )
        
        # Price filter
        if min_price or max_price:
            price_filter = {}
            if min_price:
                price_filter['room_types__base_price__gte'] = min_price
            if max_price:
                price_filter['room_types__base_price__lte'] = max_price
            queryset = queryset.filter(**price_filter).distinct()
        
        # Amenities filter
        if amenities:
            queryset = queryset.filter(amenities__id__in=amenities).distinct()
        
        # Availability filter (if dates provided)
        if check_in_date and check_out_date:
            available_hotels = []
            for hotel in queryset:
                available_rooms = BookingService.get_available_rooms(
                    hotel.id, check_in_date, check_out_date
                )
                # Check if any room can accommodate the guests
                suitable_rooms = [
                    room for room in available_rooms 
                    if room.room_type.max_occupancy >= guests
                ]
                if suitable_rooms:
                    available_hotels.append(hotel)
            
            return available_hotels
        
        return list(queryset)
    
    @staticmethod
    def get_hotel_analytics(hotel_id: int) -> Dict:
        """Get analytics data for a hotel."""
        try:
            hotel = Hotel.objects.get(id=hotel_id)
            
            # Booking statistics
            total_bookings = hotel.bookings.count()
            revenue_this_month = hotel.bookings.filter(
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month,
                payment_status='paid'
            ).aggregate(
                total=models.Sum('total_price')
            )['total'] or 0
            
            # Occupancy rate
            total_rooms = hotel.rooms.count()
            occupied_rooms = hotel.bookings.filter(
                check_in_date__lte=timezone.now().date(),
                check_out_date__gt=timezone.now().date(),
                status='checked_in'
            ).count()
            
            occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            return {
                'total_bookings': total_bookings,
                'revenue_this_month': revenue_this_month,
                'occupancy_rate': round(occupancy_rate, 2),
                'total_rooms': total_rooms,
                'occupied_rooms': occupied_rooms,
                'average_rating': hotel.average_rating
            }
            
        except Hotel.DoesNotExist:
            raise BookingError("Hotel not found")
