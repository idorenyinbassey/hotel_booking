from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Booking, Payment
from .serializers import BookingSerializer, PaymentSerializer
from hotels.models import Room
from users.permissions import IsCustomer, IsHotelManager


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Customers can view, create, and manage their own bookings.
    Hotel managers can view and manage bookings for their hotels.
    """
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'hotel', 'room', 'booking_source']
    search_fields = ['booking_number', 'special_requests', 'user__username', 'user__email']
    ordering_fields = ['check_in_date', 'check_out_date', 'created_at', 'total_price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Add computed fields
        queryset = Booking.objects.all()
        queryset = queryset.annotate_duration_days()
        queryset = queryset.annotate_balance_due()
        queryset = queryset.annotate_is_upcoming()
        queryset = queryset.annotate_is_active()
        
        # Filter based on user role
        if user.is_staff or user.is_superuser:
            return queryset
        elif hasattr(user, 'hotel_manager'):
            # Hotel managers can only see bookings for their hotels
            return queryset.filter(hotel__in=user.hotel_manager.hotels.all())
        else:
            # Regular users can only see their own bookings
            return queryset.filter(user=user)
    
    def perform_create(self, serializer):
        # Set the user to the current user if not provided
        if not self.request.user.is_staff and not hasattr(self.request.user, 'hotel_manager'):
            serializer.save(user=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking."""
        booking = self.get_object()
        
        if booking.status != Booking.STATUS_PENDING:
            return Response(
                {"detail": f"Cannot confirm booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.STATUS_CONFIRMED
        booking.confirmed_at = timezone.now()
        booking.save()
        
        return Response(BookingSerializer(booking).data)
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a guest."""
        booking = self.get_object()
        
        if booking.status != Booking.STATUS_CONFIRMED:
            return Response(
                {"detail": f"Cannot check in booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.STATUS_CHECKED_IN
        booking.checked_in_at = timezone.now()
        booking.save()
        
        return Response(BookingSerializer(booking).data)
    
    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Check out a guest."""
        booking = self.get_object()
        
        if booking.status != Booking.STATUS_CHECKED_IN:
            return Response(
                {"detail": f"Cannot check out booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.STATUS_CHECKED_OUT
        booking.checked_out_at = timezone.now()
        booking.save()
        
        return Response(BookingSerializer(booking).data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        
        if booking.status in [Booking.STATUS_CHECKED_OUT, Booking.STATUS_CANCELLED, Booking.STATUS_NO_SHOW]:
            return Response(
                {"detail": f"Cannot cancel booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.STATUS_CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save()
        
        return Response(BookingSerializer(booking).data)
    
    @action(detail=True, methods=['post'])
    def mark_no_show(self, request, pk=None):
        """Mark a booking as no-show."""
        booking = self.get_object()
        
        if booking.status != Booking.STATUS_CONFIRMED:
            return Response(
                {"detail": f"Cannot mark as no-show a booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.STATUS_NO_SHOW
        booking.save()
        
        return Response(BookingSerializer(booking).data)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    
    Customers can view their own payments.
    Hotel managers can view and manage payments for their hotels.
    """
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'booking']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return Payment.objects.all()
        elif hasattr(user, 'hotel_manager'):
            # Hotel managers can only see payments for their hotels
            managed_hotels = user.hotel_manager.hotels.all()
            return Payment.objects.filter(booking__hotel__in=managed_hotels)
        else:
            # Regular users can only see their own payments
            return Payment.objects.filter(booking__user=user)