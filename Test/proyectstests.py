# projects/tests.py
import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from projects.models import Project
from analysis_engine.models import Analisis
from users.models import Profile


def crear_usuario(username, password='pass1234seguro', rol='student', superuser=False):
    """Helper: crea usuario con perfil."""
    if superuser:
        user = User.objects.create_superuser(username=username, password=password)
    else:
        user = User.objects.create_user(username=username, password=password)
    if not superuser:
        Profile.objects.create(user=user, role=rol)
    return user


def archivo_py(contenido=b'print("hola")'):
    """Helper: genera un archivo .py en memoria."""
    return SimpleUploadedFile('prueba.py', contenido, content_type='text/plain')


def archivo_txt():
    """Helper: genera un archivo .txt (extensión no permitida)."""
    return SimpleUploadedFile('prueba.txt', b'contenido', content_type='text/plain')


# ─────────────────────────────────────────────────────────────────────────────
# 1. LISTADO DE PROYECTOS
# ─────────────────────────────────────────────────────────────────────────────
class ProjectListTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_usuario('estudiante1')
        self.otro = crear_usuario('estudiante2')
        self.client.login(username='estudiante1', password='pass1234seguro')

        self.proyecto_propio = Project.objects.create(
            user=self.user, name='Mi proyecto', status='analyzed'
        )
        self.proyecto_ajeno = Project.objects.create(
            user=self.otro, name='Proyecto ajeno', status='analyzed'
        )

    def test_lista_solo_proyectos_propios(self):
        """El estudiante solo ve sus propios proyectos en el listado."""
        url = reverse('project_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        nombres = [p.name for p in resp.context['projects']]
        self.assertIn('Mi proyecto', nombres)
        self.assertNotIn('Proyecto ajeno', nombres)

    def test_lista_requiere_login(self):
        """El listado de proyectos redirige si no hay sesión iniciada."""
        self.client.logout()
        url = reverse('project_list')
        resp = self.client.get(url)
        self.assertRedirects(resp, f'/accounts/login/?next={url}')

    def test_busqueda_por_nombre(self):
        """El buscador filtra proyectos por nombre."""
        url = reverse('project_list') + '?q=Mi proyecto'
        resp = self.client.get(url)
        nombres = [p.name for p in resp.context['projects']]
        self.assertIn('Mi proyecto', nombres)

    def test_admin_ve_todos_los_proyectos(self):
        """Un administrador ve todos los proyectos del sistema."""
        admin = crear_usuario('profe', superuser=True)
        self.client.login(username='profe', password='pass1234seguro')
        url = reverse('project_list')
        resp = self.client.get(url)
        nombres = [p.name for p in resp.context['projects']]
        self.assertIn('Mi proyecto', nombres)
        self.assertIn('Proyecto ajeno', nombres)


# ─────────────────────────────────────────────────────────────────────────────
# 2. DETALLE DE PROYECTO
# ─────────────────────────────────────────────────────────────────────────────
class ProjectDetailTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_usuario('estudiante1')
        self.otro = crear_usuario('estudiante2')
        self.client.login(username='estudiante1', password='pass1234seguro')

        self.proyecto = Project.objects.create(
            user=self.user, name='Mi proyecto', status='analyzed'
        )
        self.proyecto_ajeno = Project.objects.create(
            user=self.otro, name='Ajeno', status='analyzed'
        )

    def test_detalle_proyecto_propio_devuelve_200(self):
        """El estudiante puede ver el detalle de su propio proyecto."""
        url = reverse('project_detail', args=[self.proyecto.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_detalle_proyecto_ajeno_devuelve_404(self):
        """El estudiante recibe 404 al intentar ver un proyecto ajeno."""
        url = reverse('project_detail', args=[self.proyecto_ajeno.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


# ─────────────────────────────────────────────────────────────────────────────
# 3. CREACIÓN / SUBIDA DE PROYECTO (RF-4 y RF-5)
# ─────────────────────────────────────────────────────────────────────────────
class ProjectCreateTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_usuario('estudiante1')
        self.client.login(username='estudiante1', password='pass1234seguro')

    def test_get_formulario_devuelve_200(self):
        """GET /proyectos/crear/ devuelve el formulario correctamente."""
        url = reverse('project_create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

    def test_archivo_extension_no_permitida_devuelve_error(self):
        """Subir un .txt debe mostrar error de validación sin crear proyecto."""
        url = reverse('project_create')
        resp = self.client.post(url, {
            'name': 'Proyecto inválido',
            'description': 'Test',
            'archivo': archivo_txt(),
            'nivel': 'BASICO',
        })
        # No debe redirigir: el formulario muestra el error
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Project.objects.filter(name='Proyecto inválido').exists())

    def test_archivo_valido_py_crea_proyecto_y_analisis(self):
        """Subir un .py válido crea el proyecto y su análisis, y redirige al reporte."""
        url = reverse('project_create')
        # Código Python limpio (sin vulnerabilidades)
        codigo = b'def suma(a, b):\n    return a + b\n'
        resp = self.client.post(url, {
            'name': 'Proyecto limpio',
            'description': 'Sin vulnerabilidades',
            'archivo': archivo_py(codigo),
            'nivel': 'BASICO',
        })
        # Debe redirigir al reporte
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Project.objects.filter(name='Proyecto limpio', user=self.user).exists())
        proyecto = Project.objects.get(name='Proyecto limpio', user=self.user)
        self.assertTrue(Analisis.objects.filter(project=proyecto).exists())

    def test_crear_proyecto_requiere_login(self):
        """El formulario de creación redirige si no hay sesión."""
        self.client.logout()
        url = reverse('project_create')
        resp = self.client.get(url)
        self.assertRedirects(resp, f'/accounts/login/?next={url}')


# ─────────────────────────────────────────────────────────────────────────────
# 4. ELIMINACIÓN DE PROYECTO
# ─────────────────────────────────────────────────────────────────────────────
class ProjectDeleteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_usuario('estudiante1')
        self.otro = crear_usuario('estudiante2')
        self.client.login(username='estudiante1', password='pass1234seguro')

        self.proyecto = Project.objects.create(
            user=self.user, name='A eliminar', status='analyzed'
        )
        self.proyecto_ajeno = Project.objects.create(
            user=self.otro, name='No tocar', status='analyzed'
        )

    def test_eliminar_proyecto_propio(self):
        """POST a project_delete elimina el proyecto propio y redirige."""
        pk = self.proyecto.pk
        url = reverse('project_delete', args=[pk])
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('project_list'))
        self.assertFalse(Project.objects.filter(pk=pk).exists())

    def test_eliminar_proyecto_ajeno_devuelve_404(self):
        """POST a project_delete sobre un proyecto ajeno devuelve 404."""
        url = reverse('project_delete', args=[self.proyecto_ajeno.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Project.objects.filter(pk=self.proyecto_ajeno.pk).exists())