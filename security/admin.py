from django.contrib import admin
from .models import Camera, Vehicle, AccessLog, SecurityIncident


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'camera_type', 'is_active', 'has_facial_recognition', 'has_ocr']
    list_filter = ['camera_type', 'is_active', 'has_facial_recognition', 'has_ocr']
    search_fields = ['name', 'location']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'owner', 'brand', 'model', 'is_authorized', 'created_at']
    list_filter = ['is_authorized', 'brand']
    search_fields = ['plate_number', 'owner__username', 'brand', 'model']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'access_type', 'detection_method', 'is_resident', 'plate_detected', 'visitor_name']
    list_filter = ['access_type', 'detection_method', 'is_resident']
    search_fields = ['plate_detected', 'visitor_name', 'user__username']
    date_hierarchy = 'timestamp'


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'incident_type', 'severity', 'resolved', 'resolved_by']
    list_filter = ['incident_type', 'severity', 'resolved']
    search_fields = ['description']
    date_hierarchy = 'timestamp'
