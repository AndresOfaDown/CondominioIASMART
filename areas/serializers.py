from rest_framework import serializers
from .models import CommonArea, Reservation
from users.serializers import UserSerializer


class CommonAreaSerializer(serializers.ModelSerializer):
    """Serializer para CommonArea"""
    active_reservations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CommonArea
        fields = [
            'id', 'name', 'description', 'capacity', 'cost_per_hour',
            'is_available', 'opening_time', 'closing_time', 'image',
            'active_reservations_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_reservations_count(self, obj):
        """Contar reservas activas (pendientes y confirmadas)"""
        return obj.reservations.filter(status__in=['PENDING', 'CONFIRMED']).count()


class CommonAreaCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear áreas"""
    class Meta:
        model = CommonArea
        fields = ['name', 'description', 'capacity', 'cost_per_hour', 'opening_time', 'closing_time']


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer completo para Reservation"""
    area_name = serializers.CharField(source='area.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'area', 'area_name', 'user', 'user_name',
            'start_time', 'end_time', 'duration_hours', 'status',
            'total_cost', 'payment_confirmed', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_cost', 'created_at', 'updated_at']
    
    def get_duration_hours(self, obj):
        """Calcular duración en horas"""
        if obj.start_time and obj.end_time:
            duration = (obj.end_time - obj.start_time).total_seconds() / 3600
            return round(duration, 2)
        return 0
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("La hora de inicio debe ser antes que la hora de fin")
        
        # Validar que el área esté disponible
        area = data.get('area')
        if not area.is_available:
            raise serializers.ValidationError("El área no está disponible")
        
        return data


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservas"""
    class Meta:
        model = Reservation
        fields = ['area', 'user', 'start_time', 'end_time', 'notes']
    
    def validate(self, data):
        """Validar disponibilidad"""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("La hora de inicio debe ser antes que la hora de fin")
        
        # Verificar solapamiento
        overlapping = Reservation.objects.filter(
            area=data['area'],
            status__in=['PENDING', 'CONFIRMED']
        ).filter(
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        )
        
        if overlapping.exists():
            raise serializers.ValidationError("Ya existe una reserva en ese horario para esta área")
        
        return data


class AvailabilityCheckSerializer(serializers.Serializer):
    """Serializer para verificar disponibilidad"""
    area_id = serializers.IntegerField()
    date = serializers.DateField()
    is_available = serializers.BooleanField(read_only=True)
    available_slots = serializers.ListField(read_only=True)
