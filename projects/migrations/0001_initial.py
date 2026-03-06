from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre del proyecto')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('file', models.FileField(upload_to='projects/', verbose_name='Archivo del proyecto')),
                ('status', models.CharField(
                    choices=[('pending', 'Pendiente'), ('analyzed', 'Analizado'), ('error', 'Error')],
                    default='pending',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='projects',
                    to='auth.user'
                )),
            ],
            options={
                'verbose_name': 'Proyecto',
                'verbose_name_plural': 'Proyectos',
                'ordering': ['-created_at'],
            },
        ),
    ]