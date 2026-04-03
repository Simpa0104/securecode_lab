#/users/migrations/0002_profile_numero_clase_monitor.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='numero_clase',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Sin clase asignada'),
                    ('clase-1', 'Clase 1'),
                    ('clase-2', 'Clase 2'),
                    ('clase-3', 'Clase 3'),
                    ('clase-4', 'Clase 4'),
                    ('clase-5', 'Clase 5'),
                ],
                default='',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(
                choices=[
                    ('student', 'Estudiante'),
                    ('monitor', 'Monitor'),
                    ('admin', 'Profesor / Administrador'),
                ],
                default='student',
                max_length=20,
            ),
        ),
    ]