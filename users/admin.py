from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, UnidadResidencial, Residente


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'email_verificado']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'telefono', 'foto', 'email_verificado', 'encoding_facial')
        }),
    )


@admin.register(UnidadResidencial)
class UnidadResidencialAdmin(admin.ModelAdmin):
    list_display = ['numero_unidad', 'propietario', 'estado_ocupacion', 'piso', 'dormitorios', 'activo']
    list_filter = ['estado_ocupacion', 'activo', 'piso']
    search_fields = ['numero_unidad', 'propietario__username', 'propietario__email']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Residente)
class ResidenteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'unidad', 'tipo_residente', 'es_principal', 'activo', 'fecha_ingreso']
    list_filter = ['tipo_residente', 'es_principal', 'activo']
    search_fields = ['usuario__username', 'usuario__email', 'unidad__numero_unidad']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_ingreso'
