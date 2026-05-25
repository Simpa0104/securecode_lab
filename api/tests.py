# api/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from projects.models import Project
from analysis_engine.models import Analisis
from users.models import Profile


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def crear_usuario(username, password='pass1234seguro', rol='student'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role=rol)
    return user


def crear_proyecto(user, nombre='Proyecto Test', status='analyzed'):
    return Project.objects.create(user=user, name=nombre, status=status)


def crear_analisis(proyecto, score=80, nivel='BASICO'):
    return Analisis.objects.create(project=proyecto, score=score, nivel=nivel)


# ─────────────────────────────────────────────────────────────────────────────
# 1. AUTENTICACIÓN POR TOKEN
# ─────────────────────────────────────────────────────────────────────────────
class TokenAutenticacionTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        self.url_token = reverse('api_token')

    def test_obtener_token_con_credenciales_validas(self):
        """POST /api/token/ con credenciales válidas devuelve un token."""
        resp = self.client.post(self.url_token, {
            'username': 'est1',
            'password': 'pass1234seguro',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp.data)
        self.assertTrue(len(resp.data['token']) > 0)

    def test_obtener_token_con_credenciales_invalidas(self):
        """POST /api/token/ con credenciales incorrectas devuelve 400."""
        resp = self.client.post(self.url_token, {
            'username': 'est1',
            'password': 'contraseña_mala',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn('token', resp.data)

    def test_endpoint_sin_token_devuelve_401(self):
        """GET /api/proyectos/ sin token de autenticación devuelve 401."""
        resp = self.client.get(reverse('api_proyecto_list'))
        self.assertEqual(resp.status_code, 401)

    def test_endpoint_con_token_invalido_devuelve_401(self):
        """GET /api/proyectos/ con token falso devuelve 401."""
        self.client.credentials(HTTP_AUTHORIZATION='Token tokenfalso123')
        resp = self.client.get(reverse('api_proyecto_list'))
        self.assertEqual(resp.status_code, 401)

    def test_endpoint_con_token_valido_devuelve_200(self):
        """GET /api/proyectos/ con token válido devuelve 200."""
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.get(reverse('api_proyecto_list'))
        self.assertEqual(resp.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# 2. RESUMEN
# ─────────────────────────────────────────────────────────────────────────────
class ResumenTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        self.proyecto = crear_proyecto(self.user)
        crear_analisis(self.proyecto, score=75)
        crear_analisis(self.proyecto, score=90)

    def test_resumen_devuelve_datos_correctos(self):
        """GET /api/resumen/ devuelve username, totales y mejor score."""
        resp = self.client.get(reverse('api_resumen'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['usuario'], 'est1')
        self.assertEqual(resp.data['total_proyectos'], 1)
        self.assertEqual(resp.data['total_analisis'], 2)
        self.assertEqual(resp.data['mejor_score'], 90)

    def test_resumen_sin_analisis_devuelve_na(self):
        """GET /api/resumen/ sin análisis devuelve mejor_score N/A."""
        # Nuevo usuario sin nada
        otro = crear_usuario('est2')
        token, _ = Token.objects.get_or_create(user=otro)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.get(reverse('api_resumen'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['mejor_score'], 'N/A')
        self.assertEqual(resp.data['total_proyectos'], 0)


# ─────────────────────────────────────────────────────────────────────────────
# 3. PROYECTOS — GET (lectura)
# ─────────────────────────────────────────────────────────────────────────────
class ProyectoListGetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        self.otro = crear_usuario('est2')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        self.proyecto = crear_proyecto(self.user, 'Proyecto A')
        crear_proyecto(self.otro, 'Proyecto ajeno')

    def test_get_lista_solo_proyectos_propios(self):
        """GET /api/proyectos/ devuelve solo los proyectos del usuario autenticado."""
        resp = self.client.get(reverse('api_proyecto_list'))
        self.assertEqual(resp.status_code, 200)
        nombres = [p['name'] for p in resp.data['proyectos']]
        self.assertIn('Proyecto A', nombres)
        self.assertNotIn('Proyecto ajeno', nombres)
        self.assertEqual(resp.data['count'], 1)

    def test_get_detalle_proyecto_propio(self):
        """GET /api/proyectos/<pk>/ devuelve el proyecto y su historial."""
        resp = self.client.get(reverse('api_proyecto_detail', args=[self.proyecto.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['proyecto']['name'], 'Proyecto A')
        self.assertIn('historial', resp.data)

    def test_get_detalle_proyecto_ajeno_devuelve_404(self):
        """GET /api/proyectos/<pk>/ de un proyecto ajeno devuelve 404."""
        proyecto_ajeno = Project.objects.get(name='Proyecto ajeno')
        resp = self.client.get(reverse('api_proyecto_detail', args=[proyecto_ajeno.pk]))
        self.assertEqual(resp.status_code, 404)


# ─────────────────────────────────────────────────────────────────────────────
# 4. PROYECTOS — POST (creación)
# ─────────────────────────────────────────────────────────────────────────────
class ProyectoPostTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_post_crea_proyecto_con_datos_validos(self):
        """POST /api/proyectos/ con datos válidos crea el proyecto."""
        resp = self.client.post(reverse('api_proyecto_list'), {
            'name': 'Nuevo proyecto API',
            'description': 'Creado desde la API',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Project.objects.filter(
            name='Nuevo proyecto API', user=self.user
        ).exists())

    def test_post_proyecto_sin_nombre_devuelve_400(self):
        """POST /api/proyectos/ sin nombre devuelve 400."""
        resp = self.client.post(reverse('api_proyecto_list'), {
            'name': '',
            'description': 'Sin nombre',
        })
        self.assertEqual(resp.status_code, 400)

    def test_post_proyecto_asigna_status_pending(self):
        """POST /api/proyectos/ crea el proyecto en estado 'pending'."""
        self.client.post(reverse('api_proyecto_list'), {
            'name': 'Proyecto pendiente',
            'description': '',
        })
        proyecto = Project.objects.get(name='Proyecto pendiente')
        self.assertEqual(proyecto.status, 'pending')

    def test_post_proyecto_sin_descripcion_es_valido(self):
        """POST /api/proyectos/ sin descripción es válido."""
        resp = self.client.post(reverse('api_proyecto_list'), {
            'name': 'Solo nombre',
        })
        self.assertEqual(resp.status_code, 201)


# ─────────────────────────────────────────────────────────────────────────────
# 5. PROYECTOS — PUT (actualización completa)
# ─────────────────────────────────────────────────────────────────────────────
class ProyectoPutTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        self.otro = crear_usuario('est2')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.proyecto = crear_proyecto(self.user, 'Original')
        self.proyecto_ajeno = crear_proyecto(self.otro, 'Ajeno')

    def test_put_actualiza_nombre_y_descripcion(self):
        """PUT /api/proyectos/<pk>/ actualiza nombre y descripción."""
        resp = self.client.put(
            reverse('api_proyecto_detail', args=[self.proyecto.pk]),
            {'name': 'Nombre nuevo', 'description': 'Desc nueva'},
        )
        self.assertEqual(resp.status_code, 200)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.name, 'Nombre nuevo')
        self.assertEqual(self.proyecto.description, 'Desc nueva')

    def test_put_sin_nombre_devuelve_400(self):
        """PUT /api/proyectos/<pk>/ sin nombre devuelve 400."""
        resp = self.client.put(
            reverse('api_proyecto_detail', args=[self.proyecto.pk]),
            {'name': '', 'description': 'Desc'},
        )
        self.assertEqual(resp.status_code, 400)

    def test_put_proyecto_ajeno_devuelve_404(self):
        """PUT sobre proyecto ajeno devuelve 404."""
        resp = self.client.put(
            reverse('api_proyecto_detail', args=[self.proyecto_ajeno.pk]),
            {'name': 'Hack', 'description': ''},
        )
        self.assertEqual(resp.status_code, 404)


# ─────────────────────────────────────────────────────────────────────────────
# 6. PROYECTOS — PATCH (actualización parcial)
# ─────────────────────────────────────────────────────────────────────────────
class ProyectoPatchTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.proyecto = crear_proyecto(self.user, 'Original')
        self.proyecto.description = 'Descripción original'
        self.proyecto.save()

    def test_patch_actualiza_solo_nombre(self):
        """PATCH /api/proyectos/<pk>/ con solo nombre actualiza el nombre."""
        resp = self.client.patch(
            reverse('api_proyecto_detail', args=[self.proyecto.pk]),
            {'name': 'Solo nombre cambiado'},
        )
        self.assertEqual(resp.status_code, 200)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.name, 'Solo nombre cambiado')
        # La descripción no debe cambiar
        self.assertEqual(self.proyecto.description, 'Descripción original')

    def test_patch_actualiza_solo_descripcion(self):
        """PATCH /api/proyectos/<pk>/ con solo descripción actualiza la descripción."""
        resp = self.client.patch(
            reverse('api_proyecto_detail', args=[self.proyecto.pk]),
            {'description': 'Nueva descripción'},
        )
        self.assertEqual(resp.status_code, 200)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.description, 'Nueva descripción')
        # El nombre no debe cambiar
        self.assertEqual(self.proyecto.name, 'Original')


# ─────────────────────────────────────────────────────────────────────────────
# 7. PROYECTOS — DELETE
# ─────────────────────────────────────────────────────────────────────────────
class ProyectoDeleteTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = crear_usuario('est1')
        self.otro = crear_usuario('est2')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.proyecto = crear_proyecto(self.user, 'A eliminar')
        self.proyecto_ajeno = crear_proyecto(self.otro, 'Intocable')

    def test_delete_elimina_proyecto_propio(self):
        """DELETE /api/proyectos/<pk>/ elimina el proyecto del usuario."""
        pk = self.proyecto.pk
        resp = self.client.delete(reverse('api_proyecto_detail', args=[pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Project.objects.filter(pk=pk).exists())

    def test_delete_proyecto_ajeno_devuelve_404(self):
        """DELETE sobre proyecto ajeno devuelve 404 y no lo elimina."""
        pk = self.proyecto_ajeno.pk
        resp = self.client.delete(reverse('api_proyecto_detail', args=[pk]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Project.objects.filter(pk=pk).exists())

    def test_delete_elimina_analisis_asociados(self):
        """DELETE de un proyecto también elimina sus análisis."""
        analisis = crear_analisis(self.proyecto)
        pk_proyecto = self.proyecto.pk
        pk_analisis = analisis.pk
        self.client.delete(reverse('api_proyecto_detail', args=[pk_proyecto]))
        self.assertFalse(Analisis.objects.filter(pk=pk_analisis).exists())