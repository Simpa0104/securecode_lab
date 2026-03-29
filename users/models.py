# users/models.py
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Estudiante'),
        ('monitor', 'Monitor'),
        ('admin', 'Profesor / Administrador'),
    )

    CLASE_CHOICES = (
        ('', 'Sin clase asignada'),
        ('clase-1', 'Clase 1'),
        ('clase-2', 'Clase 2'),
        ('clase-3', 'Clase 3'),
        ('clase-4', 'Clase 4'),
        ('clase-5', 'Clase 5'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    numero_clase = models.CharField(
        max_length=20,
        choices=CLASE_CHOICES,
        blank=True,
        default=''
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"