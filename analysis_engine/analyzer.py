import re
import zipfile
import os
import tempfile

# DEFINICIÓN DE REGLAS DE DETECCIÓN

RULES = [
    {
        'id': 'SQL-01',
        'nombre': 'SQL Injection',
        'severidad': 'CRITICA',
        'descripcion': 'Se detectó concatenación de variables en consultas SQL sin parametrización.',
        'recomendacion': (
            'Usa consultas parametrizadas con el ORM de Django o cursor.execute() '
            'con parámetros separados. Ejemplo seguro: '
            'cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])'
        ),
        'patrones': [
            r'execute\s*\(\s*["\'].*%s.*["\'].*%.*\)',  # cursor.execute("... %s" % var)
            r'execute\s*\(\s*f["\']',  # cursor.execute(f"...")
            r'execute\s*\(\s*["\'].*\+',  # cursor.execute("..." + var)
            r'raw\s*\(\s*f["\']',  # Model.objects.raw(f"...")
            r'raw\s*\(\s*["\'].*\+',  # Model.objects.raw("..." + var)
        ],
    },
    {
        'id': 'AUTH-01',
        'nombre': 'Contraseña en texto plano',
        'severidad': 'ALTA',
        'descripcion': 'Se detectó almacenamiento o comparación de contraseñas sin hashing.',
        'recomendacion': (
            'Nunca almacenes contraseñas en texto plano. '
            'Usa make_password() y check_password() de Django, o el sistema de autenticación '
            'integrado con set_password() y check_password() en el modelo User.'
        ),
        'patrones': [
            r'password\s*=\s*["\'][^"\']{3,}["\']',  # password = "algo"
            r'password\s*==\s*request\.',  # password == request.POST[...]
            r'passwd\s*=\s*["\']',  # passwd = "algo"
            r'\.password\s*=\s*request\.',  # user.password = request.POST
        ],
    },
    {
        'id': 'CONFIG-01',
        'nombre': 'DEBUG activado',
        'severidad': 'ALTA',
        'descripcion': 'Se encontró DEBUG = True en el archivo de configuración.',
        'recomendacion': (
            'DEBUG = True nunca debe estar activo en producción. '
            'Expone trazas de error, configuraciones internas y puede revelar información sensible. '
            'Usa variables de entorno: DEBUG = os.environ.get("DEBUG", "False") == "True"'
        ),
        'patrones': [
            r'DEBUG\s*=\s*True',
        ],
    },
    {
        'id': 'CONFIG-02',
        'nombre': 'Secret Key expuesta',
        'severidad': 'CRITICA',
        'descripcion': 'Se encontró una SECRET_KEY hardcodeada directamente en el código.',
        'recomendacion': (
            'La SECRET_KEY nunca debe estar escrita directamente en el código fuente. '
            'Muévela a una variable de entorno: '
            'SECRET_KEY = os.environ.get("SECRET_KEY")'
        ),
        'patrones': [
            r'SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']',  # SECRET_KEY = "valor-largo"
        ],
    },
    {
        'id': 'XSS-01',
        'nombre': 'Cross-Site Scripting (XSS)',
        'severidad': 'ALTA',
        'descripcion': 'Se detectó uso de mark_safe() o el filtro |safe sin sanitización previa.',
        'recomendacion': (
            'Evita usar mark_safe() con datos provenientes del usuario. '
            'Si necesitas renderizar HTML, usa bleach.clean() para sanitizar primero '
            'o asegúrate de que el contenido es 100% controlado por el sistema.'
        ),
        'patrones': [
            r'mark_safe\s*\(',  # mark_safe(variable)
            r'\|\s*safe',  # {{ variable | safe }}
        ],
    },
    {
        'id': 'CSRF-01',
        'nombre': 'Protección CSRF desactivada',
        'severidad': 'ALTA',
        'descripcion': 'Se encontró el decorador @csrf_exempt aplicado a una vista.',
        'recomendacion': (
            'El decorador @csrf_exempt desactiva la protección contra ataques CSRF. '
            'Úsalo únicamente en APIs con autenticación por token (como DRF con TokenAuthentication). '
            'En vistas de formulario HTML, nunca lo uses.'
        ),
        'patrones': [
            r'@csrf_exempt',
        ],
    },
    {
        'id': 'AUTH-02',
        'nombre': 'Vista sin control de autenticación',
        'severidad': 'MEDIA',
        'descripcion': 'Se encontraron vistas que acceden a request.user sin verificar autenticación.',
        'recomendacion': (
            'Usa el decorador @login_required en todas las vistas que requieran '
            'que el usuario esté autenticado. Ejemplo: '
            '@login_required\ndef mi_vista(request): ...'
        ),
        'patrones': [
            r'request\.user\.(?!is_authenticated|is_anonymous)',  # request.user.algo sin check
        ],
    },
    {
        'id': 'CONFIG-03',
        'nombre': 'ALLOWED_HOSTS vacío',
        'severidad': 'MEDIA',
        'descripcion': 'ALLOWED_HOSTS está configurado como lista vacía [].',
        'recomendacion': (
            'En producción, ALLOWED_HOSTS debe contener el dominio o IP del servidor. '
            'Ejemplo: ALLOWED_HOSTS = ["midominio.com", "www.midominio.com"]. '
            'Una lista vacía solo funciona correctamente con DEBUG = True.'
        ),
        'patrones': [
            r'ALLOWED_HOSTS\s*=\s*\[\s*\]',
        ],
    },
    {
        'id': 'INFO-01',
        'nombre': 'Credenciales hardcodeadas',
        'severidad': 'CRITICA',
        'descripcion': 'Se encontraron posibles credenciales escritas directamente en el código.',
        'recomendacion': (
            'Nunca escribas usuarios, contraseñas, tokens o API keys directamente en el código. '
            'Usa variables de entorno o un gestor de secretos.'
        ),
        'patrones': [
            r'api_key\s*=\s*["\'][^"\']{8,}["\']',
            r'token\s*=\s*["\'][^"\']{8,}["\']',
            r'password\s*=\s*["\'][^"\']{3,}["\']',
        ],
    },
]


