# api/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from projects.models import Project
from analysis_engine.models import Analisis
from users.models import Profile


def crear_usuario(username, password='pass1234seguro', rol='student'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role=rol)
    return user


def get_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


class APITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {get_token(self.user)}')

        self.proyecto = Project.objects.create(
            user=self.user, name='Proyecto Test', status='analyzed'
        )
        self.analisis = Analisis.objects.create(
            project=self.proyecto, score=80, nivel='BASICO'
        )

    # -- Token ------------------------------------------------------------------

    def test_obtener_token(self):
        """POST /api/token/ con credenciales validas devuelve un token."""
        cliente = APIClient()
        resp = cliente.post(reverse('api_token'), {
            'username': 'est1',
            'password': 'pass1234seguro',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp.data)

    def test_sin_token_devuelve_401(self):
        """Acceder a la API sin token devuelve 401."""
        cliente = APIClient()
        resp = cliente.get(reverse('api_proyecto_list'))
        self.assertEqual(resp.status_code, 401)

    # -- Resumen ----------------------------------------------------------------

    def test_get_resumen(self):
        """GET /api/resumen/ devuelve los datos del usuario autenticado."""
        resp = self.client.get(reverse('api_resumen'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['usuario'], 'est1')

    # -- Proyectos CRUD ---------------------------------------------------------

    def test_get_proyectos(self):
        """GET /api/proyectos/ devuelve la lista de proyectos del usuario."""
        resp = self.client.get(reverse('api_proyecto_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_post_proyecto(self):
        """POST /api/proyectos/ crea un nuevo proyecto."""
        resp = self.client.post(reverse('api_proyecto_list'), {
            'name': 'Proyecto nuevo',
            'description': 'Creado via API',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Project.objects.filter(name='Proyecto nuevo', user=self.user).exists())

    def test_get_proyecto_detalle(self):
        """GET /api/proyectos/<pk>/ devuelve el detalle del proyecto."""
        resp = self.client.get(reverse('api_proyecto_detail', args=[self.proyecto.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['proyecto']['name'], 'Proyecto Test')

    def test_put_proyecto(self):
        """PUT /api/proyectos/<pk>/ actualiza nombre y descripcion."""
        resp = self.client.put(
            reverse('api_proyecto_detail', args=[self.proyecto.pk]),
            {'name': 'Nombre actualizado', 'description': 'Nueva descripcion'},
        )
        self.assertEqual(resp.status_code, 200)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.name, 'Nombre actualizado')

    def test_patch_proyecto(self):
        """PATCH /api/proyectos/<pk>/ actualiza solo el nombre."""
        resp = self.client.patch(
            reverse('api_proyecto_detail', args=[self.proyecto.pk]),
            {'name': 'Solo nombre'},
        )
        self.assertEqual(resp.status_code, 200)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.name, 'Solo nombre')

    def test_delete_proyecto(self):
        """DELETE /api/proyectos/<pk>/ elimina el proyecto."""
        pk = self.proyecto.pk
        resp = self.client.delete(reverse('api_proyecto_detail', args=[pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Project.objects.filter(pk=pk).exists())

    # -- Analisis CRUD ----------------------------------------------------------

    def test_get_analisis(self):
        """GET /api/analisis/ devuelve la lista de analisis del usuario."""
        resp = self.client.get(reverse('api_analisis_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_get_analisis_detalle(self):
        """GET /api/analisis/<pk>/ devuelve el detalle con vulnerabilidades."""
        resp = self.client.get(reverse('api_analisis_detail', args=[self.analisis.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['score'], 80)
        self.assertIn('vulnerabilidades', resp.data)

    def test_delete_analisis(self):
        """DELETE /api/analisis/<pk>/ elimina el analisis."""
        pk = self.analisis.pk
        resp = self.client.delete(reverse('api_analisis_detail', args=[pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Analisis.objects.filter(pk=pk).exists())