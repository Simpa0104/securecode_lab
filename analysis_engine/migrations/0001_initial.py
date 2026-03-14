from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analisis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.CharField(
                    choices=[('BASICO', 'Básico'), ('INTERMEDIO', 'Intermedio'), ('AVANZADO', 'Avanzado')],
                    default='BASICO',
                    max_length=20
                )),
                ('score', models.IntegerField(default=0)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='analisis',
                    to='projects.project'
                )),
            ],
            options={
                'verbose_name': 'Análisis',
                'verbose_name_plural': 'Análisis',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Vulnerabilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regla_id', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=200)),
                ('severidad', models.CharField(
                    choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('CRITICA', 'Crítica')],
                    max_length=10
                )),
                ('descripcion', models.TextField()),
                ('recomendacion', models.TextField()),
                ('archivo', models.CharField(max_length=300)),
                ('linea', models.IntegerField()),
                ('codigo_linea', models.TextField(blank=True)),
                ('analisis', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='vulnerabilidades',
                    to='analysis_engine.analisis'
                )),
            ],
            options={
                'verbose_name': 'Vulnerabilidad',
                'verbose_name_plural': 'Vulnerabilidades',
                'ordering': ['severidad', 'archivo', 'linea'],
            },
        ),
    ]