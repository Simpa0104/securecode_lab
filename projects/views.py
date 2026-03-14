from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from users.views import es_admin


@login_required
def project_list(request):
    if es_admin(request.user):
        projects = Project.objects.all().select_related('user')
    else:
        projects = Project.objects.filter(user=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_create(request):
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
    if es_admin(request.user):
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    return render(request, 'projects/project_detail.html', {'project': project})


@login_required
def project_delete(request, pk):
    if es_admin(request.user):
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        name = project.name
        project.file.delete()
        project.delete()
        messages.success(request, f'Proyecto "{name}" eliminado.')
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {'project': project})