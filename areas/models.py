# areas/models.py
from django.db import models
from django.core.exceptions import ValidationError
from users.models import Usuario


class CommonArea(models.Model):
    """Áreas comunes del condominio"""
    name = models.CharField(max_length=100)  # Ej: Churrasquera, Salón de Eventos
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField()
    cost_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    opening_time = models.TimeField(default='08:00')
    closing_time = models.TimeField(default='22:00')
    image = models.ImageField(upload_to='areas/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Área Común"
        verbose_name_plural = "Áreas Comunes"
    
    def __str__(self):
        return f"{self.name} (Capacidad: {self.capacity})"


class Reservation(models.Model):
    """Reservas rápidas y confirmaciones"""
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
        ('COMPLETED', 'Completada'),
    )
    
    area = models.ForeignKey(CommonArea, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservations')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
    
    def __str__(self):
        return f"{self.area.name} - {self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        """Validar que la fecha de inicio sea antes que la de fin"""
        if self.start_time >= self.end_time:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        # Validar que no haya solapamiento de reservas
        overlapping = Reservation.objects.filter(
            area=self.area,
            status__in=['PENDING', 'CONFIRMED']
        ).exclude(id=self.id).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        
        if overlapping.exists():
            raise ValidationError("Ya existe una reserva en ese horario para esta área")
    
    def save(self, *args, **kwargs):
        # Calcular costo total basado en horas
        if self.start_time and self.end_time and self.area:
            hours = (self.end_time - self.start_time).total_seconds() / 3600
            self.total_cost = self.area.cost_per_hour * hours
        super().save(*args, **kwargs)
