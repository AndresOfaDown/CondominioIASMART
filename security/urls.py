from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CameraViewSet, VehicleViewSet, AccessLogViewSet, SecurityIncidentViewSet

router = DefaultRouter()
router.register(r'cameras', CameraViewSet, basename='camera')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'access-logs', AccessLogViewSet, basename='accesslog')
router.register(r'incidents', SecurityIncidentViewSet, basename='securityincident')

urlpatterns = [
    path('', include(router.urls)),
]
