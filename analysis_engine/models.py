from django.db import models
from projects.models import Project


class Analisis(models.Model):
    NIVEL_CHOICES = (
        ('BASICO', 'Básico'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='analisis')
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='BASICO')
    score = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Análisis'
        verbose_name_plural = 'Análisis'

    def __str__(self):
        return f"Análisis #{self.pk} - {self.project.name} (Score: {self.score})"


class Vulnerabilidad(models.Model):
    SEVERIDAD_CHOICES = (
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    )

    analisis = models.ForeignKey(Analisis, on_delete=models.CASCADE, related_name='vulnerabilidades')
    regla_id = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    severidad = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES)
    descripcion = models.TextField()
    recomendacion = models.TextField()
    archivo = models.CharField(max_length=300)
    linea = models.IntegerField()
    codigo_linea = models.TextField(blank=True)

    class Meta:
        ordering = ['severidad', 'archivo', 'linea']
        verbose_name = 'Vulnerabilidad'
        verbose_name_plural = 'Vulnerabilidades'

    def get_severidad_color(self):
        colores = {
            'BAJA': 'secondary',
            'MEDIA': 'warning',
            'ALTA': 'danger',
            'CRITICA': 'dark',
        }
        return colores.get(self.severidad, 'secondary')

    def __str__(self):
        return f"{self.nombre} en {self.archivo}:{self.linea}"
