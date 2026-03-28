# prueba_basico.py
# Archivo con vulnerabilidades de nivel BASICO
# SecureCode Lab — Archivo de prueba

import os
from django.db import connection

# CONFIG-02: Secret Key expuesta directamente en el codigo
SECRET_KEY = "mi-clave-super-secreta-12345678"

# CONFIG-01: Debug activado
DEBUG = True

# CONFIG-03: Allowed hosts vacio
ALLOWED_HOSTS = []

# SQL-01: SQL Injection por concatenacion de string
def buscar_usuario(username):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
    return cursor.fetchall()

# SQL-01: SQL Injection con f-string
def buscar_por_id(user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchall()

# AUTH-01: Contrasena en texto plano
def verificar_contrasena(usuario, contrasena):
    password = "admin123"
    return contrasena == password

# XSS-01: mark_safe sin sanitizacion
from django.utils.safestring import mark_safe
def mostrar_comentario(comentario):
    return mark_safe(comentario)

# CSRF-01: Vista sin proteccion CSRF
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def mi_vista(request):
    return None

# INFO-01: Token hardcodeado
api_key = "sk-1234567890abcdefghij"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"