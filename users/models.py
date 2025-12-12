# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('RESIDENTE', 'Residente'),
        ('SEGURIDAD', 'Seguridad'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='RESIDENTE')
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_verificado = models.BooleanField(default=False)
    encoding_facial = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class UnidadResidencial(models.Model):
    """Unidades habitacionales (Apartamentos/Casas)"""
    ESTADO_OCUPACION = (
        ('OCUPADA_PROPIETARIO', 'Ocupada por Propietario'),
        ('ALQUILADA', 'Alquilada'),
        ('VACANTE', 'Vacante'),
    )
    
    numero_unidad = models.CharField(max_length=10, unique=True, verbose_name='Número de Unidad')
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='unidades_propias')
    estado_ocupacion = models.CharField(max_length=25, choices=ESTADO_OCUPACION, default='VACANTE')
    piso = models.IntegerField(blank=True, null=True)
    superficie_m2 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Superficie (m²)')
    dormitorios = models.IntegerField(blank=True, null=True)
    banos = models.IntegerField(blank=True, null=True, verbose_name='Baños')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['numero_unidad']
        verbose_name = 'Unidad Residencial'
        verbose_name_plural = 'Unidades Residenciales'
    
    def __str__(self):
        return f"Unidad {self.numero_unidad}"
    
    def obtener_residentes_activos(self):
        """Retorna los residentes activos de la unidad"""
        return self.residentes.filter(activo=True)
    
    def obtener_residente_principal(self):
        """Retorna el residente principal (propietario o inquilino principal)"""
        return self.residentes.filter(activo=True, es_principal=True).first()


class Residente(models.Model):
    """Relación entre Usuario y Unidad con tipo de residencia"""
    TIPO_RESIDENTE = (
        ('PROPIETARIO_RESIDENTE', 'Propietario Residente'),
        ('INQUILINO', 'Inquilino'),
        ('FAMILIAR', 'Familiar'),
        ('AUTORIZADO', 'Autorizado'),
    )
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='residencias')
    unidad = models.ForeignKey(UnidadResidencial, on_delete=models.CASCADE, related_name='residentes')
    tipo_residente = models.CharField(max_length=25, choices=TIPO_RESIDENTE)
    es_principal = models.BooleanField(default=False, help_text='Indica si es el propietario o inquilino principal')
    fecha_ingreso = models.DateField(help_text='Fecha de ingreso')
    fecha_salida = models.DateField(null=True, blank=True, help_text='Fecha de salida')
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-es_principal', '-fecha_creacion']
        verbose_name = 'Residente'
        verbose_name_plural = 'Residentes'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.unidad} ({self.get_tipo_residente_display()})"
    
    def terminar_residencia(self, fecha_salida=None):
        """Termina la residencia del usuario"""
        from django.utils import timezone
        self.activo = False
        self.fecha_salida = fecha_salida or timezone.now().date()
        self.save()