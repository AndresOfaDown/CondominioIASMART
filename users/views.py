from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from .models import Usuario, UnidadResidencial, Residente
from .serializers import (
    UsuarioSerializer, UsuarioCrearSerializer, UsuarioActualizarSerializer,
    UnidadResidencialSerializer, UnidadResidencialCrearSerializer, UnidadResidencialActualizarSerializer,
    ResidenteSerializer, ResidenteCrearSerializer, ResidenteActualizarSerializer
)
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsSelfOrAdmin, IsOwnerOrAdmin,
    ROLE_PERMISSIONS, get_permissions_for_role
)


class LoginView(APIView):
    """
    Vista de login que retorna tokens JWT
    POST /api/users/login/
    Body: {"email": "usuario@email.com", "password": "contraseña"}
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {"error": "Se requieren email y password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar usuario por email
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificar contraseña
        if not user.check_password(password):
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {"error": "Usuario inactivo"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "usuario": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol,
                "nombre": user.first_name,
                "apellido": user.last_name,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Vista de logout que invalida el refresh token
    POST /api/users/logout/
    Body: {"refresh": "refresh_token"}
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Se requiere el refresh token"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"mensaje": "Logout exitoso"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Token inválido o ya expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de usuarios
    Endpoints:
    - GET /usuarios/ - Listar todos los usuarios
    - POST /usuarios/ - Crear nuevo usuario
    - GET /usuarios/{id}/ - Obtener detalle de usuario
    - PUT /usuarios/{id}/ - Actualizar usuario
    - DELETE /usuarios/{id}/ - Eliminar usuario
    - GET /usuarios/me/ - Obtener usuario actual
    - GET /usuarios/por_rol/ - Filtrar usuarios por rol
    """
    queryset = Usuario.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'fecha_creacion']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCrearSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioActualizarSerializer
        return UsuarioSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsSelfOrAdmin()]
        elif self.action in ['me', 'roles', 'permisos', 'mis_permisos']:
            return [IsAuthenticated()]
        elif self.action in ['list', 'por_rol', 'cambiar_rol']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.rol == 'ADMIN':
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        """Filtrar usuarios por rol (solo ADMIN)"""
        rol = request.query_params.get('rol', None)
        if rol:
            usuarios = Usuario.objects.filter(rol=rol)
            serializer = UsuarioSerializer(usuarios, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'rol' es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def roles(self, request):
        """Listar todos los roles disponibles"""
        roles = [
            {"codigo": codigo, "nombre": nombre} 
            for codigo, nombre in Usuario.ROLES
        ]
        return Response(roles)
    
    @action(detail=False, methods=['get'])
    def permisos(self, request):
        """Obtener todos los permisos por rol (solo ADMIN)"""
        return Response(ROLE_PERMISSIONS)
    
    @action(detail=False, methods=['get'])
    def mis_permisos(self, request):
        """Obtener los permisos del usuario actual según su rol"""
        permisos_usuario = get_permissions_for_role(request.user.rol)
        return Response({
            "rol": request.user.rol,
            "rol_nombre": request.user.get_rol_display(),
            "permisos": permisos_usuario
        })
    
    @action(detail=True, methods=['post'])
    def cambiar_rol(self, request, pk=None):
        """Cambiar el rol de un usuario (solo ADMIN)"""
        usuario = self.get_object()
        nuevo_rol = request.data.get('rol')
        
        if not nuevo_rol:
            return Response(
                {"error": "Se requiere el campo 'rol'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        roles_validos = [codigo for codigo, nombre in Usuario.ROLES]
        if nuevo_rol not in roles_validos:
            return Response(
                {"error": f"Rol inválido. Roles válidos: {roles_validos}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rol_anterior = usuario.rol
        usuario.rol = nuevo_rol
        usuario.save()
        
        return Response({
            "mensaje": "Rol cambiado exitosamente",
            "usuario_id": usuario.id,
            "username": usuario.username,
            "rol_anterior": rol_anterior,
            "rol_nuevo": nuevo_rol
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def subir_foto(self, request, pk=None):
        """Endpoint para subir foto del usuario (para reconocimiento facial)"""
        usuario = self.get_object()
        if 'foto' in request.FILES:
            usuario.foto = request.FILES['foto']
            usuario.save()
            return Response(
                {"mensaje": "Foto actualizada correctamente"},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "No se proporcionó ninguna foto"},
            status=status.HTTP_400_BAD_REQUEST
        )


class UnidadResidencialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de unidades residenciales
    Endpoints:
    - GET /unidades/ - Listar todas las unidades
    - POST /unidades/ - Crear nueva unidad
    - GET /unidades/{id}/ - Obtener detalle de unidad
    - PUT /unidades/{id}/ - Actualizar unidad
    - DELETE /unidades/{id}/ - Eliminar unidad
    - POST /unidades/{id}/alquilar/ - Alquilar unidad a inquilino
    - POST /unidades/{id}/terminar_alquiler/ - Terminar alquiler
    - GET /unidades/{id}/residentes/ - Ver residentes de la unidad
    """
    queryset = UnidadResidencial.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_unidad', 'propietario__username', 'propietario__email']
    ordering_fields = ['numero_unidad', 'fecha_creacion', 'estado_ocupacion']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UnidadResidencialCrearSerializer
        elif self.action in ['update', 'partial_update']:
            return UnidadResidencialActualizarSerializer
        return UnidadResidencialSerializer
    
    @action(detail=True, methods=['get'])
    def residentes(self, request, pk=None):
        """Obtener residentes activos de la unidad"""
        unidad = self.get_object()
        residentes = unidad.residentes.filter(activo=True)
        serializer = ResidenteSerializer(residentes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def registrar_propietario_residente(self, request, pk=None):
        """Registrar al propietario como residente de su propia unidad"""
        unidad = self.get_object()
        fecha_ingreso = request.data.get('fecha_ingreso', timezone.now().date())
        
        # Verificar si el propietario ya está registrado como residente activo
        existente = Residente.objects.filter(
            usuario=unidad.propietario, unidad=unidad, activo=True
        ).exists()
        
        if existente:
            return Response(
                {"error": "El propietario ya está registrado como residente activo"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear registro de residente
        residente = Residente.objects.create(
            usuario=unidad.propietario,
            unidad=unidad,
            tipo_residente='PROPIETARIO_RESIDENTE',
            es_principal=True,
            fecha_ingreso=fecha_ingreso
        )
        
        # Actualizar estado de ocupación
        unidad.estado_ocupacion = 'OCUPADA_PROPIETARIO'
        unidad.save()
        
        serializer = ResidenteSerializer(residente)
        return Response({
            "mensaje": "Propietario registrado como residente",
            "residente": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def alquilar(self, request, pk=None):
        """
        Alquilar unidad a un inquilino
        Body: {
            "inquilino_id": 5,
            "fecha_ingreso": "2024-01-15",
            "notas": "Contrato por 12 meses" (opcional)
        }
        """
        unidad = self.get_object()
        inquilino_id = request.data.get('inquilino_id')
        fecha_ingreso = request.data.get('fecha_ingreso', timezone.now().date())
        notas = request.data.get('notas', '')
        
        if not inquilino_id:
            return Response(
                {"error": "Se requiere inquilino_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que la unidad no esté alquilada
        if unidad.estado_ocupacion == 'ALQUILADA':
            return Response(
                {"error": "La unidad ya está alquilada. Termine el alquiler actual primero."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inquilino = Usuario.objects.get(id=inquilino_id)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario inquilino no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Desactivar residentes anteriores si los hay
        Residente.objects.filter(unidad=unidad, activo=True).update(
            activo=False,
            fecha_salida=timezone.now().date()
        )
        
        # Crear registro del inquilino
        residente = Residente.objects.create(
            usuario=inquilino,
            unidad=unidad,
            tipo_residente='INQUILINO',
            es_principal=True,
            fecha_ingreso=fecha_ingreso,
            notas=notas
        )
        
        # Actualizar estado de ocupación
        unidad.estado_ocupacion = 'ALQUILADA'
        unidad.save()
        
        serializer = ResidenteSerializer(residente)
        return Response({
            "mensaje": f"Unidad {unidad.numero_unidad} alquilada a {inquilino.get_full_name()}",
            "residente": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def terminar_alquiler(self, request, pk=None):
        """Terminar alquiler de la unidad"""
        unidad = self.get_object()
        fecha_salida = request.data.get('fecha_salida', timezone.now().date())
        
        if unidad.estado_ocupacion != 'ALQUILADA':
            return Response(
                {"error": "La unidad no está alquilada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Desactivar todos los residentes activos
        residentes = Residente.objects.filter(unidad=unidad, activo=True)
        cantidad = residentes.count()
        residentes.update(activo=False, fecha_salida=fecha_salida)
        
        # Cambiar estado a vacante
        unidad.estado_ocupacion = 'VACANTE'
        unidad.save()
        
        return Response({
            "mensaje": f"Alquiler terminado. {cantidad} residente(s) desactivado(s).",
            "estado_unidad": "VACANTE"
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def mis_unidades(self, request):
        """Obtener las unidades del usuario actual (como propietario o residente)"""
        # Unidades que posee
        propias = UnidadResidencial.objects.filter(propietario=request.user)
        
        # Unidades donde es residente activo
        ids_residencia = Residente.objects.filter(
            usuario=request.user, activo=True
        ).values_list('unidad_id', flat=True)
        residiendo = UnidadResidencial.objects.filter(id__in=ids_residencia)
        
        # Combinar sin duplicados
        unidades = (propias | residiendo).distinct()
        serializer = UnidadResidencialSerializer(unidades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Filtrar unidades por estado de ocupación"""
        estado = request.query_params.get('estado')
        if estado:
            unidades = UnidadResidencial.objects.filter(estado_ocupacion=estado)
            serializer = UnidadResidencialSerializer(unidades, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'estado' es requerido (OCUPADA_PROPIETARIO, ALQUILADA, VACANTE)"},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResidenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de residentes
    Endpoints:
    - GET /residentes/ - Listar todos los residentes
    - POST /residentes/ - Registrar nuevo residente
    - GET /residentes/{id}/ - Obtener detalle de residente
    - PUT /residentes/{id}/ - Actualizar residente
    - DELETE /residentes/{id}/ - Desactivar residente
    - POST /residentes/{id}/terminar_residencia/ - Terminar residencia
    - GET /residentes/activos/ - Solo residentes activos
    - GET /residentes/por_tipo/ - Filtrar por tipo
    """
    queryset = Residente.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['usuario__username', 'usuario__email', 'usuario__first_name', 'unidad__numero_unidad']
    ordering_fields = ['fecha_creacion', 'fecha_ingreso', 'es_principal']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ResidenteCrearSerializer
        elif self.action in ['update', 'partial_update']:
            return ResidenteActualizarSerializer
        return ResidenteSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Obtener solo residentes activos"""
        residentes = Residente.objects.filter(activo=True)
        serializer = ResidenteSerializer(residentes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Filtrar residentes por tipo"""
        tipo = request.query_params.get('tipo')
        if tipo:
            residentes = Residente.objects.filter(tipo_residente=tipo, activo=True)
            serializer = ResidenteSerializer(residentes, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'tipo' es requerido (PROPIETARIO_RESIDENTE, INQUILINO, FAMILIAR, AUTORIZADO)"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def terminar_residencia(self, request, pk=None):
        """Terminar la residencia de un usuario"""
        residente = self.get_object()
        fecha_salida = request.data.get('fecha_salida', timezone.now().date())
        
        if not residente.activo:
            return Response(
                {"error": "Esta residencia ya está inactiva"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        residente.terminar_residencia(fecha_salida)
        
        # Si era el principal y es INQUILINO, actualizar estado de la unidad
        if residente.es_principal and residente.tipo_residente == 'INQUILINO':
            unidad = residente.unidad
            # Verificar si hay otros residentes activos
            if not Residente.objects.filter(unidad=unidad, activo=True).exists():
                unidad.estado_ocupacion = 'VACANTE'
                unidad.save()
        
        return Response({
            "mensaje": f"Residencia de {residente.usuario.get_full_name()} terminada",
            "fecha_salida": str(fecha_salida)
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def mis_residencias(self, request):
        """Obtener residencias del usuario actual"""
        residencias = Residente.objects.filter(usuario=request.user)
        serializer = ResidenteSerializer(residencias, many=True)
        return Response(serializer.data)
