# Aplicacion web basica con vulnerabilidades de configuracion y autenticacion
import sqlite3

DEBUG = True
SECRET_KEY = 'django-insecure-abc123xyz789supersecreto-hardcodeado-aqui'

def login(username, password):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    # Vulnerabilidad SQL Injection - concatenacion directa
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()

def verificar_admin(user, password_ingresada):
    # Contraseña en texto plano
    password_admin = 'admin123'
    if password_ingresada == password_admin:
        return True
    return False

def obtener_usuario(user_id):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    # Otra inyeccion SQL con f-string
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()