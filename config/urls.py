# config/urls.py
from django.contrib import admin
from django.urls import path, include
from users.views import (
    home, register, dashboard_estudiante, dashboard_admin,
    dashboard_monitor, gestion_usuarios, editar_usuario,
    eliminar_usuario, perfil
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard_estudiante, name='dashboard_estudiante'),
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/monitor/', dashboard_monitor, name='dashboard_monitor'),
    path('perfil/', perfil, name='perfil'),
    path('usuarios/', gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/<int:user_pk>/editar/', editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_pk>/eliminar/', eliminar_usuario, name='eliminar_usuario'),
    path('projects/', include('projects.urls')),
    path('analysis/', include('analysis_engine.urls')),
]
