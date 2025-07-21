from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel


class Amenity(BaseModel):
    """
    Model for hotel and room amenities.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # FontAwesome icon name
    
    class Meta:
        verbose_name_plural = 'Amenities'
    
    def __str__(self):
        return self.name


class Location(BaseModel):
    """
    Model for hotel locations.
    """
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country}"


class Hotel(BaseModel):
    """
    Model for hotels.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='hotel')
    star_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Hotel star rating (1-5)"
    )
    amenities = models.ManyToManyField(Amenity, related_name='hotels')
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='11:00')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def total_rooms(self):
        return self.rooms.count()


class HotelImage(BaseModel):
    """
    Model for hotel images.
    """
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotel_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.hotel.name}"


class RoomType(BaseModel):
    """
    Model for room types.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    max_occupancy = models.PositiveSmallIntegerField(default=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    size_sqm = models.PositiveSmallIntegerField(help_text="Size in square meters")
    amenities = models.ManyToManyField(Amenity, related_name='room_types')
    
    def __str__(self):
        return f"{self.name} at {self.hotel.name}"


class Room(BaseModel):
    """
    Model for individual rooms.
    """
    room_number = models.CharField(max_length=20)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    floor = models.PositiveSmallIntegerField()
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('hotel', 'room_number')
    
    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.name}) at {self.hotel.name}"


class RoomImage(BaseModel):
    """
    Model for room images.
    """
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.room_type.name}"


class Review(BaseModel):
    """
    Model for hotel reviews.
    """
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    title = models.CharField(max_length=255)
    comment = models.TextField()
    stay_date = models.DateField()
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.hotel.name}"