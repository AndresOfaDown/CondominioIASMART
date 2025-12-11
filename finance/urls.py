from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeConfigurationViewSet, FeeViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'configurations', FeeConfigurationViewSet, basename='fee-configuration')
router.register(r'fees', FeeViewSet, basename='fee')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
