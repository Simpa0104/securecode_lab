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
    """Serializer liviano para listados (sin vulnerabilidades)."""
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