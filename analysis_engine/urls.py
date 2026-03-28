from django.urls import path
from . import views

urlpatterns = [
    path('resultado/<int:analisis_pk>/', views.resultado, name='analisis_resultado'),
    path('historial/<int:proyecto_pk>/', views.historial, name='analisis_historial'),
]