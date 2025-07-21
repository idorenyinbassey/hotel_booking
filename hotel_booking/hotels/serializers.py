from rest_framework import serializers
from .models import Hotel, HotelImage, Location, Amenity, RoomType, Room, RoomImage, Review


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for the Amenity model."""
    
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'description', 'icon']


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for the Location model."""
    
    class Meta:
        model = Location
        fields = ['id', 'address', 'city', 'state', 'country', 'zip_code', 'latitude', 'longitude']


class HotelImageSerializer(serializers.ModelSerializer):
    """Serializer for the HotelImage model."""
    
    class Meta:
        model = HotelImage
        fields = ['id', 'image', 'caption', 'is_primary']


class RoomImageSerializer(serializers.ModelSerializer):
    """Serializer for the RoomImage model."""
    
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'caption', 'is_primary']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model."""
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'rating', 'title', 'comment', 'stay_date', 'created_at']
        read_only_fields = ['user', 'is_approved']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RoomTypeSerializer(serializers.ModelSerializer):
    """Serializer for the RoomType model."""
    
    amenities = AmenitySerializer(many=True, read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = RoomType
        fields = ['id', 'name', 'description', 'hotel', 'max_occupancy', 'base_price', 
                  'size_sqm', 'amenities', 'images']


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for the Room model."""
    
    room_type = RoomTypeSerializer(read_only=True)
    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all(), source='room_type', write_only=True
    )
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'room_type_id', 'hotel', 'floor', 'is_available', 'notes']


class HotelListSerializer(serializers.ModelSerializer):
    """Serializer for listing hotels."""
    
    location = LocationSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'description', 'location', 'star_rating', 
                  'primary_image', 'average_rating', 'featured']
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return HotelImageSerializer(primary_image).data
        return None


class HotelDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed hotel information."""
    
    location = LocationSerializer()
    amenities = AmenitySerializer(many=True, read_only=True)
    images = HotelImageSerializer(many=True, read_only=True)
    room_types = RoomTypeSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'description', 'location', 'star_rating', 'amenities',
                  'check_in_time', 'check_out_time', 'contact_email', 'contact_phone',
                  'website', 'images', 'room_types', 'reviews', 'average_rating', 'featured']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True)[:5]  # Get only 5 approved reviews
        return ReviewSerializer(reviews, many=True).data
    
    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location = Location.objects.create(**location_data)
        hotel = Hotel.objects.create(location=location, **validated_data)
        return hotel
    
    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data:
            location = instance.location
            for attr, value in location_data.items():
                setattr(location, attr, value)
            location.save()
        
        return super().update(instance, validated_data)