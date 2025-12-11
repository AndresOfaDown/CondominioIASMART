from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ResidentialUnitViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'units', ResidentialUnitViewSet, basename='unit')

urlpatterns = [
    path('', include(router.urls)),
]
