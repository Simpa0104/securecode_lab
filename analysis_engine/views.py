from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.models import Project
from .models import Analisis, Vulnerabilidad
from .analyzer import ejecutar_analisis
from users.views import es_admin


@login_required
def ejecutar(request, proyecto_pk):
    if es_admin(request.user):
        proyecto = get_object_or_404(Project, pk=proyecto_pk)
    else:
        proyecto = get_object_or_404(Project, pk=proyecto_pk, user=request.user)

    if request.method == 'POST':
        try:
            resultado = ejecutar_analisis(proyecto)

            analisis = Analisis.objects.create(
                project=proyecto,
                nivel='BASICO',
                score=resultado['score'],
            )

            for vuln in resultado['vulnerabilidades']:
                Vulnerabilidad.objects.create(
                    analisis=analisis,
                    regla_id=vuln['regla_id'],
                    nombre=vuln['nombre'],
                    severidad=vuln['severidad'],
                    descripcion=vuln['descripcion'],
                    recomendacion=vuln['recomendacion'],
                    archivo=vuln['archivo'],
                    linea=vuln['linea'],
                    codigo_linea=vuln['codigo_linea'],
                )

            proyecto.status = 'analyzed'
            proyecto.save()

            messages.success(request, f'Análisis completado. Score: {resultado["score"]}/100')
            return redirect('analisis_resultado', analisis_pk=analisis.pk)

        except Exception as e:
            proyecto.status = 'error'
            proyecto.save()
            messages.error(request, f'Error al analizar el proyecto: {str(e)}')
            return redirect('project_detail', pk=proyecto_pk)

    return redirect('project_detail', pk=proyecto_pk)


@login_required
def resultado(request, analisis_pk):
    if es_admin(request.user):
        analisis = get_object_or_404(Analisis, pk=analisis_pk)
    else:
        analisis = get_object_or_404(Analisis, pk=analisis_pk, project__user=request.user)

    vulnerabilidades = analisis.vulnerabilidades.all().order_by('-severidad')

    resumen = {
        'criticas': vulnerabilidades.filter(severidad='CRITICA').count(),
        'altas': vulnerabilidades.filter(severidad='ALTA').count(),
        'medias': vulnerabilidades.filter(severidad='MEDIA').count(),
        'bajas': vulnerabilidades.filter(severidad='BAJA').count(),
    }

    if analisis.score >= 80:
        nivel_color = 'success'
        nivel_texto = 'Seguro'
    elif analisis.score >= 60:
        nivel_color = 'warning'
        nivel_texto = 'Aceptable'
    elif analisis.score >= 40:
        nivel_color = 'orange'
        nivel_texto = 'Vulnerable'
    else:
        nivel_color = 'danger'
        nivel_texto = 'Crítico'

    return render(request, 'analysis_engine/resultado.html', {
        'analisis': analisis,
        'vulnerabilidades': vulnerabilidades,
        'resumen': resumen,
        'nivel_color': nivel_color,
        'nivel_texto': nivel_texto,
    })


@login_required
def historial(request, proyecto_pk):
    if es_admin(request.user):
        proyecto = get_object_or_404(Project, pk=proyecto_pk)
    else:
        proyecto = get_object_or_404(Project, pk=proyecto_pk, user=request.user)

    analisis_list = Analisis.objects.filter(project=proyecto)

    return render(request, 'analysis_engine/historial.html', {
        'proyecto': proyecto,
        'analisis_list': analisis_list,
    })
