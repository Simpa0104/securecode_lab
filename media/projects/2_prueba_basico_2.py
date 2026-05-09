# Configuracion insegura de Django con XSS y CSRF desactivado
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

ALLOWED_HOSTS = []

# Credenciales hardcodeadas en el codigo
api_key = 'sk-prod-9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1'
database_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secreto'

@csrf_exempt
def comentarios(request):
    comentario = request.POST.get('comentario', '')
    # Vulnerabilidad XSS - renderizando contenido sin escapar
    contenido = mark_safe('<div>' + comentario + '</div>')
    return contenido

def mostrar_perfil(request):
    nombre = request.GET.get('nombre', '')
    # Otro XSS con mark_safe
    html = mark_safe(f'<h1>Bienvenido {nombre}</h1>')
    return html

@csrf_exempt
def actualizar_datos(request):
    datos = request.POST
    return datos