from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ResidentialUnit


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('role', 'phone', 'photo', 'email_verified', 'facial_encoding')
        }),
    )


@admin.register(ResidentialUnit)
class ResidentialUnitAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'owner', 'floor', 'bedrooms', 'is_active']
    list_filter = ['is_active', 'floor']
    search_fields = ['unit_number', 'owner__username']
    filter_horizontal = ['residents']

##admin.site.register(User)
