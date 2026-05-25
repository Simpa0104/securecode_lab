# users/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile


def crear_estudiante(username='est1', password='pass1234seguro', clase='clase-1'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role='student', numero_clase=clase)
    return user


def crear_monitor(username='mon1', password='pass1234seguro', clase='clase-1'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role='monitor', numero_clase=clase)
    return user


def crear_admin(username='admin1', password='pass1234seguro'):
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, role='admin')
    return user


# ─────────────────────────────────────────────────────────────────────────────
# 1. REGISTRO
# ─────────────────────────────────────────────────────────────────────────────
class RegistroTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_get_formulario_registro_devuelve_200(self):
        """GET /register/ devuelve el formulario de registro."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_registro_exitoso_redirige_al_login(self):
        """POST con datos válidos crea el usuario y redirige al login."""
        resp = self.client.post(self.url, {
            'username': 'nuevo_usuario',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@test.com',
            'password1': 'ClaveSegura123',
            'password2': 'ClaveSegura123',
            'grupo': 'student',
            'numero_clase': 'clase-1',
        })
        self.assertRedirects(resp, reverse('login'))
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())

    def test_registro_contrasena_corta_muestra_error(self):
        """POST con contraseña < 8 caracteres no crea el usuario."""
        resp = self.client.post(self.url, {
            'username': 'usuario2',
            'first_name': 'Ana',
            'last_name': 'López',
            'email': 'ana@test.com',
            'password1': '123',
            'password2': '123',
            'grupo': 'student',
            'numero_clase': 'clase-1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='usuario2').exists())

    def test_registro_contrasenas_distintas_muestra_error(self):
        """POST con contraseñas que no coinciden no crea el usuario."""
        resp = self.client.post(self.url, {
            'username': 'usuario3',
            'first_name': 'Carlos',
            'last_name': 'García',
            'email': 'carlos@test.com',
            'password1': 'ClaveSegura123',
            'password2': 'ClaveDistinta456',
            'grupo': 'student',
            'numero_clase': 'clase-1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='usuario3').exists())

    def test_registro_username_duplicado_muestra_error(self):
        """POST con username ya existente no crea el usuario."""
        crear_estudiante(username='duplicado')
        resp = self.client.post(self.url, {
            'username': 'duplicado',
            'first_name': 'X',
            'last_name': 'Y',
            'email': 'x@test.com',
            'password1': 'ClaveSegura123',
            'password2': 'ClaveSegura123',
            'grupo': 'student',
            'numero_clase': 'clase-1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.filter(username='duplicado').count(), 1)


# ─────────────────────────────────────────────────────────────────────────────
# 2. AUTENTICACIÓN (RF-2)
# ─────────────────────────────────────────────────────────────────────────────
class AutenticacionTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_estudiante(username='est1')

    def test_login_contrasena_incorrecta_no_autentica(self):
        """Login con contraseña incorrecta muestra el formulario con error."""
        resp = self.client.post(reverse('login'), {
            'username': 'est1',
            'password': 'contraseña_mala',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_login_no_revela_campo_incorrecto(self):
        """El mensaje de error no indica si fue el usuario o la contraseña."""
        resp = self.client.post(reverse('login'), {
            'username': 'est1',
            'password': 'mala',
        })
        contenido = resp.content.decode()
        # No debe decir "contraseña incorrecta" ni "usuario incorrecto" por separado
        self.assertNotIn('usuario incorrecto', contenido.lower())
        self.assertNotIn('contraseña incorrecta', contenido.lower())

    def test_logout_cierra_sesion(self):
        """Después del logout el usuario no está autenticado."""
        self.client.login(username='est1', password='pass1234seguro')
        self.client.post(reverse('logout'))
        resp = self.client.get(reverse('project_list'))
        self.assertFalse(resp.wsgi_request.user.is_authenticated)


# ─────────────────────────────────────────────────────────────────────────────
# 3. CONTROL DE ACCESO POR ROL (RF-3)
# ─────────────────────────────────────────────────────────────────────────────
class ControlAccesoTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.estudiante = crear_estudiante(username='est1')
        self.monitor = crear_monitor(username='mon1')
        self.admin = crear_admin(username='adm1')

    def test_estudiante_redirige_a_su_dashboard(self):
        """El estudiante al hacer login llega a dashboard_estudiante."""
        self.client.login(username='est1', password='pass1234seguro')
        resp = self.client.get(reverse('home'), follow=True)
        self.assertTemplateUsed(resp, 'users/dashboard_estudiante.html')

    def test_monitor_redirige_a_su_dashboard(self):
        """El monitor al hacer login llega a dashboard_monitor."""
        self.client.login(username='mon1', password='pass1234seguro')
        resp = self.client.get(reverse('home'), follow=True)
        self.assertTemplateUsed(resp, 'users/dashboard_monitor.html')

    def test_admin_redirige_a_su_dashboard(self):
        """El admin al hacer login llega a dashboard_admin."""
        self.client.login(username='adm1', password='pass1234seguro')
        resp = self.client.get(reverse('home'), follow=True)
        self.assertTemplateUsed(resp, 'users/dashboard_admin.html')

    def test_estudiante_no_puede_acceder_a_dashboard_admin(self):
        """Un estudiante que accede a /dashboard/admin/ es redirigido a su propio panel."""
        self.client.login(username='est1', password='pass1234seguro')
        resp = self.client.get(reverse('dashboard_admin'), follow=True)
        # No debe ver el template de admin
        self.assertTemplateNotUsed(resp, 'users/dashboard_admin.html')

    def test_monitor_no_puede_acceder_a_dashboard_admin(self):
        """Un monitor que accede a /dashboard/admin/ es redirigido a su propio panel."""
        self.client.login(username='mon1', password='pass1234seguro')
        resp = self.client.get(reverse('dashboard_admin'), follow=True)
        self.assertTemplateNotUsed(resp, 'users/dashboard_admin.html')

    def test_ruta_protegida_sin_sesion_redirige_al_login(self):
        """Acceder a un dashboard sin sesión redirige al login."""
        resp = self.client.get(reverse('dashboard_estudiante'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])


# ─────────────────────────────────────────────────────────────────────────────
# 4. GESTIÓN DE USUARIOS — solo admin (RF-11)
# ─────────────────────────────────────────────────────────────────────────────
class GestionUsuariosTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = crear_admin(username='adm1')
        self.estudiante = crear_estudiante(username='est1')
        self.client.login(username='adm1', password='pass1234seguro')

    def test_admin_puede_ver_gestion_usuarios(self):
        """El admin accede a la página de gestión de usuarios."""
        resp = self.client.get(reverse('gestion_usuarios'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_puede_editar_usuario(self):
        """El admin puede cambiar el rol de un usuario existente."""
        url = reverse('editar_usuario_modal', args=[self.estudiante.pk])
        resp = self.client.post(url, {
            'username': 'est1',
            'email': 'est1@test.com',
            'role': 'monitor',
            'numero_clase': 'clase-1',
            'is_active': 'on',
        })
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.estudiante.profile.refresh_from_db()
        self.assertEqual(self.estudiante.profile.role, 'monitor')

    def test_admin_puede_eliminar_usuario(self):
        """El admin puede eliminar un usuario desde la vista de eliminación."""
        pk = self.estudiante.pk
        url = reverse('eliminar_usuario', args=[pk])
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('gestion_usuarios'))
        self.assertFalse(User.objects.filter(pk=pk).exists())

    def test_admin_no_puede_eliminarse_a_si_mismo(self):
        """El admin no puede eliminar su propia cuenta."""
        url = reverse('eliminar_usuario', args=[self.admin.pk])
        resp = self.client.post(url)
        # Debe redirigir con mensaje de error, no eliminar
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())


# ─────────────────────────────────────────────────────────────────────────────
# 5. PERFIL DE USUARIO
# ─────────────────────────────────────────────────────────────────────────────
class PerfilTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = crear_estudiante(username='est1')
        self.user.first_name = 'Juan'
        self.user.last_name = 'Pérez'
        self.user.save()
        self.client.login(username='est1', password='pass1234seguro')

    def test_ver_perfil_devuelve_200(self):
        """GET /perfil/ devuelve 200."""
        resp = self.client.get(reverse('perfil'))
        self.assertEqual(resp.status_code, 200)

    def test_actualizar_datos_personales(self):
        """POST accion=datos actualiza nombre y correo."""
        resp = self.client.post(reverse('perfil'), {
            'accion': 'datos',
            'first_name': 'Carlos',
            'last_name': 'Gómez',
            'email': 'carlos@test.com',
        })
        self.assertRedirects(resp, reverse('perfil'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Carlos')
        self.assertEqual(self.user.email, 'carlos@test.com')

    def test_cambiar_contrasena_correctamente(self):
        """POST accion=contraseña actualiza la contraseña si los datos son válidos."""
        resp = self.client.post(reverse('perfil'), {
            'accion': 'contraseña',
            'contraseña_actual': 'pass1234seguro',
            'contraseña_nueva': 'NuevaClave5678',
            'contraseña_confirmar': 'NuevaClave5678',
        })
        self.assertRedirects(resp, reverse('perfil'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NuevaClave5678'))

    def test_cambiar_contrasena_actual_incorrecta(self):
        """POST accion=contraseña con clave actual incorrecta no cambia la contraseña."""
        self.client.post(reverse('perfil'), {
            'accion': 'contraseña',
            'contraseña_actual': 'incorrecta',
            'contraseña_nueva': 'NuevaClave5678',
            'contraseña_confirmar': 'NuevaClave5678',
        })
        self.user.refresh_from_db()
        # La contraseña original debe mantenerse
        self.assertTrue(self.user.check_password('pass1234seguro'))

    def test_cambiar_contrasena_nueva_muy_corta(self):
        """POST accion=contraseña con nueva contraseña < 8 caracteres no actualiza."""
        self.client.post(reverse('perfil'), {
            'accion': 'contraseña',
            'contraseña_actual': 'pass1234seguro',
            'contraseña_nueva': '123',
            'contraseña_confirmar': '123',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('pass1234seguro'))