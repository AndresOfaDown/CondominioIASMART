from django.contrib import admin
from .models import Fee, Payment, FeeConfiguration


@admin.register(FeeConfiguration)
class FeeConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_amount', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'amount', 'due_date', 'status', 'created_at']
    list_filter = ['status', 'due_date']
    search_fields = ['title', 'unit__unit_number']
    date_hierarchy = 'due_date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['fee', 'amount_paid', 'payment_method', 'is_verified', 'payment_date']
    list_filter = ['is_verified', 'payment_method', 'payment_date']
    search_fields = ['fee__title', 'fee__unit__unit_number']
    date_hierarchy = 'payment_date'
