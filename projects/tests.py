# projects/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from projects.models import Project
from analysis_engine.models import Analisis
from users.models import Profile


def crear_usuario(username, password='pass1234seguro', rol='student'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role=rol)
    return user


def archivo_py(contenido=b'def suma(a, b):\n    return a + b\n'):
    return SimpleUploadedFile('prueba.py', contenido, content_type='text/plain')


def archivo_txt():
    return SimpleUploadedFile('prueba.txt', b'contenido', content_type='text/plain')


class ProyectosTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_usuario('est1')
        self.otro = crear_usuario('est2')
        self.client.login(username='est1', password='pass1234seguro')

        self.proyecto = Project.objects.create(
            user=self.user, name='Mi proyecto', status='analyzed'
        )
        self.proyecto_ajeno = Project.objects.create(
            user=self.otro, name='Proyecto ajeno', status='analyzed'
        )

    # -- Listar (RF-9) ----------------------------------------------------------

    def test_lista_solo_proyectos_propios(self):
        """El estudiante solo ve sus propios proyectos."""
        resp = self.client.get(reverse('project_list'))
        self.assertEqual(resp.status_code, 200)
        nombres = [p.name for p in resp.context['projects']]
        self.assertIn('Mi proyecto', nombres)
        self.assertNotIn('Proyecto ajeno', nombres)

    def test_lista_requiere_login(self):
        """El listado redirige si no hay sesion."""
        self.client.logout()
        resp = self.client.get(reverse('project_list'))
        self.assertEqual(resp.status_code, 302)

    # -- Crear (RF-4 y RF-5) ----------------------------------------------------

    def test_crear_proyecto_archivo_valido(self):
        """Subir un .py valido crea el proyecto y redirige al reporte."""
        resp = self.client.post(reverse('project_create'), {
            'name': 'Proyecto limpio',
            'description': 'Sin vulnerabilidades',
            'archivo': archivo_py(),
            'nivel': 'BASICO',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Project.objects.filter(name='Proyecto limpio', user=self.user).exists())

    def test_crear_proyecto_extension_no_permitida(self):
        """Subir un .txt no crea el proyecto."""
        self.client.post(reverse('project_create'), {
            'name': 'Proyecto invalido',
            'description': '',
            'archivo': archivo_txt(),
            'nivel': 'BASICO',
        })
        self.assertFalse(Project.objects.filter(name='Proyecto invalido').exists())

    # -- Ver detalle (RF-9) -----------------------------------------------------

    def test_ver_detalle_proyecto_propio(self):
        """El estudiante puede ver el detalle de su proyecto."""
        resp = self.client.get(reverse('project_detail', args=[self.proyecto.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_ver_detalle_proyecto_ajeno_devuelve_404(self):
        """El estudiante recibe 404 al intentar ver un proyecto ajeno."""
        resp = self.client.get(reverse('project_detail', args=[self.proyecto_ajeno.pk]))
        self.assertEqual(resp.status_code, 404)

    # -- Eliminar ---------------------------------------------------------------

    def test_eliminar_proyecto_propio(self):
        """POST a project_delete elimina el proyecto propio."""
        pk = self.proyecto.pk
        self.client.post(reverse('project_delete', args=[pk]))
        self.assertFalse(Project.objects.filter(pk=pk).exists())

    def test_eliminar_proyecto_ajeno_devuelve_404(self):
        """POST a project_delete sobre un proyecto ajeno devuelve 404."""
        resp = self.client.post(reverse('project_delete', args=[self.proyecto_ajeno.pk]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Project.objects.filter(pk=self.proyecto_ajeno.pk).exists())