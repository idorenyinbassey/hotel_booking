from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from .models import Hotel, Amenity, RoomType, Room, Review
from .serializers import (
    HotelListSerializer, HotelDetailSerializer, AmenitySerializer,
    RoomTypeSerializer, RoomSerializer, ReviewSerializer
)
from .permissions import IsHotelManagerOrReadOnly, IsOwnerOrReadOnly


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for amenities.
    """
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticated]


class HotelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for hotels.
    """
    queryset = Hotel.objects.filter(is_active=True, is_deleted=False)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['star_rating', 'featured', 'location__city', 'location__country']
    search_fields = ['name', 'description', 'location__city', 'location__country']
    ordering_fields = ['name', 'star_rating', 'created_at']
    permission_classes = [IsHotelManagerOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset().annotate(average_rating=Avg('reviews__rating'))
        
        # Filter by amenities
        amenities = self.request.query_params.getlist('amenities')
        if amenities:
            queryset = queryset.filter(amenities__id__in=amenities).distinct()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(room_types__base_price__gte=min_price).distinct()
        if max_price:
            queryset = queryset.filter(room_types__base_price__lte=max_price).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HotelListSerializer
        return HotelDetailSerializer
    
    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """
        Get all rooms for a hotel.
        """
        hotel = self.get_object()
        rooms = Room.objects.filter(hotel=hotel)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def reviews(self, request, pk=None):
        """
        Get all reviews for a hotel or create a new review.
        """
        hotel = self.get_object()
        
        if request.method == 'GET':
            reviews = hotel.reviews.filter(is_approved=True)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ReviewSerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save(hotel=hotel)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for room types.
    """
    queryset = RoomType.objects.filter(is_deleted=False)
    serializer_class = RoomTypeSerializer
    permission_classes = [IsHotelManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hotel', 'max_occupancy']
    ordering_fields = ['base_price', 'max_occupancy']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        # Filter by amenities
        amenities = self.request.query_params.getlist('amenities')
        if amenities:
            queryset = queryset.filter(amenities__id__in=amenities).distinct()
        
        return queryset


class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for rooms.
    """
    queryset = Room.objects.filter(is_deleted=False)
    serializer_class = RoomSerializer
    permission_classes = [IsHotelManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hotel', 'room_type', 'floor', 'is_available']


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reviews.
    """
    queryset = Review.objects.filter(is_deleted=False)
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hotel', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(is_approved=True)