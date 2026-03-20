from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('analyzed', 'Analizado'),
        ('error', 'Error'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200, verbose_name='Nombre del proyecto')
    description = models.TextField(blank=True, verbose_name='Descripción')
    file = models.FileField(upload_to='projects/', verbose_name='Archivo del proyecto')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def get_file_extension(self):
        import os
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    def get_file_size_kb(self):
        try:
            return round(self.file.size / 1024, 2)
        except Exception:
            return 0
