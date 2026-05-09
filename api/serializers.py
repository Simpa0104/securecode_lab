# api/serializers.py
from rest_framework import serializers
from projects.models import Project
from analysis_engine.models import Analisis, Vulnerabilidad


# ──────────────────────────────────────────────
# VULNERABILIDAD
# ──────────────────────────────────────────────

class VulnerabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerabilidad
        fields = [
            'id', 'regla_id', 'nombre', 'severidad',
            'descripcion', 'recomendacion', 'archivo',
            'linea', 'codigo_linea',
        ]


# ──────────────────────────────────────────────
# ANÁLISIS – LECTURA
# ──────────────────────────────────────────────

class AnalisisSerializer(serializers.ModelSerializer):
    vulnerabilidades = VulnerabilidadSerializer(many=True, read_only=True)
    proyecto_nombre  = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model  = Analisis
        fields = ['id', 'proyecto_nombre', 'nivel', 'score', 'fecha', 'vulnerabilidades']


class AnalisisListSerializer(serializers.ModelSerializer):
    proyecto_nombre       = serializers.CharField(source='project.name', read_only=True)
    total_vulnerabilidades = serializers.IntegerField(
        source='vulnerabilidades.count', read_only=True
    )

    class Meta:
        model  = Analisis
        fields = ['id', 'proyecto_nombre', 'nivel', 'score', 'fecha', 'total_vulnerabilidades']


# ──────────────────────────────────────────────
# PROYECTO – LECTURA
# ──────────────────────────────────────────────

class ProjectSerializer(serializers.ModelSerializer):
    total_analisis = serializers.IntegerField(source='analisis.count', read_only=True)
    ultimo_score   = serializers.SerializerMethodField()

    class Meta:
        model  = Project
        fields = ['id', 'name', 'description', 'filename', 'status',
                'created_at', 'total_analisis', 'ultimo_score']

    def get_ultimo_score(self, obj):
        ultimo = obj.analisis.order_by('-fecha').first()
        return ultimo.score if ultimo else None


# ──────────────────────────────────────────────
# PROYECTO – ESCRITURA (POST / PUT / PATCH)
# ──────────────────────────────────────────────

class ProjectWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Project
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El nombre no puede estar vacío.')
        if len(value) > 200:
            raise serializers.ValidationError('El nombre no puede superar 200 caracteres.')
        return value

    def create(self, validated_data):
        return Project.objects.create(status='pending', **validated_data)

    def update(self, instance, validated_data):
        instance.name        = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance