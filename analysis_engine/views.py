from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Analisis
from users.views import es_admin


@login_required
def resultado(request, analisis_pk):
    if es_admin(request.user):
        analisis = get_object_or_404(Analisis, pk=analisis_pk)
    else:
        analisis = get_object_or_404(Analisis, pk=analisis_pk, project__user=request.user)

    vulnerabilidades = analisis.vulnerabilidades.all().order_by('-severidad')

    resumen = {
        'criticas': vulnerabilidades.filter(severidad='CRITICA').count(),
        'altas':    vulnerabilidades.filter(severidad='ALTA').count(),
        'medias':   vulnerabilidades.filter(severidad='MEDIA').count(),
        'bajas':    vulnerabilidades.filter(severidad='BAJA').count(),
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
        nivel_texto = 'Critico'

    return render(request, 'analysis_engine/resultado.html', {
        'analisis':         analisis,
        'vulnerabilidades': vulnerabilidades,
        'resumen':          resumen,
        'nivel_color':      nivel_color,
        'nivel_texto':      nivel_texto,
    })


@login_required
def historial(request, proyecto_pk):
    from projects.models import Project
    if es_admin(request.user):
        proyecto = get_object_or_404(Project, pk=proyecto_pk)
    else:
        proyecto = get_object_or_404(Project, pk=proyecto_pk, user=request.user)

    analisis_list = Analisis.objects.filter(project=proyecto)

    return render(request, 'analysis_engine/historial.html', {
        'proyecto':      proyecto,
        'analisis_list': analisis_list,
    })