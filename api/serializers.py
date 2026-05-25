# api/serializers.py
from rest_framework import serializers
from projects.models import Project
from analysis_engine.models import Analisis, Vulnerabilidad

class VulnerabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerabilidad
        fields = [
            'id', 'regla_id', 'nombre', 'severidad',
            'descripcion', 'recomendacion', 'archivo',
            'linea', 'codigo_linea',
        ]

class AnalisisSerializer(serializers.ModelSerializer):
    vulnerabilidades = VulnerabilidadSerializer(many=True, read_only=True)
    proyecto_nombre = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Analisis
        fields = [
            'id', 'proyecto_nombre', 'nivel', 'score',
            'fecha', 'vulnerabilidades',
        ]


class AnalisisListSerializer(serializers.ModelSerializer):
    proyecto_nombre = serializers.CharField(source='project.name', read_only=True)
    total_vulnerabilidades = serializers.IntegerField(
        source='vulnerabilidades.count', read_only=True
    )

    class Meta:
        model = Analisis
        fields = [
            'id', 'proyecto_nombre', 'nivel',
            'score', 'fecha', 'total_vulnerabilidades',
        ]

class ProjectSerializer(serializers.ModelSerializer):
    total_analisis = serializers.IntegerField(
        source='analisis.count', read_only=True
    )
    ultimo_score = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'filename',
            'status', 'created_at', 'total_analisis', 'ultimo_score',
        ]

    def get_ultimo_score(self, obj):
        ultimo = obj.analisis.order_by('-fecha').first()
        return ultimo.score if ultimo else None

class ProjectWriteSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, write_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'file']
        read_only_fields = ['id']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El nombre del proyecto no puede estar vacío.')
        if len(value) > 200:
            raise serializers.ValidationError('El nombre no puede superar los 200 caracteres.')
        return value

    def validate_file(self, value):
        extensiones_permitidas = ('.py', '.zip')
        nombre = value.name.lower()
        if not nombre.endswith(extensiones_permitidas):
            raise serializers.ValidationError(
                'Tipo de archivo no permitido. Extensiones aceptadas: .py, .zip'
            )
        limite_bytes = 5 * 1024 * 1024  # 5 MB
        if value.size > limite_bytes:
            raise serializers.ValidationError('El archivo no puede superar los 5 MB.')
        return value

    def create(self, validated_data):
        archivo = validated_data.pop('file', None)
        proyecto = Project(**validated_data)
        if archivo:
            proyecto.file = archivo
            proyecto.filename = archivo.name
        proyecto.status = 'pending'
        proyecto.save()
        return proyecto

    def update(self, instance, validated_data):
        archivo = validated_data.pop('file', None)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        if archivo:
            instance.file = archivo
            instance.filename = archivo.name
            instance.status = 'pending'
        instance.save()
        return instance