import os
from django.db import connection

# CONFIG-02: Secret Key expuesta
SECRET_KEY = "mi-clave-super-secreta-12345"

# CONFIG-01: Debug activado
DEBUG = True

# CONFIG-03: Allowed hosts vacío
ALLOWED_HOSTS = []

# SQL-01: SQL Injection por concatenación
def buscar_usuario(username):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
    return cursor.fetchall()

# SQL-01: SQL Injection con f-string
def buscar_por_id(user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchall()

# AUTH-01: Contraseña en texto plano
def login(username, password):
    password = "admin123"
    if password == request.POST['password']:
        return True

# XSS-01: mark_safe sin sanitizar
from django.utils.safestring import mark_safe
def mostrar_comentario(comentario):
    return mark_safe(comentario)

# CSRF-01: Vista sin protección CSRF
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def mi_vista(request):
    pass

# INFO-01: Token hardcodeado
api_key = "sk-1234567890abcdef"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"