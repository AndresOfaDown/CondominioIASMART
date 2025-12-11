from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Announcement, Notification
from users.models import User
from .serializers import (
    AnnouncementSerializer, AnnouncementCreateSerializer, AnnouncementPublishSerializer,
    NotificationSerializer, NotificationCreateSerializer, BulkNotificationSerializer
)


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de avisos y comunicados
    Endpoints:
    - GET /announcements/ - Listar todos los avisos
    - POST /announcements/ - Crear nuevo aviso
    - GET /announcements/{id}/ - Obtener detalle de aviso
    - PUT /announcements/{id}/ - Actualizar aviso
    - DELETE /announcements/{id}/ - Eliminar aviso
    - GET /announcements/published/ - Listar avisos publicados
    - POST /announcements/{id}/publish/ - Publicar aviso
    - POST /announcements/{id}/unpublish/ - Despublicar aviso
    """
    queryset = Announcement.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'category']
    ordering_fields = ['created_at', 'published_date', 'is_pinned']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AnnouncementCreateSerializer
        elif self.action in ['publish', 'unpublish']:
            return AnnouncementPublishSerializer
        return AnnouncementSerializer
    
    def perform_create(self, serializer):
        """Asignar autor actual al crear aviso"""
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        """Obtener solo avisos publicados y no expirados"""
        now = timezone.now()
        announcements = Announcement.objects.filter(
            is_published=True
        ).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gt=now)
        )
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publicar un aviso"""
        announcement = self.get_object()
        announcement.is_published = True
        announcement.published_date = timezone.now()
        announcement.save()
        
        # Crear notificaciones para todos los usuarios
        users = User.objects.filter(is_active=True)
        notifications = [
            Notification(
                user=user,
                title=f"Nuevo aviso: {announcement.title}",
                message=announcement.content[:200],
                notification_type='INFO',
                related_announcement=announcement
            ) for user in users
        ]
        Notification.objects.bulk_create(notifications)
        
        return Response(
            {"message": "Aviso publicado y notificaciones enviadas"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Despublicar un aviso"""
        announcement = self.get_object()
        announcement.is_published = False
        announcement.save()
        
        return Response(
            {"message": "Aviso despublicado correctamente"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Filtrar avisos por categoría"""
        category = request.query_params.get('category')
        if category:
            announcements = Announcement.objects.filter(
                category=category,
                is_published=True
            )
            serializer = AnnouncementSerializer(announcements, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "El parámetro 'category' es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de notificaciones
    Endpoints:
    - GET /notifications/ - Listar todas las notificaciones
    - POST /notifications/ - Crear nueva notificación
    - GET /notifications/{id}/ - Obtener detalle de notificación
    - PUT /notifications/{id}/ - Actualizar notificación
    - DELETE /notifications/{id}/ - Eliminar notificación
    - GET /notifications/my_notifications/ - Obtener notificaciones del usuario
    - GET /notifications/unread/ - Obtener notificaciones no leídas
    - POST /notifications/{id}/mark_read/ - Marcar como leída
    - POST /notifications/mark_all_read/ - Marcar todas como leídas
    - POST /notifications/send_bulk/ - Enviar notificaciones masivas
    """
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'is_read']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action == 'send_bulk':
            return BulkNotificationSerializer
        return NotificationSerializer
    
    @action(detail=False, methods=['get'])
    def my_notifications(self, request):
        """Obtener notificaciones del usuario actual"""
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Obtener notificaciones no leídas del usuario actual"""
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marcar una notificación como leída"""
        notification = self.get_object()
        notification.mark_as_read()
        
        return Response(
            {"message": "Notificación marcada como leída"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marcar todas las notificaciones del usuario como leídas"""
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        
        for notification in notifications:
            notification.mark_as_read()
        
        return Response(
            {"message": f"{notifications.count()} notificaciones marcadas como leídas"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def send_bulk(self, request):
        """Enviar notificaciones masivas"""
        serializer = BulkNotificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        title = data['title']
        message = data['message']
        notification_type = data['notification_type']
        
        # Determinar destinatarios
        if 'user_ids' in data and data['user_ids']:
            users = User.objects.filter(id__in=data['user_ids'])
        elif 'target_role' in data and data['target_role'] != 'ALL':
            users = User.objects.filter(role=data['target_role'])
        else:
            users = User.objects.filter(is_active=True)
        
        # Crear notificaciones
        notifications = [
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type
            ) for user in users
        ]
        
        Notification.objects.bulk_create(notifications)
        
        return Response(
            {
                "message": f"Se enviaron {len(notifications)} notificaciones",
                "count": len(notifications)
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de notificaciones del usuario"""
        user = request.user
        total = Notification.objects.filter(user=user).count()
        unread = Notification.objects.filter(user=user, is_read=False).count()
        read = total - unread
        
        return Response({
            'total': total,
            'read': read,
            'unread': unread
        })
