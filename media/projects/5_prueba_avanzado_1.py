# Sistema de autenticacion con criptografia debil
import hashlib
import requests
import pickle
import sqlite3

DEBUG = True
SECRET_KEY = 'clave-super-secreta-hardcodeada-12345678'
CORS_ALLOW_ALL_ORIGINS = True

def hashear_password(password):
    # Hash debil MD5
    return hashlib.md5(password.encode()).hexdigest()

def verificar_integridad(archivo):
    # Hash debil SHA1
    with open(archivo, 'rb') as f:
        contenido = f.read()
    return hashlib.sha1(contenido).hexdigest()

def otro_hash_debil(dato):
    # md5 directo
    h = hashlib.md5()
    h.update(dato.encode())
    return h.hexdigest()

def consultar_api_externa(url):
    # SSL desactivado - verify=False
    respuesta = requests.get(url, verify=False)
    return respuesta.json()

def descargar_reporte(url):
    # Otro verify=False
    datos = requests.get(url, verify=False, timeout=10)
    return datos.content

def cargar_datos(raw):
    return pickle.loads(raw)

def buscar_usuario(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM usuarios WHERE id = {user_id}")
    return cursor.fetchone()