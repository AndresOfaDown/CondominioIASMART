# users/permissions.py
"""
Sistema de permisos basado en roles para Smart Condominium.
Roles: ADMIN, RESIDENTE, SEGURIDAD, MANTENIMIENTO
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Permite acceso solo a usuarios con rol ADMIN.
    """
    message = "Solo los administradores pueden realizar esta acción."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol == 'ADMIN'
        )


class IsAdminOrReadOnly(BasePermission):
    """
    ADMIN tiene acceso completo, otros roles solo lectura.
    """
    message = "Solo los administradores pueden modificar este recurso."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        return request.user.rol == 'ADMIN'


class IsAdminOrSecurity(BasePermission):
    """
    Permite acceso a usuarios con rol ADMIN o SEGURIDAD.
    """
    message = "Solo administradores o personal de seguridad pueden realizar esta acción."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['ADMIN', 'SEGURIDAD']
        )


class IsAdminOrSecurityOrReadOnly(BasePermission):
    """
    ADMIN/SEGURIDAD tienen acceso completo, otros roles solo lectura.
    """
    message = "Solo administradores o seguridad pueden modificar este recurso."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        return request.user.rol in ['ADMIN', 'SEGURIDAD']


class IsAdminOrMaintenance(BasePermission):
    """
    Permite acceso a usuarios con rol ADMIN o MANTENIMIENTO.
    """
    message = "Solo administradores o personal de mantenimiento pueden realizar esta acción."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['ADMIN', 'MANTENIMIENTO']
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permite acceso al dueño del objeto o a ADMIN.
    Requiere que el objeto tenga un campo 'propietario' o 'usuario'.
    """
    message = "Solo el propietario o un administrador puede realizar esta acción."
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.rol == 'ADMIN':
            return True
        
        # Verificar si el usuario es el dueño
        if hasattr(obj, 'propietario'):
            return obj.propietario == request.user
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        if hasattr(obj, 'residente'):
            return obj.residente == request.user
        
        return False


class IsSelfOrAdmin(BasePermission):
    """
    Permite que un usuario edite su propio perfil o que ADMIN edite cualquiera.
    """
    message = "Solo puedes editar tu propio perfil o ser administrador."
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.rol == 'ADMIN':
            return True
        
        return obj == request.user


class CanManageVisits(BasePermission):
    """
    ADMIN, SEGURIDAD: acceso completo
    RESIDENTE: solo sus propias visitas
    """
    message = "No tienes permiso para gestionar visitas."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ADMIN y SEGURIDAD pueden todo
        if request.user.rol in ['ADMIN', 'SEGURIDAD']:
            return True
        
        # RESIDENTE puede crear y ver
        if request.user.rol == 'RESIDENTE':
            return request.method in SAFE_METHODS or request.method == 'POST'
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.rol in ['ADMIN', 'SEGURIDAD']:
            return True
        
        # RESIDENTE solo puede ver/editar sus propias visitas
        if hasattr(obj, 'residente'):
            return obj.residente == request.user
        if hasattr(obj, 'unidad'):
            return obj.unidad.propietario == request.user
        
        return False


class CanManageFinances(BasePermission):
    """
    ADMIN: acceso completo
    RESIDENTE: solo ver sus propios pagos
    Otros: sin acceso
    """
    message = "No tienes permiso para acceder a información financiera."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ADMIN puede todo
        if request.user.rol == 'ADMIN':
            return True
        
        # RESIDENTE solo puede ver
        if request.user.rol == 'RESIDENTE':
            return request.method in SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.rol == 'ADMIN':
            return True
        
        # RESIDENTE solo puede ver sus propios registros
        if hasattr(obj, 'unidad'):
            return obj.unidad.propietario == request.user
        if hasattr(obj, 'residente'):
            return obj.residente == request.user
        
        return False


class CanManageAreas(BasePermission):
    """
    ADMIN: acceso completo (CRUD de áreas)
    MANTENIMIENTO: puede actualizar estado de mantenimiento
    RESIDENTE: puede hacer reservas
    """
    message = "No tienes permiso para gestionar áreas comunes."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ADMIN puede todo
        if request.user.rol == 'ADMIN':
            return True
        
        # MANTENIMIENTO puede ver y actualizar
        if request.user.rol == 'MANTENIMIENTO':
            return request.method in SAFE_METHODS or request.method in ['PUT', 'PATCH']
        
        # RESIDENTE puede ver y crear reservas
        if request.user.rol == 'RESIDENTE':
            return request.method in SAFE_METHODS or request.method == 'POST'
        
        return False


class CanCreateAnnouncements(BasePermission):
    """
    ADMIN, SEGURIDAD: pueden crear avisos
    RESIDENTE: solo puede ver avisos
    """
    message = "No tienes permiso para crear avisos."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ADMIN y SEGURIDAD pueden todo
        if request.user.rol in ['ADMIN', 'SEGURIDAD']:
            return True
        
        # Otros solo pueden ver
        return request.method in SAFE_METHODS


# Diccionario de permisos por rol (para endpoint de consulta)
ROLE_PERMISSIONS = {
    'ADMIN': {
        'usuarios': ['crear', 'leer', 'actualizar', 'eliminar', 'cambiar_rol'],
        'unidades': ['crear', 'leer', 'actualizar', 'eliminar'],
        'residentes': ['crear', 'leer', 'actualizar', 'eliminar'],
        'visitas': ['crear', 'leer', 'actualizar', 'eliminar'],
        'vehiculos': ['crear', 'leer', 'actualizar', 'eliminar'],
        'avisos': ['crear', 'leer', 'actualizar', 'eliminar'],
        'finanzas': ['crear', 'leer', 'actualizar', 'eliminar'],
        'areas': ['crear', 'leer', 'actualizar', 'eliminar'],
        'seguridad': ['crear', 'leer', 'actualizar', 'eliminar'],
        'reportes': ['leer', 'exportar'],
    },
    'SEGURIDAD': {
        'usuarios': ['leer'],
        'unidades': ['leer'],
        'residentes': ['leer'],
        'visitas': ['crear', 'leer', 'actualizar', 'eliminar'],
        'vehiculos': ['crear', 'leer', 'actualizar', 'eliminar'],
        'avisos': ['crear', 'leer'],
        'finanzas': [],
        'areas': ['leer'],
        'seguridad': ['crear', 'leer', 'actualizar', 'eliminar'],
        'reportes': ['leer'],
    },
    'MANTENIMIENTO': {
        'usuarios': ['leer'],
        'unidades': ['leer'],
        'residentes': ['leer'],
        'visitas': [],
        'vehiculos': [],
        'avisos': ['leer'],
        'finanzas': [],
        'areas': ['leer', 'actualizar'],
        'seguridad': [],
        'reportes': [],
    },
    'RESIDENTE': {
        'usuarios': ['leer_propio', 'actualizar_propio'],
        'unidades': ['leer_propio'],
        'residentes': ['leer_propio'],
        'visitas': ['crear_propio', 'leer_propio', 'actualizar_propio', 'eliminar_propio'],
        'vehiculos': ['crear_propio', 'leer_propio', 'actualizar_propio', 'eliminar_propio'],
        'avisos': ['leer'],
        'finanzas': ['leer_propio'],
        'areas': ['leer', 'reservar'],
        'seguridad': [],
        'reportes': [],
    },
}


def get_permissions_for_role(rol):
    """Retorna los permisos para un rol específico."""
    return ROLE_PERMISSIONS.get(rol, {})