# FUNCIONES DEL MOTOR

def analizar_contenido(codigo, nombre_archivo):
    vulnerabilidades = []
    lineas = codigo.splitlines()

    for regla in RULES:
        for num_linea, linea in enumerate(lineas, start=1):
            linea_limpia = linea.strip()

            # Ignorar comentarios
            if linea_limpia.startswith('#'):
                continue

            for patron in regla['patrones']:
                if re.search(patron, linea, re.IGNORECASE):
                    vulnerabilidades.append({
                        'regla_id': regla['id'],
                        'nombre': regla['nombre'],
                        'severidad': regla['severidad'],
                        'descripcion': regla['descripcion'],
                        'recomendacion': regla['recomendacion'],
                        'archivo': nombre_archivo,
                        'linea': num_linea,
                        'codigo_linea': linea.strip(),
                    })
                    break

    return vulnerabilidades


def analizar_archivo_py(ruta_archivo, nombre_mostrar=None):
    nombre = nombre_mostrar or os.path.basename(ruta_archivo)
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            codigo = f.read()
        return analizar_contenido(codigo, nombre)
    except Exception as e:
        return []


def analizar_zip(ruta_zip):
    vulnerabilidades = []

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with zipfile.ZipFile(ruta_zip, 'r') as zf:
                # Seguridad: evitar path traversal en el ZIP
                for member in zf.namelist():
                    member_path = os.path.realpath(os.path.join(tmpdir, member))
                    if not member_path.startswith(os.path.realpath(tmpdir)):
                        continue  # Saltar entradas maliciosas
                    zf.extract(member, tmpdir)

            # Recorrer todos los .py dentro del ZIP
            for root, dirs, files in os.walk(tmpdir):
                # Ignorar carpetas de dependencias
                dirs[:] = [d for d in dirs if d not in ('venv', '.venv', '__pycache__', '.git', 'node_modules')]

                for filename in files:
                    if filename.endswith('.py'):
                        ruta_completa = os.path.join(root, filename)
                        nombre_relativo = os.path.relpath(ruta_completa, tmpdir)
                        vulnerabilidades += analizar_archivo_py(ruta_completa, nombre_relativo)

        except zipfile.BadZipFile:
            pass  # El archivo ZIP está corrupto, se maneja en la vista

    return vulnerabilidades


def calcular_score(vulnerabilidades):
    PENALIZACIONES = {
        'CRITICA': 25,
        'ALTA': 15,
        'MEDIA': 8,
        'BAJA': 3,
    }

    score = 100
    for vuln in vulnerabilidades:
        score -= PENALIZACIONES.get(vuln['severidad'], 5)

    return max(0, score)  # El score nunca baja de 0


def obtener_nivel_score(score):
    if score >= 80:
        return {'etiqueta': 'Seguro', 'color': 'success'}
    elif score >= 60:
        return {'etiqueta': 'Aceptable', 'color': 'warning'}
    elif score >= 40:
        return {'etiqueta': 'Vulnerable', 'color': 'orange'}
    else:
        return {'etiqueta': 'Crítico', 'color': 'danger'}


def ejecutar_analisis(proyecto):
    ruta = proyecto.file.path
    extension = os.path.splitext(ruta)[1].lower()

    if extension == '.py':
        vulnerabilidades = analizar_archivo_py(ruta, os.path.basename(ruta))
    elif extension == '.zip':
        vulnerabilidades = analizar_zip(ruta)
    else:
        vulnerabilidades = []

    score = calcular_score(vulnerabilidades)
    nivel = obtener_nivel_score(score)

    return {
        'vulnerabilidades': vulnerabilidades,
        'score': score,
        'nivel': nivel,
        'total': len(vulnerabilidades),
        'criticas': sum(1 for v in vulnerabilidades if v['severidad'] == 'CRITICA'),
        'altas': sum(1 for v in vulnerabilidades if v['severidad'] == 'ALTA'),
        'medias': sum(1 for v in vulnerabilidades if v['severidad'] == 'MEDIA'),
        'bajas': sum(1 for v in vulnerabilidades if v['severidad'] == 'BAJA'),
    }
