# Aplicacion con buenas practicas de seguridad avanzadas
import os
import hashlib
import hmac
import secrets
import json
import logging
from pathlib import Path

# Configuracion desde entorno
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'https://midominio.com').split(',')
DEBUG = False

# Logger configurado correctamente — sin exponer datos sensibles
logger = logging.getLogger(__name__)


# Hashing seguro con SHA-256 y salt
def hashear_dato(dato: str) -> str:
    salt = secrets.token_bytes(32)
    clave = hashlib.pbkdf2_hmac(
        'sha256',
        dato.encode('utf-8'),
        salt,
        310000,
        dklen=32
    )
    return salt.hex() + ':' + clave.hex()


def verificar_dato(dato: str, hash_guardado: str) -> bool:
    try:
        salt_hex, clave_hex = hash_guardado.split(':')
        salt = bytes.fromhex(salt_hex)
        clave = hashlib.pbkdf2_hmac(
            'sha256',
            dato.encode('utf-8'),
            salt,
            310000,
            dklen=32
        )
        return secrets.compare_digest(clave.hex(), clave_hex)
    except (ValueError, AttributeError):
        return False


# Firma HMAC para tokens
def generar_token_firmado(payload: dict) -> str:
    datos = json.dumps(payload, sort_keys=True)
    firma = hmac.new(
        SECRET_KEY.encode(),
        datos.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{datos}:{firma}"


def verificar_token(token: str) -> dict | None:
    try:
        datos, firma_recibida = token.rsplit(':', 1)
        firma_esperada = hmac.new(
            SECRET_KEY.encode(),
            datos.encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(firma_esperada, firma_recibida):
            logger.warning('Token con firma invalida recibido.')
            return None
        return json.loads(datos)
    except (ValueError, json.JSONDecodeError):
        return None


# Validacion estricta de archivos subidos
EXTENSIONES_PERMITIDAS = {'.py', '.zip'}
TAMANO_MAXIMO = 5 * 1024 * 1024  # 5 MB


def validar_archivo(nombre: str, tamano: int, contenido: bytes) -> bool:
    extension = Path(nombre).suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValueError(f'Extension no permitida: {extension}')
    if tamano > TAMANO_MAXIMO:
        raise ValueError(f'El archivo supera el limite de 5 MB.')
    if len(contenido) != tamano:
        raise ValueError('El tamano declarado no coincide con el contenido.')
    return True


# Validacion y sanitizacion de entradas
def sanitizar_texto(texto: str, max_len: int = 200) -> str:
    if not isinstance(texto, str):
        raise TypeError('Se esperaba texto.')
    texto = texto.strip()
    if len(texto) > max_len:
        raise ValueError(f'Texto supera {max_len} caracteres.')
    return texto


# Redireccion segura — solo origenes permitidos
def redirigir_seguro(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    dominio = f"{parsed.scheme}://{parsed.netloc}"
    if dominio not in ALLOWED_ORIGINS:
        logger.warning(f'Intento de redireccion a origen no permitido: {dominio}')
        return '/'
    return url


# Consulta parametrizada segura
def consultar_db(conexion, tabla: str, campo: str, valor) -> list:
    tablas_permitidas = {'usuarios', 'proyectos', 'analisis'}
    if tabla not in tablas_permitidas:
        raise ValueError(f'Tabla no permitida: {tabla}')
    cursor = conexion.cursor()
    cursor.execute(
        f"SELECT * FROM {tabla} WHERE {campo} = ?",
        (valor,)
    )
    return cursor.fetchall()


# Generacion de tokens seguros
def nuevo_token() -> str:
    return secrets.token_urlsafe(64)


def nuevo_token_numerico(digitos: int = 6) -> str:
    return str(secrets.randbelow(10 ** digitos)).zfill(digitos)