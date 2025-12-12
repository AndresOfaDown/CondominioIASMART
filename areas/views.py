from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import CommonArea, Reservation
from .serializers import (
    CommonAreaSerializer, CommonAreaCreateSerializer,
    ReservationSerializer, ReservationCreateSerializer,
    AvailabilityCheckSerializer
)
from users.permissions import IsAdmin, IsAdminOrReadOnly, CanManageAreas


class CommonAreaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de áreas comunes
    Endpoints:
    - GET /areas/ - Listar todas las áreas
    - POST /areas/ - Crear nueva área
    - GET /areas/{id}/ - Obtener detalle de área
    - PUT /areas/{id}/ - Actualizar área
    - DELETE /areas/{id}/ - Eliminar área
    - GET /areas/available/ - Listar áreas disponibles
    - POST /areas/{id}/check_availability/ - Verificar disponibilidad
    """
    queryset = CommonArea.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'cost_per_hour', 'capacity']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommonAreaCreateSerializer
        return CommonAreaSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Obtener solo áreas disponibles"""
        areas = CommonArea.objects.filter(is_available=True)
        serializer = CommonAreaSerializer(areas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_availability(self, request, pk=None):
        """Verificar disponibilidad de un área en una fecha específica"""
        area = self.get_object()
        date_str = request.data.get('date')
        
        if not date_str:
            return Response(
                {"error": "El parámetro 'date' es requerido (formato: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener reservas del día
        reservations = Reservation.objects.filter(
            area=area,
            status__in=['PENDING', 'CONFIRMED'],
            start_time__date=check_date
        ).order_by('start_time')
        
        # Generar slots disponibles (simplificado)
        reserved_slots = [
            {
                'start': res.start_time.strftime('%H:%M'),
                'end': res.end_time.strftime('%H:%M')
            } for res in reservations
        ]
        
        return Response({
            'area_id': area.id,
            'date': date_str,
            'is_available': area.is_available,
            'reserved_slots': reserved_slots,
            'opening_time': area.opening_time.strftime('%H:%M'),
            'closing_time': area.closing_time.strftime('%H:%M')
        })
    
    @action(detail=False, methods=['get'])
    def usage_report(self, request):
        """Reporte de uso de áreas comunes"""
        areas = CommonArea.objects.annotate(
            total_reservations=Count('reservations'),
            confirmed_reservations=Count('reservations', filter=Q(reservations__status='CONFIRMED'))
        )
        
        report = [
            {
                'area_name': area.name,
                'total_reservations': area.total_reservations,
                'confirmed_reservations': area.confirmed_reservations,
                'capacity': area.capacity,
                'cost_per_hour': str(area.cost_per_hour)
            } for area in areas
        ]
        
        return Response(report)


class ReservationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reservas
    Endpoints:
    - GET /reservations/ - Listar todas las reservas
    - POST /reservations/ - Crear nueva reserva
    - GET /reservations/{id}/ - Obtener detalle de reserva
    - PUT /reservations/{id}/ - Actualizar reserva
    - DELETE /reservations/{id}/ - Eliminar reserva
    - POST /reservations/{id}/confirm/ - Confirmar reserva
    - POST /reservations/{id}/cancel/ - Cancelar reserva
    - GET /reservations/my_reservations/ - Obtener reservas del usuario
    """
    queryset = Reservation.objects.all()
    permission_classes = [CanManageAreas]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['area__name', 'user__username']
    ordering_fields = ['start_time', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer
    
    def perform_create(self, serializer):
        """Asignar usuario actual al crear reserva"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmar una reserva"""
        reservation = self.get_object()
        
        if reservation.status != 'PENDING':
            return Response(
                {"error": "Solo se pueden confirmar reservas pendientes"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'CONFIRMED'
        reservation.save()
        
        return Response(
            {"message": "Reserva confirmada correctamente"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar una reserva"""
        reservation = self.get_object()
        
        if reservation.status == 'COMPLETED':
            return Response(
                {"error": "No se puede cancelar una reserva completada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'CANCELLED'
        reservation.save()
        
        return Response(
            {"message": "Reserva cancelada correctamente"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirmar pago de reserva"""
        reservation = self.get_object()
        reservation.payment_confirmed = True
        reservation.save()
        
        return Response(
            {"message": "Pago confirmado correctamente"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        """Obtener reservas del usuario actual"""
        reservations = Reservation.objects.filter(user=request.user)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Obtener reservas próximas"""
        now = datetime.now()
        reservations = Reservation.objects.filter(
            start_time__gte=now,
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('start_time')
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
