# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from .forms import RegisterForm
from .models import Profile
from projects.models import Project
from analysis_engine.models import Analisis


def es_admin(user):
    if user.is_superuser:
        return True
    try:
        return user.profile.role == 'admin'
    except Profile.DoesNotExist:
        return False


def es_monitor(user):
    try:
        return user.profile.role == 'monitor'
    except Profile.DoesNotExist:
        return False


@login_required
def home(request):
    if es_admin(request.user):
        return redirect('dashboard_admin')
    if es_monitor(request.user):
        return redirect('dashboard_monitor')
    return redirect('dashboard_estudiante')


@login_required
def dashboard_estudiante(request):
    if es_admin(request.user):
        return redirect('dashboard_admin')
    if es_monitor(request.user):
        return redirect('dashboard_monitor')

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
def dashboard_monitor(request):
    if es_admin(request.user):
        return redirect('dashboard_admin')
    if not es_monitor(request.user):
        return redirect('dashboard_estudiante')

    busqueda_analisis = request.GET.get('q_analisis', '').strip()

    try:
        clase_monitor = request.user.profile.numero_clase
    except Profile.DoesNotExist:
        clase_monitor = ''

    if clase_monitor:
        estudiantes_ids = User.objects.filter(
            profile__role='student',
            profile__numero_clase=clase_monitor
        ).values_list('id', flat=True)

        analisis_qs = Analisis.objects.filter(
            project__user__id__in=estudiantes_ids
        ).select_related('project', 'project__user')

        total_proyectos = Project.objects.filter(
            user__id__in=estudiantes_ids
        ).count()
    else:
        analisis_qs = Analisis.objects.select_related(
            'project', 'project__user'
        ).filter(project__user__profile__role='student')

        total_proyectos = Project.objects.count()

    total_analisis = analisis_qs.count()

    if busqueda_analisis:
        analisis_qs = analisis_qs.filter(
            Q(project__name__icontains=busqueda_analisis) |
            Q(project__user__username__icontains=busqueda_analisis) |
            Q(project__user__first_name__icontains=busqueda_analisis) |
            Q(project__user__last_name__icontains=busqueda_analisis)
        )

    ultimos_analisis = analisis_qs.order_by('-fecha')[:15]

    return render(request, 'users/dashboard_monitor.html', {
        'total_proyectos': total_proyectos,
        'total_analisis': total_analisis,
        'ultimos_analisis': ultimos_analisis,
        'busqueda_analisis': busqueda_analisis,
        'clase_monitor': clase_monitor,
    })


@login_required
def dashboard_admin(request):
    if not es_admin(request.user):
        if es_monitor(request.user):
            return redirect('dashboard_monitor')
        return redirect('dashboard_estudiante')

    busqueda_usuarios = request.GET.get('q_usuarios', '').strip()
    busqueda_analisis = request.GET.get('q_analisis', '').strip()
    filtro_clase_usuarios = request.GET.get('clase_usuarios', '').strip()
    filtro_clase_analisis = request.GET.get('clase_analisis', '').strip()
    pagina_usuarios_num = request.GET.get('pagina_usuarios', 1)

    total_usuarios = User.objects.count()
    total_proyectos = Project.objects.count()
    total_analisis = Analisis.objects.count()

    usuarios_qs = User.objects.select_related('profile').order_by('-date_joined')
    if busqueda_usuarios:
        usuarios_qs = usuarios_qs.filter(
            Q(username__icontains=busqueda_usuarios) |
            Q(first_name__icontains=busqueda_usuarios) |
            Q(last_name__icontains=busqueda_usuarios) |
            Q(email__icontains=busqueda_usuarios)
        )
    if filtro_clase_usuarios:
        usuarios_qs = usuarios_qs.filter(profile__numero_clase=filtro_clase_usuarios)

    paginator_usuarios = Paginator(usuarios_qs, 8)
    usuarios_recientes = paginator_usuarios.get_page(pagina_usuarios_num)

    analisis_qs = Analisis.objects.select_related(
        'project', 'project__user'
    ).order_by('-fecha')
    if busqueda_analisis:
        analisis_qs = analisis_qs.filter(
            Q(project__name__icontains=busqueda_analisis) |
            Q(project__user__username__icontains=busqueda_analisis) |
            Q(project__user__first_name__icontains=busqueda_analisis) |
            Q(project__user__last_name__icontains=busqueda_analisis)
        )
    if filtro_clase_analisis:
        analisis_qs = analisis_qs.filter(
            project__user__profile__numero_clase=filtro_clase_analisis
        )
    ultimos_analisis = analisis_qs[:10]

    return render(request, 'users/dashboard_admin.html', {
        'total_usuarios': total_usuarios,
        'total_proyectos': total_proyectos,
        'total_analisis': total_analisis,
        'ultimos_analisis': ultimos_analisis,
        'usuarios_recientes': usuarios_recientes,
        'busqueda_usuarios': busqueda_usuarios,
        'busqueda_analisis': busqueda_analisis,
        'filtro_clase_usuarios': filtro_clase_usuarios,
        'filtro_clase_analisis': filtro_clase_analisis,
        'clases': Profile.CLASE_CHOICES,
    })


