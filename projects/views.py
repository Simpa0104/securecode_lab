# projects/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Project
from .forms import ProjectForm
from analysis_engine.models import Analisis, Vulnerabilidad
from analysis_engine.analyzer import ejecutar_analisis
from users.views import es_admin, es_monitor


@login_required
def project_list(request):
    busqueda = request.GET.get('q', '').strip()

    if es_admin(request.user):
        projects = Project.objects.all().select_related('user')
    else:
        projects = Project.objects.filter(user=request.user)

    if busqueda:
        projects = projects.filter(
            Q(name__icontains=busqueda) |
            Q(description__icontains=busqueda)
        )

    paginator = Paginator(projects.order_by('-created_at'), 10)
    pagina_num = request.GET.get('pagina', 1)
    pagina = paginator.get_page(pagina_num)

    return render(request, 'projects/project_list.html', {
        'projects': pagina,
        'busqueda': busqueda,
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            nivel = form.cleaned_data['nivel']

            try:
                resultado = ejecutar_analisis(archivo, nivel)

                project = form.save(commit=False)
                project.user = request.user
                project.filename = archivo.name
                project.status = 'analyzed'
                project.save()

                analisis = Analisis.objects.create(
                    project=project,
                    nivel=nivel,
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

                messages.success(
                    request,
                    f'Analisis completado. Score: {resultado["score"]}/100'
                )
                return redirect('analisis_resultado', analisis_pk=analisis.pk)

            except Exception as e:
                messages.error(request, f'Error al analizar el proyecto: {str(e)}')
                return render(request, 'projects/project_create.html', {'form': form})
    else:
        form = ProjectForm()

    return render(request, 'projects/project_create.html', {'form': form})


@login_required
def project_detail(request, pk):
    if es_admin(request.user):
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    analisis_list = project.analisis.all()
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'analisis_list': analisis_list,
    })


@login_required
def project_delete(request, pk):
    if es_admin(request.user):
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Proyecto "{name}" eliminado.')
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {'project': project})