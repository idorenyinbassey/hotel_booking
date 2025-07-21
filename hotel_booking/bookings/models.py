from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel


class Booking(BaseModel):
    """
    Model for hotel bookings.
    """
    # Booking status choices
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CHECKED_IN = 'checked_in'
    STATUS_CHECKED_OUT = 'checked_out'
    STATUS_CANCELLED = 'cancelled'
    STATUS_NO_SHOW = 'no_show'
    
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CHECKED_IN, 'Checked In'),
        (STATUS_CHECKED_OUT, 'Checked Out'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_NO_SHOW, 'No Show'),
    )
    
    # Payment status choices
    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_PARTIALLY_PAID = 'partially_paid'
    PAYMENT_REFUNDED = 'refunded'
    PAYMENT_FAILED = 'failed'
    
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_PARTIALLY_PAID, 'Partially Paid'),
        (PAYMENT_REFUNDED, 'Refunded'),
        (PAYMENT_FAILED, 'Failed'),
    )
    
    # Booking source choices
    SOURCE_WEBSITE = 'website'
    SOURCE_MOBILE_APP = 'mobile_app'
    SOURCE_PHONE = 'phone'
    SOURCE_WALK_IN = 'walk_in'
    SOURCE_THIRD_PARTY = 'third_party'
    
    SOURCE_CHOICES = (
        (SOURCE_WEBSITE, 'Website'),
        (SOURCE_MOBILE_APP, 'Mobile App'),
        (SOURCE_PHONE, 'Phone'),
        (SOURCE_WALK_IN, 'Walk-in'),
        (SOURCE_THIRD_PARTY, 'Third Party'),
    )
    
    # Booking fields
    booking_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    children = models.PositiveSmallIntegerField(default=0)
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    booking_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_WEBSITE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps for status changes
    confirmed_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking #{self.booking_number} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Generate booking number if not set
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        super().save(*args, **kwargs)
    
    def generate_booking_number(self):
        """Generate a unique booking number."""
        now = timezone.now()
        return f"BK{now.strftime('%Y%m%d')}{now.strftime('%H%M%S')}"
    
    def confirm(self):
        """Confirm the booking."""
        self.status = self.STATUS_CONFIRMED
        self.confirmed_at = timezone.now()
        self.save()
    
    def check_in(self):
        """Check in the guest."""
        self.status = self.STATUS_CHECKED_IN
        self.checked_in_at = timezone.now()
        self.save()
    
    def check_out(self):
        """Check out the guest."""
        self.status = self.STATUS_CHECKED_OUT
        self.checked_out_at = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancel the booking."""
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = timezone.now()
        self.save()
    
    def mark_as_no_show(self):
        """Mark the booking as no show."""
        self.status = self.STATUS_NO_SHOW
        self.save()
    
    def record_payment(self, amount):
        """Record a payment for the booking."""
        self.paid_amount += amount
        
        if self.paid_amount >= self.total_price:
            self.payment_status = self.PAYMENT_PAID
        elif self.paid_amount > 0:
            self.payment_status = self.PAYMENT_PARTIALLY_PAID
        
        self.save()
        
        # Create payment record
        Payment.objects.create(
            booking=self,
            amount=amount,
            payment_method='credit_card',  # Default method
            status='completed'
        )
    
    @property
    def duration_days(self):
        """Calculate the duration of the stay in days."""
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def balance_due(self):
        """Calculate the remaining balance due."""
        return max(0, self.total_price - self.paid_amount)
    
    @property
    def is_upcoming(self):
        """Check if the booking is upcoming."""
        return self.check_in_date > timezone.now().date() and self.status not in [
            self.STATUS_CANCELLED, self.STATUS_NO_SHOW
        ]
    
    @property
    def is_active(self):
        """Check if the booking is currently active."""
        today = timezone.now().date()
        return (
            self.check_in_date <= today <= self.check_out_date and 
            self.status not in [self.STATUS_CANCELLED, self.STATUS_CHECKED_OUT, self.STATUS_NO_SHOW]
        )


class Payment(BaseModel):
    """
    Model for booking payments.
    """
    # Payment method choices
    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_DEBIT_CARD = 'debit_card'
    METHOD_PAYPAL = 'paypal'
    METHOD_BANK_TRANSFER = 'bank_transfer'
    METHOD_CASH = 'cash'
    
    METHOD_CHOICES = (
        (METHOD_CREDIT_CARD, 'Credit Card'),
        (METHOD_DEBIT_CARD, 'Debit Card'),
        (METHOD_PAYPAL, 'PayPal'),
        (METHOD_BANK_TRANSFER, 'Bank Transfer'),
        (METHOD_CASH, 'Cash'),
    )
    
    # Payment status choices
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.booking.booking_number}"