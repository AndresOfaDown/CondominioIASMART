from django.db import models
from users.models import User


class Announcement(models.Model):
    """Avisos y comunicados de la administración"""
    CATEGORY_CHOICES = (
        ('GENERAL', 'General'),
        ('MAINTENANCE', 'Mantenimiento'),
        ('SECURITY', 'Seguridad'),
        ('FINANCE', 'Finanzas'),
        ('EVENT', 'Evento'),
        ('URGENT', 'Urgente'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)  # Para avisos importantes en la parte superior
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class Notification(models.Model):
    """Notificaciones push para usuarios"""
    NOTIFICATION_TYPE_CHOICES = (
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ALERT', 'Alerta'),
        ('SUCCESS', 'Éxito'),
        # Para notificaciones de IA de seguridad
        ('SECURITY_INCIDENT', 'Incidente de Seguridad'),
        ('UNAUTHORIZED_ACCESS', 'Acceso No Autorizado'),
        ('UNKNOWN_PERSON', 'Persona Desconocida'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES, default='INFO')
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)  # Link relacionado con la notificación
    
    # Referencias opcionales a otros modelos
    related_announcement = models.ForeignKey(
        Announcement, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='notifications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
