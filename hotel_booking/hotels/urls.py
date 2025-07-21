from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, AmenityViewSet, RoomTypeViewSet, RoomViewSet, ReviewViewSet, HotelListView

router = DefaultRouter()
router.register(r'amenities', AmenityViewSet)
router.register(r'', HotelViewSet)
router.register(r'room-types', RoomTypeViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('list/', HotelListView.as_view(), name='hotel_list'),  # Web view for hotel list
    path('', include(router.urls)),
]