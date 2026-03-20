"""
analysis_engine/analyzer.py
Motor principal de analisis estatico de SecureCode Lab.
Las reglas estan separadas por nivel en analysis_engine/rules/.
"""

import re
import zipfile
import os
import tempfile

from .rules.basico import REGLAS_BASICO
from .rules.intermedio import REGLAS_INTERMEDIO
from .rules.avanzado import REGLAS_AVANZADO


# Niveles acumulativos — cada nivel incluye las reglas de los anteriores
REGLAS_POR_NIVEL = {
    'BASICO':     REGLAS_BASICO,
    'INTERMEDIO': REGLAS_BASICO + REGLAS_INTERMEDIO,
    'AVANZADO':   REGLAS_BASICO + REGLAS_INTERMEDIO + REGLAS_AVANZADO,
}


def analizar_contenido(codigo, nombre_archivo, nivel='BASICO'):
    """
    Analiza el contenido de un archivo linea por linea
    usando las reglas del nivel indicado.
    """
    vulnerabilidades = []
    reglas = REGLAS_POR_NIVEL.get(nivel, REGLAS_BASICO)
    lineas = codigo.splitlines()

    for regla in reglas:
        for num_linea, linea in enumerate(lineas, start=1):
            linea_limpia = linea.strip()

            # Ignorar comentarios excepto para la regla COMMENT-01
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


def analizar_archivo_py(ruta_archivo, nombre_mostrar=None, nivel='BASICO'):
    """Analiza un archivo .py individual."""
    nombre = nombre_mostrar or os.path.basename(ruta_archivo)
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            codigo = f.read()
        return analizar_contenido(codigo, nombre, nivel)
    except Exception:
        return []


def analizar_requirements(ruta_archivo, nombre_mostrar='requirements.txt'):
    """
    Analiza requirements.txt buscando dependencias sin version fija.
    Solo se activa en nivel AVANZADO.
    """
    vulnerabilidades = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            lineas = f.readlines()

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
                    'descripcion':   'Se encontro una dependencia sin version especificada.',
                    'recomendacion': (
                        'Especifica la version exacta. '
                        'Ejemplo: Django==4.2.1 en lugar de solo Django.'
                    ),
                    'archivo':       nombre_mostrar,
                    'linea':         num_linea,
                    'codigo_linea':  linea_limpia,
                })
    except Exception:
        pass

    return vulnerabilidades


def analizar_zip(ruta_zip, nivel='BASICO'):
    """
    Descomprime el ZIP, analiza todos los .py encontrados
    y requirements.txt si el nivel es AVANZADO.
    """
    vulnerabilidades = []

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with zipfile.ZipFile(ruta_zip, 'r') as zf:
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
                        vulnerabilidades += analizar_archivo_py(
                            ruta_completa, nombre_relativo, nivel
                        )
                    elif filename == 'requirements.txt' and nivel == 'AVANZADO':
                        vulnerabilidades += analizar_requirements(
                            ruta_completa, nombre_relativo
                        )

        except zipfile.BadZipFile:
            pass

    return vulnerabilidades


def calcular_score(vulnerabilidades):
    """
    Calcula el score de seguridad de 0 a 100.
    Penalizacion por severidad:
      CRITICA: -25
      ALTA:    -15
      MEDIA:   -8
      BAJA:    -3
    """
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
    """Retorna etiqueta y color Bootstrap segun el score."""
    if score >= 80:
        return {'etiqueta': 'Seguro',     'color': 'success'}
    elif score >= 60:
        return {'etiqueta': 'Aceptable',  'color': 'warning'}
    elif score >= 40:
        return {'etiqueta': 'Vulnerable', 'color': 'orange'}
    else:
        return {'etiqueta': 'Critico',    'color': 'danger'}


def ejecutar_analisis(proyecto, nivel='BASICO'):
    """
    Funcion principal. Recibe un objeto Project y el nivel de analisis,
    ejecuta el motor y retorna el resultado completo.
    """
    ruta = proyecto.file.path
    extension = os.path.splitext(ruta)[1].lower()

    if extension == '.py':
        vulnerabilidades = analizar_archivo_py(ruta, os.path.basename(ruta), nivel)
    elif extension == '.zip':
        vulnerabilidades = analizar_zip(ruta, nivel)
    else:
        vulnerabilidades = []

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