@login_required
def gestion_usuarios(request):
    if not es_admin(request.user):
        if es_monitor(request.user):
            return redirect('dashboard_monitor')
        return redirect('dashboard_estudiante')

    busqueda = request.GET.get('q', '').strip()
    filtro_clase = request.GET.get('clase', '').strip()

    usuarios = User.objects.select_related('profile').order_by('-date_joined')

    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    if filtro_clase:
        usuarios = usuarios.filter(profile__numero_clase=filtro_clase)

    paginator = Paginator(usuarios, 15)
    pagina_num = request.GET.get('pagina', 1)
    pagina = paginator.get_page(pagina_num)

    return render(request, 'users/gestion_usuarios.html', {
        'usuarios': pagina,
        'busqueda': busqueda,
        'filtro_clase': filtro_clase,
        'clases': Profile.CLASE_CHOICES,
    })


@login_required
def editar_usuario(request, user_pk):
    if not es_admin(request.user):
        if es_monitor(request.user):
            return redirect('dashboard_monitor')
        return redirect('dashboard_estudiante')

    usuario = get_object_or_404(User, pk=user_pk)
    es_mismo_usuario = usuario.pk == request.user.pk

    profile, _ = Profile.objects.get_or_create(
        user=usuario,
        defaults={'role': 'student'}
    )

    if request.method == 'POST':
        nuevo_username = request.POST.get('username', '').strip()
        nuevo_email = request.POST.get('email', '').strip()
        nuevo_rol = request.POST.get('role')
        nuevo_numero_clase = request.POST.get('numero_clase', '')
        activo = request.POST.get('is_active') == 'on'

        if not nuevo_username:
            messages.error(request, 'El nombre de usuario no puede estar vacio.')
            return render(request, 'users/editar_usuario.html', {
                'usuario': usuario, 'profile': profile,
                'es_mismo_usuario': es_mismo_usuario,
                'clases': Profile.CLASE_CHOICES,
            })

        if User.objects.filter(username=nuevo_username).exclude(pk=usuario.pk).exists():
            messages.error(request, f'El nombre de usuario "{nuevo_username}" ya esta en uso.')
            return render(request, 'users/editar_usuario.html', {
                'usuario': usuario, 'profile': profile,
                'es_mismo_usuario': es_mismo_usuario,
                'clases': Profile.CLASE_CHOICES,
            })

        usuario.username = nuevo_username
        usuario.email = nuevo_email

        if not es_mismo_usuario:
            usuario.is_active = activo

        usuario.save()

        if nuevo_rol in ['student', 'monitor', 'admin']:
            profile.role = nuevo_rol

        profile.numero_clase = nuevo_numero_clase if nuevo_rol in ['student', 'monitor'] else ''
        profile.save()

        messages.success(request, f'Usuario "{nuevo_username}" actualizado correctamente.')
        return redirect('gestion_usuarios')

    return render(request, 'users/editar_usuario.html', {
        'usuario': usuario,
        'profile': profile,
        'es_mismo_usuario': es_mismo_usuario,
        'clases': Profile.CLASE_CHOICES,
    })


@login_required
def eliminar_usuario(request, user_pk):
    if not es_admin(request.user):
        if es_monitor(request.user):
            return redirect('dashboard_monitor')
        return redirect('dashboard_estudiante')

    usuario = get_object_or_404(User, pk=user_pk)

    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('gestion_usuarios')

    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" eliminado correctamente.')
        return redirect('gestion_usuarios')

    return render(request, 'users/confirmar_eliminar_usuario.html', {'usuario': usuario})


@login_required
def perfil(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'datos':
            nuevo_nombre = request.POST.get('first_name', '').strip()
            nuevo_apellido = request.POST.get('last_name', '').strip()
            nuevo_email = request.POST.get('email', '').strip()

            request.user.first_name = nuevo_nombre
            request.user.last_name = nuevo_apellido
            request.user.email = nuevo_email
            request.user.save()

            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('perfil')

        elif accion == 'contrasena':
            contrasena_actual = request.POST.get('contrasena_actual', '')
            contrasena_nueva = request.POST.get('contrasena_nueva', '')
            contrasena_confirmar = request.POST.get('contrasena_confirmar', '')

            if not request.user.check_password(contrasena_actual):
                messages.error(request, 'La contrasena actual es incorrecta.')
                return redirect('perfil')

            if len(contrasena_nueva) < 8:
                messages.error(request, 'La nueva contrasena debe tener al menos 8 caracteres.')
                return redirect('perfil')

            if contrasena_nueva != contrasena_confirmar:
                messages.error(request, 'Las contrasenas nuevas no coinciden.')
                return redirect('perfil')

            request.user.set_password(contrasena_nueva)
            request.user.save()
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Contrasena actualizada correctamente.')
            return redirect('perfil')

    return render(request, 'users/perfil.html')


def register(request):
    hay_admin = User.objects.filter(
        profile__role='admin'
    ).exists() or User.objects.filter(is_superuser=True).exists()

    mostrar_admin = not hay_admin

    if request.method == 'POST':
        form = RegisterForm(request.POST, mostrar_admin=mostrar_admin)
        if form.is_valid():
            user = form.save()
            grupo = form.cleaned_data.get('grupo', 'student')

            if grupo == 'admin' and not mostrar_admin:
                grupo = 'student'

            numero_clase = ''
            if grupo in ['student', 'monitor']:
                numero_clase = form.cleaned_data.get('numero_clase', '')

            Profile.objects.create(
                user=user,
                role=grupo,
                numero_clase=numero_clase
            )
            messages.success(request, 'Cuenta creada correctamente. Ya puedes iniciar sesion.')
            return redirect('login')
    else:
        form = RegisterForm(mostrar_admin=mostrar_admin)

    return render(request, 'registration/register.html', {
        'form': form,
        'mostrar_admin': mostrar_admin,
    })
