from rest_framework import serializers
from .models import Fee, Payment, FeeConfiguration


class FeeConfigurationSerializer(serializers.ModelSerializer):
    """Serializer para configuración de tarifas"""
    class Meta:
        model = FeeConfiguration
        fields = ['id', 'name', 'description', 'base_amount', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeeSerializer(serializers.ModelSerializer):
    """Serializer completo para Fee"""
    unit_number = serializers.CharField(source='unit.unit_number', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    total_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = Fee
        fields = [
            'id', 'unit', 'unit_number', 'title', 'description',
            'amount', 'due_date', 'status', 'is_overdue',
            'days_overdue', 'total_paid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_paid(self, obj):
        """Calcular total pagado para esta cuota"""
        return sum(payment.amount_paid for payment in obj.payments.filter(is_verified=True))


class FeeCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear cuotas"""
    class Meta:
        model = Fee
        fields = ['unit', 'title', 'description', 'amount', 'due_date']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer completo para Payment"""
    fee_title = serializers.CharField(source='fee.title', read_only=True)
    unit_number = serializers.CharField(source='fee.unit.unit_number', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'fee', 'fee_title', 'unit_number', 'payment_date',
            'amount_paid', 'payment_method', 'receipt_image',
            'is_verified', 'verified_by', 'verified_by_name',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'payment_date', 'created_at', 'verified_by']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos"""
    class Meta:
        model = Payment
        fields = ['fee', 'amount_paid', 'payment_method', 'receipt_image', 'notes']


class FinancialReportSerializer(serializers.Serializer):
    """Serializer para reportes financieros"""
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_overdue = serializers.DecimalField(max_digits=12, decimal_places=2)
    morosidad_rate = serializers.FloatField()
    pending_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()