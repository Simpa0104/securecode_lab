# users/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile


def crear_estudiante(username='est1', password='pass1234seguro'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role='student', numero_clase='clase-1')
    return user


def crear_admin(username='adm1', password='pass1234seguro'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role='admin')
    return user


class UsuariosTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = crear_admin()
        self.estudiante = crear_estudiante()

    # -- Registro (RF-1) --------------------------------------------------------

    def test_registro_exitoso(self):
        """POST /register/ con datos validos crea el usuario y redirige al login."""
        resp = self.client.post(reverse('register'), {
            'username': 'nuevo',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'email': 'juan@test.com',
            'password1': 'ClaveSegura123',
            'password2': 'ClaveSegura123',
            'grupo': 'student',
            'numero_clase': 'clase-1',
        })
        self.assertRedirects(resp, reverse('login'))
        self.assertTrue(User.objects.filter(username='nuevo').exists())

    def test_registro_contrasena_invalida_no_crea_usuario(self):
        """POST /register/ con contrasena corta no crea el usuario."""
        self.client.post(reverse('register'), {
            'username': 'usuario2',
            'first_name': 'Ana',
            'last_name': 'Lopez',
            'email': 'ana@test.com',
            'password1': '123',
            'password2': '123',
            'grupo': 'student',
            'numero_clase': 'clase-1',
        })
        self.assertFalse(User.objects.filter(username='usuario2').exists())

    # -- Autenticacion (RF-2) ---------------------------------------------------

    def test_login_credenciales_validas(self):
        """Login con credenciales correctas redirige al home."""
        resp = self.client.post(reverse('login'), {
            'username': 'est1',
            'password': 'pass1234seguro',
        })
        self.assertRedirects(resp, reverse('home'))

    def test_login_credenciales_invalidas(self):
        """Login con contrasena incorrecta no autentica al usuario."""
        resp = self.client.post(reverse('login'), {
            'username': 'est1',
            'password': 'mala',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    # -- Control de acceso por rol (RF-3) ---------------------------------------

    def test_estudiante_no_accede_a_dashboard_admin(self):
        """Un estudiante que accede a /dashboard/admin/ no ve ese template."""
        self.client.login(username='est1', password='pass1234seguro')
        resp = self.client.get(reverse('dashboard_admin'), follow=True)
        self.assertTemplateNotUsed(resp, 'users/dashboard_admin.html')

    def test_ruta_protegida_sin_sesion_redirige_al_login(self):
        """Acceder a proyectos sin sesion redirige al login."""
        resp = self.client.get(reverse('project_list'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])

    # -- Gestion de usuarios (RF-11) --------------------------------------------

    def test_admin_puede_ver_gestion_usuarios(self):
        """El admin accede correctamente a la gestion de usuarios."""
        self.client.login(username='adm1', password='pass1234seguro')
        resp = self.client.get(reverse('gestion_usuarios'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_puede_editar_usuario(self):
        """El admin puede cambiar el rol de un usuario via modal."""
        self.client.login(username='adm1', password='pass1234seguro')
        url = reverse('editar_usuario_modal', args=[self.estudiante.pk])
        resp = self.client.post(url, {
            'username': 'est1',
            'email': 'est1@test.com',
            'role': 'monitor',
            'numero_clase': 'clase-1',
            'is_active': 'on',
        })
        self.assertTrue(resp.json().get('ok'))
        self.estudiante.profile.refresh_from_db()
        self.assertEqual(self.estudiante.profile.role, 'monitor')

    def test_admin_puede_eliminar_usuario(self):
        """El admin puede eliminar un usuario."""
        self.client.login(username='adm1', password='pass1234seguro')
        pk = self.estudiante.pk
        self.client.post(reverse('eliminar_usuario', args=[pk]))
        self.assertFalse(User.objects.filter(pk=pk).exists())