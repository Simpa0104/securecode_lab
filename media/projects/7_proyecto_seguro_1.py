# Aplicacion web con buenas practicas de seguridad basicas
import os
import sqlite3
import hashlib
import secrets

# Configuracion desde variables de entorno, nunca hardcodeada
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')


def hashear_password(password: str) -> str:
    # Uso de algoritmo seguro con salt
    salt = secrets.token_hex(32)
    clave = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        310000
    )
    return f"{salt}:{clave.hex()}"


def verificar_password(password: str, hash_guardado: str) -> bool:
    salt, clave_hex = hash_guardado.split(':')
    clave_nueva = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        310000
    )
    return secrets.compare_digest(clave_nueva.hex(), clave_hex)


def buscar_usuario(user_id: int):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    # Consulta parametrizada - sin concatenacion de strings
    cursor.execute("SELECT id, username, email FROM usuarios WHERE id = ?", (user_id,))
    return cursor.fetchone()


def buscar_por_username(username: str):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    # Parametrizada con named placeholder
    cursor.execute(
        "SELECT id, username FROM usuarios WHERE username = ?",
        (username,)
    )
    return cursor.fetchone()


def login(username: str, password: str) -> bool:
    usuario = buscar_por_username(username)
    if not usuario:
        # Tiempo constante para evitar enumeracion de usuarios
        secrets.compare_digest('a', 'b')
        return False
    hash_guardado = obtener_hash(usuario[0])
    return verificar_password(password, hash_guardado)


def obtener_hash(user_id: int) -> str:
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM usuarios WHERE id = ?", (user_id,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else ''


def generar_token() -> str:
    # Token criptograficamente seguro
    return secrets.token_urlsafe(64)


def validar_entrada(texto: str, max_longitud: int = 255) -> str:
    if not isinstance(texto, str):
        raise ValueError('Se esperaba una cadena de texto.')
    texto = texto.strip()
    if len(texto) > max_longitud:
        raise ValueError(f'La entrada supera el limite de {max_longitud} caracteres.')
    return texto