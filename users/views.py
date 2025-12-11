from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import User, ResidentialUnit
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ResidentialUnitSerializer, ResidentialUnitCreateSerializer
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
            user = User.objects.get(email=email)
        except User.DoesNotExist:
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
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
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
                {"message": "Logout exitoso"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Token inválido o ya expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )



class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de usuarios
    Endpoints:
    - GET /users/ - Listar todos los usuarios
    - POST /users/ - Crear nuevo usuario
    - GET /users/{id}/ - Obtener detalle de usuario
    - PUT /users/{id}/ - Actualizar usuario
    - DELETE /users/{id}/ - Eliminar usuario
    - GET /users/me/ - Obtener usuario actual
    - GET /users/by_role/ - Filtrar usuarios por rol
    """
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Filtrar usuarios por rol"""
        role = request.query_params.get('role', None)
        if role:
            users = User.objects.filter(role=role)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'role' es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def roles(self, request):
        """Listar todos los roles disponibles"""
        roles = [
            {"code": code, "name": name} 
            for code, name in User.ROLE_CHOICES
        ]
        return Response(roles)
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """Endpoint para subir foto del usuario (para reconocimiento facial)"""
        user = self.get_object()
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
            user.save()
            return Response(
                {"message": "Foto actualizada correctamente"},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "No se proporcionó ninguna foto"},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResidentialUnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de unidades residenciales
    Endpoints:
    - GET /units/ - Listar todas las unidades
    - POST /units/ - Crear nueva unidad
    - GET /units/{id}/ - Obtener detalle de unidad
    - PUT /units/{id}/ - Actualizar unidad
    - DELETE /units/{id}/ - Eliminar unidad
    - POST /units/{id}/add_resident/ - Añadir residente a unidad
    - POST /units/{id}/remove_resident/ - Remover residente de unidad
    """
    queryset = ResidentialUnit.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['unit_number', 'owner__username']
    ordering_fields = ['unit_number', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ResidentialUnitCreateSerializer
        return ResidentialUnitSerializer
    
    @action(detail=True, methods=['post'])
    def add_resident(self, request, pk=None):
        """Añadir un residente a la unidad"""
        unit = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            unit.residents.add(user)
            return Response(
                {"message": f"Residente {user.username} añadido correctamente"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_resident(self, request, pk=None):
        """Remover un residente de la unidad"""
        unit = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            unit.residents.remove(user)
            return Response(
                {"message": f"Residente {user.username} removido correctamente"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def my_units(self, request):
        """Obtener las unidades del usuario actual"""
        units = ResidentialUnit.objects.filter(
            Q(owner=request.user) | Q(residents=request.user)
        ).distinct()
        serializer = ResidentialUnitSerializer(units, many=True)
        return Response(serializer.data)
