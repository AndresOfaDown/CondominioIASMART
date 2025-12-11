from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, ResidentialUnit


class UserSerializer(serializers.ModelSerializer):
    """Serializer completo para User"""
    owned_units = serializers.StringRelatedField(many=True, read_only=True)
    residing_units = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'photo', 'email_verified',
            'owned_units', 'residing_units', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'email_verified']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de usuarios con validación de password"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'role', 'phone', 'photo'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Los passwords no coinciden"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualización de usuarios"""
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'phone', 'photo', 'is_active'
        ]


class ResidentialUnitSerializer(serializers.ModelSerializer):
    """Serializer para ResidentialUnit"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    residents_list = UserSerializer(source='residents', many=True, read_only=True)
    
    class Meta:
        model = ResidentialUnit
        fields = [
            'id', 'unit_number', 'owner', 'owner_name',
            'residents', 'residents_list', 'floor', 'size_sqm',
            'bedrooms', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResidentialUnitCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear unidades"""
    class Meta:
        model = ResidentialUnit
        fields = ['unit_number', 'owner', 'floor', 'size_sqm', 'bedrooms']
