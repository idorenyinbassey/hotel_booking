from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, AmenityViewSet, RoomTypeViewSet, RoomViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'amenities', AmenityViewSet)
router.register(r'', HotelViewSet)
router.register(r'room-types', RoomTypeViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]