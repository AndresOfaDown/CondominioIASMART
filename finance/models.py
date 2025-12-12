# finance/models.py
from django.db import models
from users.models import UnidadResidencial
from datetime import date


class FeeConfiguration(models.Model):
    """Configuración de precios de expensas, multas y otros"""
    name = models.CharField(max_length=100)  # Ej: "Expensa Mensual Básica"
    description = models.TextField(blank=True)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Tarifa"
        verbose_name_plural = "Configuraciones de Tarifas"
    
    def __str__(self):
        return f"{self.name} - ${self.base_amount}"


class Fee(models.Model):
    """Expensas y Cuotas"""
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('OVERDUE', 'Vencido'),  # Para la analítica de morosidad
    )
    unit = models.ForeignKey(UnidadResidencial, on_delete=models.CASCADE, related_name='fees')
    title = models.CharField(max_length=100)  # Ej: Expensas Noviembre
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        verbose_name = "Cuota/Expensa"
        verbose_name_plural = "Cuotas/Expensas"
    
    def __str__(self):
        return f"{self.title} - Unidad {self.unit.unit_number}"
    
    def is_overdue(self):
        """Verificar si la cuota está vencida"""
        return self.status == 'PENDING' and self.due_date < date.today()
    
    def days_overdue(self):
        """Calcular días de mora"""
        if self.is_overdue():
            return (date.today() - self.due_date).days
        return 0


class Payment(models.Model):
    """Historial de pagos con comprobantes"""
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Efectivo'),
        ('TRANSFER', 'Transferencia'),
        ('CARD', 'Tarjeta'),
        ('CHECK', 'Cheque'),
    )
    
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='TRANSFER')
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)  # Comprobante
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('users.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
    
    def __str__(self):
        return f"Pago de ${self.amount_paid} - {self.fee.title}"
