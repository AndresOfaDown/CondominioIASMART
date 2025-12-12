from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, UnidadResidencial, Residente


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo para Usuario"""
    unidades_propias = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'telefono', 'foto', 'email_verificado',
            'unidades_propias', 'is_active',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'email_verificado']


class UsuarioCrearSerializer(serializers.ModelSerializer):
    """Serializer para creación de usuarios con validación de password"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'rol', 'telefono', 'foto'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Los passwords no coinciden"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = Usuario.objects.create_user(**validated_data)
        return user


class UsuarioActualizarSerializer(serializers.ModelSerializer):
    """Serializer para actualización de usuarios"""
    class Meta:
        model = Usuario
        fields = [
            'email', 'first_name', 'last_name',
            'telefono', 'foto', 'is_active'
        ]


class UsuarioSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para referencias"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nombre_completo', 'telefono', 'rol']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username


# ===================== RESIDENTE SERIALIZERS =====================

class ResidenteSerializer(serializers.ModelSerializer):
    """Serializer para lectura de Residente"""
    usuario_detalle = UsuarioSimpleSerializer(source='usuario', read_only=True)
    numero_unidad = serializers.CharField(source='unidad.numero_unidad', read_only=True)
    tipo_residente_display = serializers.CharField(source='get_tipo_residente_display', read_only=True)
    
    class Meta:
        model = Residente
        fields = [
            'id', 'usuario', 'usuario_detalle', 'unidad', 'numero_unidad',
            'tipo_residente', 'tipo_residente_display', 'es_principal',
            'fecha_ingreso', 'fecha_salida', 'activo', 'notas',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class ResidenteCrearSerializer(serializers.ModelSerializer):
    """Serializer para creación de Residente"""
    class Meta:
        model = Residente
        fields = ['usuario', 'unidad', 'tipo_residente', 'es_principal', 'fecha_ingreso', 'notas']
    
    def validate(self, attrs):
        unidad = attrs.get('unidad')
        es_principal = attrs.get('es_principal', False)
        tipo_residente = attrs.get('tipo_residente')
        
        # Si es principal, verificar que no exista otro principal activo
        if es_principal:
            existing_primary = Residente.objects.filter(
                unidad=unidad, es_principal=True, activo=True
            ).exists()
            if existing_primary:
                raise serializers.ValidationError({
                    "es_principal": "Ya existe un residente principal activo en esta unidad."
                })
        
        # Validar que PROPIETARIO_RESIDENTE sea el propietario
        if tipo_residente == 'PROPIETARIO_RESIDENTE':
            usuario = attrs.get('usuario')
            if unidad.propietario != usuario:
                raise serializers.ValidationError({
                    "tipo_residente": "Solo el propietario puede ser registrado como PROPIETARIO_RESIDENTE."
                })
        
        return attrs


class ResidenteActualizarSerializer(serializers.ModelSerializer):
    """Serializer para actualización de Residente"""
    class Meta:
        model = Residente
        fields = ['es_principal', 'fecha_salida', 'activo', 'notas']


# ===================== UNIDAD RESIDENCIAL SERIALIZERS =====================

class UnidadResidencialSerializer(serializers.ModelSerializer):
    """Serializer para UnidadResidencial"""
    propietario_nombre = serializers.CharField(source='propietario.get_full_name', read_only=True)
    propietario_detalle = UsuarioSimpleSerializer(source='propietario', read_only=True)
    estado_ocupacion_display = serializers.CharField(source='get_estado_ocupacion_display', read_only=True)
    residentes_activos = ResidenteSerializer(source='obtener_residentes_activos', many=True, read_only=True)
    residente_principal = ResidenteSerializer(source='obtener_residente_principal', read_only=True)
    cantidad_residentes = serializers.SerializerMethodField()
    
    class Meta:
        model = UnidadResidencial
        fields = [
            'id', 'numero_unidad', 'propietario', 'propietario_nombre', 'propietario_detalle',
            'estado_ocupacion', 'estado_ocupacion_display',
            'piso', 'superficie_m2', 'dormitorios', 'banos', 'descripcion',
            'activo', 'residentes_activos', 'residente_principal', 'cantidad_residentes',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_cantidad_residentes(self, obj):
        return obj.residentes.filter(activo=True).count()


class UnidadResidencialCrearSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear unidades"""
    class Meta:
        model = UnidadResidencial
        fields = ['numero_unidad', 'propietario', 'piso', 'superficie_m2', 'dormitorios', 'banos', 'descripcion']


class UnidadResidencialActualizarSerializer(serializers.ModelSerializer):
    """Serializer para actualizar unidades"""
    class Meta:
        model = UnidadResidencial
        fields = ['estado_ocupacion', 'piso', 'superficie_m2', 'dormitorios', 'banos', 'descripcion', 'activo']
