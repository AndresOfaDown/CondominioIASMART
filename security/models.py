# security/models.py
from django.db import models
from users.models import User, ResidentialUnit


class Camera(models.Model):
    """Cámaras de vigilancia para control con IA"""
    CAMERA_TYPE_CHOICES = (
        ('ENTRANCE', 'Entrada'),
        ('EXIT', 'Salida'),
        ('PARKING', 'Estacionamiento'),
        ('COMMON_AREA', 'Área Común'),
        ('RESTRICTED', 'Área Restringida'),
    )
    
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    camera_type = models.CharField(max_length=20, choices=CAMERA_TYPE_CHOICES)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    has_facial_recognition = models.BooleanField(default=False)
    has_ocr = models.BooleanField(default=False)  # OCR para placas
    has_anomaly_detection = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cámara"
        verbose_name_plural = "Cámaras"
    
    def __str__(self):
        return f"{self.name} ({self.get_camera_type_display()})"


class Vehicle(models.Model):
    """Para Reconocimiento de Vehículos (OCR)"""
    plate_number = models.CharField(max_length=20, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    unit = models.ForeignKey(ResidentialUnit, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    is_authorized = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
    
    def __str__(self):
        return f"{self.plate_number} - {self.owner.get_full_name()}"


class AccessLog(models.Model):
    """Registro automático de ingresos/salidas"""
    ACCESS_TYPES = (('ENTRY', 'Entrada'), ('EXIT', 'Salida'))
    DETECTION_METHOD_CHOICES = (
        ('FACIAL', 'Reconocimiento Facial'),
        ('MANUAL', 'Manual'),
        ('CARD', 'Tarjeta'),
        ('PLATE', 'Reconocimiento de Placa'),
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    plate_detected = models.CharField(max_length=20, blank=True, null=True)
    visitor_photo = models.ImageField(upload_to='visitors/', blank=True, null=True)  # Foto visitante
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPES)
    detection_method = models.CharField(max_length=20, choices=DETECTION_METHOD_CHOICES, default='MANUAL')
    is_resident = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='access_logs')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    visitor_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Acceso"
        verbose_name_plural = "Registros de Acceso"
    
    def __str__(self):
        return f"{self.get_access_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SecurityIncident(models.Model):
    """Incidentes detectados por IA (Anomalías)"""
    SEVERITY_CHOICES = (
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    )
    
    INCIDENT_TYPE_CHOICES = (
        ('UNAUTHORIZED_ACCESS', 'Acceso No Autorizado'),
        ('UNKNOWN_PERSON', 'Persona Desconocida'),
        ('SUSPICIOUS_BEHAVIOR', 'Comportamiento Sospechoso'),
        ('LOOSE_DOG', 'Perro Suelto'),
        ('DOG_WASTE', 'Perro haciendo necesidades'),
        ('WRONG_PARKING', 'Vehículo mal estacionado'),
        ('OTHER', 'Otro'),
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES, default='OTHER')
    description = models.TextField()  # Ej: "Persona desconocida en área restringida"
    evidence_image = models.ImageField(upload_to='incidents/')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_incidents')
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Incidente de Seguridad"
        verbose_name_plural = "Incidentes de Seguridad"
    
    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
