# api/urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # Autenticacion: POST con username+password, devuelve token
    path('token/', obtain_auth_token, name='api_token'),

    # Proyectos
    path('proyectos/', views.proyecto_list, name='api_proyecto_list'),
    path('proyectos/<int:pk>/', views.proyecto_detail, name='api_proyecto_detail'),

    # Analisis
    path('analisis/', views.analisis_list, name='api_analisis_list'),
    path('analisis/<int:pk>/', views.analisis_detail, name='api_analisis_detail'),

    # Resumen general
    path('resumen/', views.resumen, name='api_resumen'),
]