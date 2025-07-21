from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Booking, Payment


@receiver(pre_save, sender=Booking)
def update_room_availability(sender, instance, **kwargs):
    """
    Update room availability when a booking is created or updated.
    """
    if instance.pk:  # Existing booking
        try:
            old_instance = Booking.objects.get(pk=instance.pk)
            
            # If status changed to cancelled or no_show, make the room available
            if instance.status in [Booking.STATUS_CANCELLED, Booking.STATUS_NO_SHOW] and \
               old_instance.status not in [Booking.STATUS_CANCELLED, Booking.STATUS_NO_SHOW]:
                instance.room.is_available = True
                instance.room.save()
            
            # If room changed, update availability of both rooms
            if old_instance.room != instance.room:
                old_instance.room.is_available = True
                old_instance.room.save()
                
                if instance.status not in [Booking.STATUS_CANCELLED, Booking.STATUS_NO_SHOW, Booking.STATUS_CHECKED_OUT]:
                    instance.room.is_available = False
                    instance.room.save()
                
        except Booking.DoesNotExist:
            pass
    else:  # New booking
        if instance.status not in [Booking.STATUS_CANCELLED, Booking.STATUS_NO_SHOW]:
            instance.room.is_available = False
            instance.room.save()


@receiver(post_save, sender=Payment)
def update_booking_payment_status(sender, instance, created, **kwargs):
    """
    Update booking payment status when a payment is created or updated.
    """
    if created and instance.status == Payment.STATUS_COMPLETED:
        booking = instance.booking
        total_paid = booking.payments.filter(status=Payment.STATUS_COMPLETED).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        booking.paid_amount = total_paid
        
        if total_paid >= booking.total_price:
            booking.payment_status = Booking.PAYMENT_PAID
        elif total_paid > 0:
            booking.payment_status = Booking.PAYMENT_PARTIALLY_PAID
        else:
            booking.payment_status = Booking.PAYMENT_PENDING
        
        booking.save()