from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommonAreaViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r'areas', CommonAreaViewSet, basename='commonarea')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]
