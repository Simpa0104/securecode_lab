from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile
from projects.models import Project
from analysis_engine.models import Analisis


def es_admin(user):
    """
    Retorna True si el usuario es admin.
    Un usuario es admin si es superusuario de Django
    o tiene un Profile con role='admin'.
    """
    if user.is_superuser:
        return True
    try:
        return user.profile.role == 'admin'
    except Profile.DoesNotExist:
        return False


@login_required
def home(request):
    """Redirige al dashboard según el rol del usuario."""
    if es_admin(request.user):
        return redirect('dashboard_admin')
    return redirect('dashboard_estudiante')


@login_required
def dashboard_estudiante(request):
    """Dashboard principal del estudiante."""
    if es_admin(request.user):
        return redirect('dashboard_admin')

    proyectos = Project.objects.filter(user=request.user)
    ultimos_analisis = Analisis.objects.filter(
        project__user=request.user
    ).select_related('project')[:5]

    total_proyectos = proyectos.count()
    proyectos_analizados = proyectos.filter(status='analyzed').count()
    mejor_score = Analisis.objects.filter(
        project__user=request.user
    ).order_by('-score').values_list('score', flat=True).first()

    return render(request, 'users/dashboard_estudiante.html', {
        'proyectos': proyectos[:4],
        'ultimos_analisis': ultimos_analisis,
        'total_proyectos': total_proyectos,
        'proyectos_analizados': proyectos_analizados,
        'mejor_score': mejor_score or 'N/A',
    })


@login_required
def dashboard_admin(request):
    """Dashboard del administrador."""
    if not es_admin(request.user):
        return redirect('dashboard_estudiante')

    total_usuarios = User.objects.count()
    total_proyectos = Project.objects.count()
    total_analisis = Analisis.objects.count()
    ultimos_analisis = Analisis.objects.select_related(
        'project', 'project__user'
    ).order_by('-fecha')[:10]
    usuarios_recientes = User.objects.select_related('profile').order_by('-date_joined')[:10]

    return render(request, 'users/dashboard_admin.html', {
        'total_usuarios': total_usuarios,
        'total_proyectos': total_proyectos,
        'total_analisis': total_analisis,
        'ultimos_analisis': ultimos_analisis,
        'usuarios_recientes': usuarios_recientes,
    })


@login_required
def gestion_usuarios(request):
    """Lista todos los usuarios del sistema (RF-11)."""
    if not es_admin(request.user):
        return redirect('dashboard_estudiante')

    usuarios = User.objects.select_related('profile').order_by('-date_joined')

    return render(request, 'users/gestion_usuarios.html', {
        'usuarios': usuarios,
    })


@login_required
def editar_usuario(request, user_pk):
    """Permite al admin editar rol y estado de un usuario (RF-11)."""
    if not es_admin(request.user):
        return redirect('dashboard_estudiante')

    usuario = get_object_or_404(User, pk=user_pk)
    es_mismo_usuario = usuario.pk == request.user.pk

    profile, _ = Profile.objects.get_or_create(
        user=usuario,
        defaults={'role': 'student'}
    )

    if request.method == 'POST':
        nuevo_rol = request.POST.get('role')
        activo = request.POST.get('is_active') == 'on'

        if nuevo_rol in ['student', 'admin']:
            profile.role = nuevo_rol
            profile.save()

        if not es_mismo_usuario:
            usuario.is_active = activo
            usuario.save()

        messages.success(request, f'Usuario "{usuario.username}" actualizado correctamente.')
        return redirect('gestion_usuarios')

    return render(request, 'users/editar_usuario.html', {
        'usuario': usuario,
        'profile': profile,
        'es_mismo_usuario': es_mismo_usuario,
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role='student')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
