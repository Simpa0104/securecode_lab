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
    ProjectWriteSerializer,
    AnalisisSerializer,
    AnalisisListSerializer,
)


# ──────────────────────────────────────────────
# PROYECTOS
# ──────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def proyecto_list(request):
    if request.method == 'GET':
        proyectos = Project.objects.filter(user=request.user).order_by('-created_at')
        serializer = ProjectSerializer(proyectos, many=True)
        return Response({
            'count': proyectos.count(),
            'proyectos': serializer.data,
        })

    # POST
    serializer = ProjectWriteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def proyecto_detail(request, pk):
    proyecto = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'GET':
        analisis_qs = proyecto.analisis.order_by('-fecha')
        return Response({
            'proyecto': ProjectSerializer(proyecto).data,
            'historial': AnalisisListSerializer(analisis_qs, many=True).data,
        })

    if request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = ProjectWriteSerializer(proyecto, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    nombre = proyecto.name
    proyecto.delete()
    return Response(
        {'mensaje': f'Proyecto "{nombre}" eliminado correctamente.'},
        status=status.HTTP_200_OK,
    )


# ──────────────────────────────────────────────
# ANÁLISIS
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analisis_list(request):
    analisis = Analisis.objects.filter(
        project__user=request.user
    ).select_related('project').order_by('-fecha')

    serializer = AnalisisListSerializer(analisis, many=True)
    return Response({
        'count': analisis.count(),
        'analisis': serializer.data,
    })


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def analisis_detail(request, pk):
    analisis = get_object_or_404(Analisis, pk=pk, project__user=request.user)

    if request.method == 'GET':
        serializer = AnalisisSerializer(analisis)
        return Response(serializer.data)

    # DELETE
    proyecto_nombre = analisis.project.name
    fecha = analisis.fecha
    analisis.delete()
    return Response(
        {
            'mensaje': (
                f'Análisis del proyecto "{proyecto_nombre}" '
                f'con fecha {fecha} eliminado correctamente.'
            )
        },
        status=status.HTTP_200_OK,
    )


# ──────────────────────────────────────────────
# RESUMEN
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen(request):
    proyectos = Project.objects.filter(user=request.user)
    analisis = Analisis.objects.filter(project__user=request.user)

    mejor = analisis.order_by('-score').values_list('score', flat=True).first()

    return Response({
        'usuario': request.user.username,
        'total_proyectos': proyectos.count(),
        'total_analisis': analisis.count(),
        'mejor_score': mejor if mejor is not None else 'N/A',
    })