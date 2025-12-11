# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Roles definidos en el documento [cite: 63]
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('RESIDENT', 'Residente'),
        ('SECURITY', 'Seguridad'),
        ('MAINTENANCE', 'Mantenimiento'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RESIDENT')
    photo = models.ImageField(upload_to='users/', blank=True, null=True)  # Para reconocimiento facial
    phone = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    facial_encoding = models.TextField(blank=True, null=True)  # Para almacenar encoding de IA
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class ResidentialUnit(models.Model):
    """Unidades habitacionales (Apartamentos/Casas)"""
    unit_number = models.CharField(max_length=10, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_units')
    residents = models.ManyToManyField(User, related_name='residing_units', blank=True)
    floor = models.IntegerField(blank=True, null=True)
    size_sqm = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Tamaño en m²
    bedrooms = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['unit_number']
    
    def __str__(self):
        return f"Unidad {self.unit_number}"