import re
import zipfile
import os
import io
import tempfile

from .rules.basico import REGLAS_BASICO
from .rules.intermedio import REGLAS_INTERMEDIO
from .rules.avanzado import REGLAS_AVANZADO

REGLAS_POR_NIVEL = {
    'BASICO':     REGLAS_BASICO,
    'INTERMEDIO': REGLAS_BASICO + REGLAS_INTERMEDIO,
    'AVANZADO':   REGLAS_BASICO + REGLAS_INTERMEDIO + REGLAS_AVANZADO,
}


def analizar_contenido(codigo, nombre_archivo, nivel='BASICO'):
    vulnerabilidades = []
    reglas = REGLAS_POR_NIVEL.get(nivel, REGLAS_BASICO)
    lineas = codigo.splitlines()

    for regla in reglas:
        for num_linea, linea in enumerate(lineas, start=1):
            linea_limpia = linea.strip()

            if linea_limpia.startswith('#') and regla['id'] != 'COMMENT-01':
                continue

            for patron in regla['patrones']:
                if re.search(patron, linea, re.IGNORECASE):
                    vulnerabilidades.append({
                        'regla_id':      regla['id'],
                        'nombre':        regla['nombre'],
                        'nivel':         regla['nivel'],
                        'owasp':         regla['owasp'],
                        'severidad':     regla['severidad'],
                        'descripcion':   regla['descripcion'],
                        'recomendacion': regla['recomendacion'],
                        'archivo':       nombre_archivo,
                        'linea':         num_linea,
                        'codigo_linea':  linea.strip(),
                    })
                    break

    return vulnerabilidades


def analizar_requirements_contenido(contenido, nombre_mostrar='requirements.txt'):
    vulnerabilidades = []
    lineas = contenido.splitlines()

    for num_linea, linea in enumerate(lineas, start=1):
        linea_limpia = linea.strip()
        if not linea_limpia or linea_limpia.startswith('#'):
            continue
        if re.match(r'^[a-zA-Z][a-zA-Z0-9_\-]*\s*$', linea_limpia):
            vulnerabilidades.append({
                'regla_id':      'DEP-01',
                'nombre':        'Dependencia sin version fija',
                'nivel':         'AVANZADO',
                'owasp':         'A06 — Componentes Vulnerables',
                'severidad':     'BAJA',
                'descripcion':   'Se encontro una dependencia sin version especificada en requirements.txt.',
                'recomendacion': (
                    'Especifica la version exacta. '
                    'Ejemplo: Django==4.2.1 en lugar de solo Django.'
                ),
                'archivo':       nombre_mostrar,
                'linea':         num_linea,
                'codigo_linea':  linea_limpia,
            })

    return vulnerabilidades


def analizar_archivo_en_memoria(archivo_django, nivel='BASICO'):
    nombre = archivo_django.name
    extension = os.path.splitext(nombre)[1].lower()
    vulnerabilidades = []

    if extension == '.py':
        contenido = archivo_django.read().decode('utf-8', errors='ignore')
        vulnerabilidades = analizar_contenido(contenido, nombre, nivel)

    elif extension == '.zip':
        contenido_bytes = archivo_django.read()
        vulnerabilidades = analizar_zip_en_memoria(contenido_bytes, nivel)

    return vulnerabilidades


def analizar_zip_en_memoria(contenido_bytes, nivel='BASICO'):
    vulnerabilidades = []

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with zipfile.ZipFile(io.BytesIO(contenido_bytes), 'r') as zf:
                for member in zf.namelist():
                    member_path = os.path.realpath(os.path.join(tmpdir, member))
                    if not member_path.startswith(os.path.realpath(tmpdir)):
                        continue
                    zf.extract(member, tmpdir)

            for root, dirs, files in os.walk(tmpdir):
                dirs[:] = [d for d in dirs if d not in (
                    'venv', '.venv', '__pycache__', '.git', 'node_modules'
                )]

                for filename in files:
                    ruta_completa = os.path.join(root, filename)
                    nombre_relativo = os.path.relpath(ruta_completa, tmpdir)

                    if filename.endswith('.py'):
                        try:
                            with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                                codigo = f.read()
                            vulnerabilidades += analizar_contenido(codigo, nombre_relativo, nivel)
                        except Exception:
                            pass

                    elif filename == 'requirements.txt' and nivel == 'AVANZADO':
                        try:
                            with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                                contenido = f.read()
                            vulnerabilidades += analizar_requirements_contenido(
                                contenido, nombre_relativo
                            )
                        except Exception:
                            pass

        except zipfile.BadZipFile:
            pass

    return vulnerabilidades


def calcular_score(vulnerabilidades):
    PENALIZACIONES = {
        'CRITICA': 25,
        'ALTA':    15,
        'MEDIA':   8,
        'BAJA':    3,
    }
    score = 100
    for vuln in vulnerabilidades:
        score -= PENALIZACIONES.get(vuln['severidad'], 5)
    return max(0, score)


def obtener_nivel_score(score):
    if score >= 80:
        return {'etiqueta': 'Seguro',     'color': 'success'}
    elif score >= 60:
        return {'etiqueta': 'Aceptable',  'color': 'warning'}
    elif score >= 40:
        return {'etiqueta': 'Vulnerable', 'color': 'orange'}
    else:
        return {'etiqueta': 'Critico',    'color': 'danger'}


def ejecutar_analisis(archivo_django, nivel='BASICO'):
    vulnerabilidades = analizar_archivo_en_memoria(archivo_django, nivel)
    score = calcular_score(vulnerabilidades)
    nivel_score = obtener_nivel_score(score)

    return {
        'vulnerabilidades': vulnerabilidades,
        'score':    score,
        'nivel':    nivel_score,
        'total':    len(vulnerabilidades),
        'criticas': sum(1 for v in vulnerabilidades if v['severidad'] == 'CRITICA'),
        'altas':    sum(1 for v in vulnerabilidades if v['severidad'] == 'ALTA'),
        'medias':   sum(1 for v in vulnerabilidades if v['severidad'] == 'MEDIA'),
        'bajas':    sum(1 for v in vulnerabilidades if v['severidad'] == 'BAJA'),
    }