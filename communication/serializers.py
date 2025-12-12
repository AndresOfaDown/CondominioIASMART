from rest_framework import serializers
from .models import Announcement, Notification
from users.models import Usuario


class AnnouncementSerializer(serializers.ModelSerializer):
    """Serializer completo para Announcement"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'category', 'author',
            'author_name', 'image', 'is_published', 'published_date',
            'expiry_date', 'is_pinned', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_is_expired(self, obj):
        """Verificar si el aviso ha expirado"""
        if obj.expiry_date:
            from django.utils import timezone
            return obj.expiry_date < timezone.now()
        return False


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear avisos"""
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'image', 'expiry_date', 'is_pinned']


class AnnouncementPublishSerializer(serializers.Serializer):
    """Serializer para publicar avisos"""
    is_published = serializers.BooleanField()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer completo para Notification"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'title', 'message',
            'notification_type', 'is_read', 'link',
            'related_announcement', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones"""
    class Meta:
        model = Notification
        fields = ['user', 'title', 'message', 'notification_type', 'link', 'related_announcement']


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer para enviar notificaciones masivas"""
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPE_CHOICES)
    target_role = serializers.ChoiceField(
        choices=[('ALL', 'Todos')] + list(Usuario.ROLES),
        required=False
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
