from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm


@login_required
def project_list(request):
    """Lista todos los proyectos del usuario autenticado (RF-9)."""
    projects = Project.objects.filter(user=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    """Permite al estudiante crear y subir un nuevo proyecto (RF-4, RF-5)."""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, f'Proyecto "{project.name}" creado exitosamente.')
            return redirect('project_list')

    else:
        form = ProjectForm()

    return render(request, 'projects/project_create.html', {'form': form})


@login_required
def project_detail(request, pk):
    """Muestra el detalle de un proyecto específico del usuario."""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    return render(request, 'projects/project_detail.html', {'project': project})


@login_required
def project_delete(request, pk):
    """Elimina un proyecto del usuario."""
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        name = project.name
        project.file.delete()  # Elimina el archivo físico también
        project.delete()
        messages.success(request, f'Proyecto "{name}" eliminado.')
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {'project': project})