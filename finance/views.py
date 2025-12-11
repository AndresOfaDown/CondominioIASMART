from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q, Count
from decimal import Decimal
from .models import Fee, Payment, FeeConfiguration
from .serializers import (
    FeeSerializer, FeeCreateSerializer,
    PaymentSerializer, PaymentCreateSerializer,
    FeeConfigurationSerializer, FinancialReportSerializer
)


class FeeConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de configuraciones de tarifas
    Solo accesible por administradores
    """
    queryset = FeeConfiguration.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FeeConfigurationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_amount', 'created_at']


class FeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cuotas/expensas
    Endpoints:
    - GET /fees/ - Listar todas las cuotas
    - POST /fees/ - Crear nueva cuota
    - GET /fees/{id}/ - Obtener detalle de cuota
    - PUT /fees/{id}/ - Actualizar cuota
    - DELETE /fees/{id}/ - Eliminar cuota
    - GET /fees/my_fees/ - Obtener cuotas del usuario actual
    - GET /fees/overdue/ - Obtener cuotas vencidas
    - POST /fees/{id}/mark_paid/ - Marcar cuota como pagada
    """
    queryset = Fee.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'unit__unit_number']
    ordering_fields = ['due_date', 'amount', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeeCreateSerializer
        return FeeSerializer
    
    @action(detail=False, methods=['get'])
    def my_fees(self, request):
        """Obtener cuotas de las unidades del usuario actual"""
        user = request.user
        fees = Fee.objects.filter(
            Q(unit__owner=user) | Q(unit__residents=user)
        ).distinct()
        serializer = FeeSerializer(fees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Obtener todas las cuotas vencidas"""
        fees = Fee.objects.filter(status='PENDING')
        overdue_fees = [fee for fee in fees if fee.is_overdue()]
        serializer = FeeSerializer(overdue_fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Marcar una cuota como pagada"""
        fee = self.get_object()
        fee.status = 'PAID'
        fee.save()
        return Response(
            {"message": "Cuota marcada como pagada"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_unit(self, request):
        """Filtrar cuotas por unidad"""
        unit_id = request.query_params.get('unit_id')
        if unit_id:
            fees = Fee.objects.filter(unit_id=unit_id)
            serializer = FeeSerializer(fees, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'unit_id' es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pagos
    Endpoints:
    - GET /payments/ - Listar todos los pagos
    - POST /payments/ - Registrar nuevo pago
    - GET /payments/{id}/ - Obtener detalle de pago
    - PUT /payments/{id}/ - Actualizar pago
    - DELETE /payments/{id}/ - Eliminar pago
    - POST /payments/{id}/verify/ - Verificar pago
    - GET /payments/my_payments/ - Obtener pagos del usuario
    """
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['fee__title', 'fee__unit__unit_number']
    ordering_fields = ['payment_date', 'amount_paid']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verificar un pago (solo administradores)"""
        payment = self.get_object()
        payment.is_verified = True
        payment.verified_by = request.user
        payment.save()
        
        # Actualizar estado de la cuota si está completamente pagada
        fee = payment.fee
        total_paid = sum(p.amount_paid for p in fee.payments.filter(is_verified=True))
        if total_paid >= fee.amount:
            fee.status = 'PAID'
            fee.save()
        
        return Response(
            {"message": "Pago verificado correctamente"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Obtener pagos del usuario actual"""
        user = request.user
        payments = Payment.objects.filter(
            Q(fee__unit__owner=user) | Q(fee__unit__residents=user)
        ).distinct()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def financial_report(self, request):
        """Generar reporte financiero general"""
        fees = Fee.objects.all()
        
        total_fees = fees.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        paid_fees = fees.filter(status='PAID')
        pending_fees = fees.filter(status='PENDING')
        
        total_paid = paid_fees.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_pending = pending_fees.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        overdue_fees = [fee for fee in pending_fees if fee.is_overdue()]
        total_overdue = sum(fee.amount for fee in overdue_fees)
        
        morosidad_rate = (float(total_overdue) / float(total_fees) * 100) if total_fees > 0 else 0
        
        report_data = {
            'total_fees': total_fees,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'total_overdue': total_overdue,
            'morosidad_rate': round(morosidad_rate, 2),
            'pending_count': pending_fees.count(),
            'paid_count': paid_fees.count(),
            'overdue_count': len(overdue_fees),
        }
        
        serializer = FinancialReportSerializer(report_data)
        return Response(serializer.data)