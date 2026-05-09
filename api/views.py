# api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from projects.models import Project
from analysis_engine.models import Analisis
from .serializers import (
    ProjectSerializer,
    AnalisisSerializer,
    AnalisisListSerializer,
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proyecto_list(request):
    """
    GET /api/proyectos/
    Devuelve todos los proyectos del usuario autenticado.
    """
    proyectos = Project.objects.filter(user=request.user).order_by('-created_at')
    serializer = ProjectSerializer(proyectos, many=True)
    return Response({
        'count': proyectos.count(),
        'proyectos': serializer.data,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proyecto_detail(request, pk):
    """
    GET /api/proyectos/<pk>/
    Devuelve el detalle de un proyecto con su historial de analisis.
    """
    proyecto = get_object_or_404(Project, pk=pk, user=request.user)
    analisis_list = proyecto.analisis.order_by('-fecha')

    return Response({
        'proyecto': ProjectSerializer(proyecto).data,
        'historial': AnalisisListSerializer(analisis_list, many=True).data,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analisis_list(request):
    """
    GET /api/analisis/
    Devuelve todos los analisis del usuario autenticado (sin vulnerabilidades).
    """
    analisis = Analisis.objects.filter(
        project__user=request.user
    ).select_related('project').order_by('-fecha')

    serializer = AnalisisListSerializer(analisis, many=True)
    return Response({
        'count': analisis.count(),
        'analisis': serializer.data,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analisis_detail(request, pk):
    """
    GET /api/analisis/<pk>/
    Devuelve el detalle completo de un analisis con sus vulnerabilidades.
    """
    analisis = get_object_or_404(
        Analisis, pk=pk, project__user=request.user
    )
    serializer = AnalisisSerializer(analisis)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen(request):
    """
    GET /api/resumen/
    Devuelve estadisticas generales del usuario: totales y mejor score.
    """
    proyectos = Project.objects.filter(user=request.user)
    analisis = Analisis.objects.filter(project__user=request.user)

    mejor = analisis.order_by('-score').values_list('score', flat=True).first()

    return Response({
        'usuario': request.user.username,
        'total_proyectos': proyectos.count(),
        'total_analisis': analisis.count(),
        'mejor_score': mejor if mejor is not None else 'N/A',
    })