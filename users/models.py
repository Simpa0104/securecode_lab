# users/models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


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


# Mapeo de roles a nombres de grupo
ROLE_GROUP_MAP = {
    'student': 'Estudiante',
    'monitor': 'Monitor',
    'admin': 'Profesor',
}


@receiver(post_save, sender=Profile)
def sincronizar_grupo(sender, instance, **kwargs):
    """
    Cada vez que se guarda un Profile, sincroniza el grupo de Django
    correspondiente al rol del usuario.
    """
    usuario = instance.user
    nombre_grupo = ROLE_GROUP_MAP.get(instance.role)

    if not nombre_grupo:
        return

    try:
        grupo_nuevo = Group.objects.get(name=nombre_grupo)
    except Group.DoesNotExist:
        # Si el grupo no existe en la BD, no hace nada
        return

    # Quitar todos los grupos actuales y asignar solo el nuevo
    usuario.groups.clear()
    usuario.groups.add(grupo_nuevo)