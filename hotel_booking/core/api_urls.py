from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import HealthCheckView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]