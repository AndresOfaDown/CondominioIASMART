from rest_framework import serializers
from .models import Vehicle, AccessLog, SecurityIncident, Camera
from users.serializers import UsuarioSerializer


class CameraSerializer(serializers.ModelSerializer):
    """Serializer para Camera"""
    incidents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Camera
        fields = [
            'id', 'name', 'location', 'camera_type', 'ip_address',
            'is_active', 'has_facial_recognition', 'has_ocr',
            'has_anomaly_detection', 'incidents_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_incidents_count(self, obj):
        """Contar incidentes relacionados con esta cámara"""
        return obj.securityincident_set.count()


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer completo para Vehicle"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    unit_number = serializers.CharField(source='unit.unit_number', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'plate_number', 'owner', 'owner_name',
            'unit', 'unit_number', 'brand', 'model', 'color',
            'is_authorized', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear vehículos"""
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'owner', 'unit', 'brand', 'model', 'color']


class AccessLogSerializer(serializers.ModelSerializer):
    """Serializer completo para AccessLog"""
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate_number', read_only=True)
    
    class Meta:
        model = AccessLog
        fields = [
            'id', 'timestamp', 'camera', 'camera_name',
            'plate_detected', 'visitor_photo', 'access_type',
            'detection_method', 'is_resident', 'user', 'user_name',
            'vehicle', 'vehicle_plate', 'visitor_name', 'notes'
        ]
        read_only_fields = ['id', 'timestamp']


class AccessLogCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear registros de acceso"""
    class Meta:
        model = AccessLog
        fields = [
            'camera', 'plate_detected', 'visitor_photo', 'access_type',
            'detection_method', 'is_resident', 'user', 'vehicle',
            'visitor_name', 'notes'
        ]


class SecurityIncidentSerializer(serializers.ModelSerializer):
    """Serializer completo para SecurityIncident"""
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    
    class Meta:
        model = SecurityIncident
        fields = [
            'id', 'timestamp', 'camera', 'camera_name',
            'incident_type', 'description', 'evidence_image',
            'severity', 'resolved', 'resolved_by', 'resolved_by_name',
            'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['id', 'timestamp', 'resolved_by', 'resolved_at']


class SecurityIncidentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear incidentes"""
    class Meta:
        model = SecurityIncident
        fields = [
            'camera', 'incident_type', 'description',
            'evidence_image', 'severity'
        ]


class SecurityStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de seguridad"""
    total_incidents = serializers.IntegerField()
    resolved_incidents = serializers.IntegerField()
    pending_incidents = serializers.IntegerField()
    critical_incidents = serializers.IntegerField()
    total_access_logs = serializers.IntegerField()
    entries_today = serializers.IntegerField()
    exits_today = serializers.IntegerField()
    unauthorized_accesses = serializers.IntegerField()
