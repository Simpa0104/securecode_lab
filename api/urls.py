# api/urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token'),
    path('proyectos/', views.proyecto_list, name='api_proyecto_list'),
    path('proyectos/<int:pk>/', views.proyecto_detail, name='api_proyecto_detail'),
    path('resumen/', views.resumen, name='api_resumen'),
]