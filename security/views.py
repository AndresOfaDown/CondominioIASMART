from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import Vehicle, AccessLog, SecurityIncident, Camera
from .serializers import (
    CameraSerializer,
    VehicleSerializer, VehicleCreateSerializer,
    AccessLogSerializer, AccessLogCreateSerializer,
    SecurityIncidentSerializer, SecurityIncidentCreateSerializer,
    SecurityStatsSerializer
)
from users.permissions import IsAdminOrSecurity, IsAdminOrSecurityOrReadOnly, IsOwnerOrAdmin


class CameraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cámaras de vigilancia
    Endpoints:
    - GET /cameras/ - Listar todas las cámaras
    - POST /cameras/ - Crear nueva cámara
    - GET /cameras/{id}/ - Obtener detalle de cámara
    - PUT /cameras/{id}/ - Actualizar cámara
    - DELETE /cameras/{id}/ - Eliminar cámara
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [IsAdminOrSecurity]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'camera_type', 'created_at']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener solo cámaras activas"""
        cameras = Camera.objects.filter(is_active=True)
        serializer = CameraSerializer(cameras, many=True)
        return Response(serializer.data)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de vehículos
    Endpoints:
    - GET /vehicles/ - Listar todos los vehículos
    - POST /vehicles/ - Registrar nuevo vehículo
    - GET /vehicles/{id}/ - Obtener detalle de vehículo
    - PUT /vehicles/{id}/ - Actualizar vehículo
    - DELETE /vehicles/{id}/ - Eliminar vehículo
    - GET /vehicles/authorized/ - Listar vehículos autorizados
    - POST /vehicles/{id}/authorize/ - Autorizar vehículo
    - POST /vehicles/{id}/unauthorize/ - Desautorizar vehículo
    """
    queryset = Vehicle.objects.all()
    permission_classes = [IsAdminOrSecurityOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['plate_number', 'owner__username', 'brand', 'model']
    ordering_fields = ['plate_number', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VehicleCreateSerializer
        return VehicleSerializer
    
    @action(detail=False, methods=['get'])
    def authorized(self, request):
        """Obtener solo vehículos autorizados"""
        vehicles = Vehicle.objects.filter(is_authorized=True)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Autorizar un vehículo"""
        vehicle = self.get_object()
        vehicle.is_authorized = True
        vehicle.save()
        return Response(
            {"message": f"Vehículo {vehicle.plate_number} autorizado"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unauthorize(self, request, pk=None):
        """Desautorizar un vehículo"""
        vehicle = self.get_object()
        vehicle.is_authorized = False
        vehicle.save()
        return Response(
            {"message": f"Vehículo {vehicle.plate_number} desautorizado"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_vehicles(self, request):
        """Obtener vehículos del usuario actual"""
        vehicles = Vehicle.objects.filter(owner=request.user)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


class AccessLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registros de acceso
    Endpoints:
    - GET /access-logs/ - Listar todos los registros
    - POST /access-logs/ - Crear nuevo registro
    - GET /access-logs/{id}/ - Obtener detalle de registro
    - GET /access-logs/today/ - Obtener accesos del día
    - GET /access-logs/recent/ - Obtener accesos recientes
    """
    queryset = AccessLog.objects.all()
    permission_classes = [IsAdminOrSecurity]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['plate_detected', 'visitor_name', 'user__username']
    ordering_fields = ['timestamp']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AccessLogCreateSerializer
        return AccessLogSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Obtener accesos del día actual"""
        today = timezone.now().date()
        logs = AccessLog.objects.filter(timestamp__date=today)
        serializer = AccessLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtener accesos recientes (últimas 24 horas)"""
        last_24h = timezone.now() - timedelta(hours=24)
        logs = AccessLog.objects.filter(timestamp__gte=last_24h)
        serializer = AccessLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Filtrar por tipo de acceso (ENTRY/EXIT)"""
        access_type = request.query_params.get('type')
        if access_type:
            logs = AccessLog.objects.filter(access_type=access_type)
            serializer = AccessLogSerializer(logs, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'type' es requerido (ENTRY o EXIT)"},
            status=status.HTTP_400_BAD_REQUEST
        )


class SecurityIncidentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para incidentes de seguridad
    Endpoints:
    - GET /incidents/ - Listar todos los incidentes
    - POST /incidents/ - Crear nuevo incidente
    - GET /incidents/{id}/ - Obtener detalle de incidente
    - PUT /incidents/{id}/ - Actualizar incidente
    - DELETE /incidents/{id}/ - Eliminar incidente
    - GET /incidents/unresolved/ - Obtener incidentes sin resolver
    - POST /incidents/{id}/resolve/ - Marcar incidente como resuelto
    - GET /incidents/critical/ - Obtener incidentes críticos
    - GET /incidents/stats/ - Obtener estadísticas de seguridad
    """
    queryset = SecurityIncident.objects.all()
    permission_classes = [IsAdminOrSecurity]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'incident_type']
    ordering_fields = ['timestamp', 'severity']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SecurityIncidentCreateSerializer
        return SecurityIncidentSerializer
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Obtener incidentes sin resolver"""
        incidents = SecurityIncident.objects.filter(resolved=False)
        serializer = SecurityIncidentSerializer(incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Marcar un incidente como resuelto"""
        incident = self.get_object()
        
        resolution_notes = request.data.get('resolution_notes', '')
        
        incident.resolved = True
        incident.resolved_by = request.user
        incident.resolved_at = timezone.now()
        incident.resolution_notes = resolution_notes
        incident.save()
        
        return Response(
            {"message": "Incidente marcado como resuelto"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Obtener incidentes críticos sin resolver"""
        incidents = SecurityIncident.objects.filter(
            severity='CRITICAL',
            resolved=False
        )
        serializer = SecurityIncidentSerializer(incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de seguridad"""
        total_incidents = SecurityIncident.objects.count()
        resolved_incidents = SecurityIncident.objects.filter(resolved=True).count()
        pending_incidents = total_incidents - resolved_incidents
        critical_incidents = SecurityIncident.objects.filter(
            severity='CRITICAL',
            resolved=False
        ).count()
        
        total_access_logs = AccessLog.objects.count()
        today = timezone.now().date()
        entries_today = AccessLog.objects.filter(
            timestamp__date=today,
            access_type='ENTRY'
        ).count()
        exits_today = AccessLog.objects.filter(
            timestamp__date=today,
            access_type='EXIT'
        ).count()
        
        # Incidentes de acceso no autorizado
        unauthorized_accesses = SecurityIncident.objects.filter(
            incident_type='UNAUTHORIZED_ACCESS',
            resolved=False
        ).count()
        
        stats = {
            'total_incidents': total_incidents,
            'resolved_incidents': resolved_incidents,
            'pending_incidents': pending_incidents,
            'critical_incidents': critical_incidents,
            'total_access_logs': total_access_logs,
            'entries_today': entries_today,
            'exits_today': exits_today,
            'unauthorized_accesses': unauthorized_accesses
        }
        
        serializer = SecurityStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Filtrar incidentes por severidad"""
        severity = request.query_params.get('severity')
        if severity:
            incidents = SecurityIncident.objects.filter(severity=severity)
            serializer = SecurityIncidentSerializer(incidents, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'severity' es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )