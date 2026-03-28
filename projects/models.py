from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):

    STATUS_CHOICES = (
        ('analyzed', 'Analizado'),
        ('error', 'Error'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200, verbose_name='Nombre del proyecto')
    description = models.TextField(blank=True, verbose_name='Descripcion')
    filename = models.CharField(max_length=300, blank=True, verbose_name='Nombre del archivo')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='analyzed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return f"{self.name} - {self.user.username}"