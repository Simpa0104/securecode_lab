"""
analysis_engine/rules/basico.py
Reglas de nivel basico — OWASP A03, A05, A07
Patrones simples y mas comunes en proyectos academicos.
"""

REGLAS_BASICO = [
    {
        'id': 'SQL-01',
        'nombre': 'SQL Injection',
        'nivel': 'BASICO',
        'owasp': 'A03 — Inyeccion',
        'severidad': 'CRITICA',
        'descripcion': 'Se detecto concatenacion de variables en consultas SQL sin parametrizacion.',
        'recomendacion': (
            'Usa consultas parametrizadas con el ORM de Django o cursor.execute() '
            'con parametros separados. Ejemplo seguro: '
            'cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])'
        ),
        'patrones': [
            r'execute\s*\(\s*["\'].*%s.*["\'].*%.*\)',
            r'execute\s*\(\s*f["\']',
            r'execute\s*\(\s*["\'].*\+',
            r'raw\s*\(\s*f["\']',
            r'raw\s*\(\s*["\'].*\+',
        ],
    },
    {
        'id': 'XSS-01',
        'nombre': 'Cross-Site Scripting (XSS)',
        'nivel': 'BASICO',
        'owasp': 'A03 — Inyeccion',
        'severidad': 'ALTA',
        'descripcion': 'Se detecto uso de mark_safe() o el filtro |safe sin sanitizacion previa.',
        'recomendacion': (
            'Evita usar mark_safe() con datos del usuario. '
            'Si necesitas renderizar HTML usa bleach.clean() para sanitizar primero.'
        ),
        'patrones': [
            r'mark_safe\s*\(',
            r'\|\s*safe',
        ],
    },
    {
        'id': 'CSRF-01',
        'nombre': 'Proteccion CSRF desactivada',
        'nivel': 'BASICO',
        'owasp': 'A05 — Configuracion Incorrecta',
        'severidad': 'ALTA',
        'descripcion': 'Se encontro el decorador @csrf_exempt aplicado a una vista.',
        'recomendacion': (
            'El decorador @csrf_exempt desactiva la proteccion CSRF. '
            'Usalo solo en APIs con autenticacion por token. '
            'En vistas de formulario HTML nunca lo uses.'
        ),
        'patrones': [
            r'@csrf_exempt',
        ],
    },
    {
        'id': 'CONFIG-01',
        'nombre': 'DEBUG activado',
        'nivel': 'BASICO',
        'owasp': 'A05 — Configuracion Incorrecta',
        'severidad': 'ALTA',
        'descripcion': 'Se encontro DEBUG = True en el archivo de configuracion.',
        'recomendacion': (
            'DEBUG = True nunca debe estar activo en produccion. '
            'Usa variables de entorno: DEBUG = os.environ.get("DEBUG", "False") == "True"'
        ),
        'patrones': [
            r'DEBUG\s*=\s*True',
        ],
    },
    {
        'id': 'CONFIG-02',
        'nombre': 'Secret Key expuesta',
        'nivel': 'BASICO',
        'owasp': 'A05 — Configuracion Incorrecta',
        'severidad': 'CRITICA',
        'descripcion': 'Se encontro una SECRET_KEY escrita directamente en el codigo.',
        'recomendacion': (
            'La SECRET_KEY nunca debe estar en el codigo fuente. '
            'Muevela a una variable de entorno: SECRET_KEY = os.environ.get("SECRET_KEY")'
        ),
        'patrones': [
            r'SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']',
        ],
    },
    {
        'id': 'CONFIG-03',
        'nombre': 'ALLOWED_HOSTS vacio',
        'nivel': 'BASICO',
        'owasp': 'A05 — Configuracion Incorrecta',
        'severidad': 'MEDIA',
        'descripcion': 'ALLOWED_HOSTS esta configurado como lista vacia [].',
        'recomendacion': (
            'En produccion ALLOWED_HOSTS debe contener el dominio o IP del servidor. '
            'Ejemplo: ALLOWED_HOSTS = ["midominio.com"]'
        ),
        'patrones': [
            r'ALLOWED_HOSTS\s*=\s*\[\s*\]',
        ],
    },
    {
        'id': 'AUTH-01',
        'nombre': 'Contrasena en texto plano',
        'nivel': 'BASICO',
        'owasp': 'A07 — Fallos de Autenticacion',
        'severidad': 'ALTA',
        'descripcion': 'Se detecto almacenamiento o comparacion de contrasenas sin hashing.',
        'recomendacion': (
            'Nunca almacenes contrasenas en texto plano. '
            'Usa make_password() y check_password() de Django.'
        ),
        'patrones': [
            r'password\s*=\s*["\'][^"\']{3,}["\']',
            r'password\s*==\s*request\.',
            r'passwd\s*=\s*["\']',
            r'\.password\s*=\s*request\.',
        ],
    },
    {
        'id': 'INFO-01',
        'nombre': 'Credenciales hardcodeadas',
        'nivel': 'BASICO',
        'owasp': 'A07 — Fallos de Autenticacion',
        'severidad': 'CRITICA',
        'descripcion': 'Se encontraron posibles credenciales escritas directamente en el codigo.',
        'recomendacion': (
            'Nunca escribas usuarios, contrasenas, tokens o API keys en el codigo. '
            'Usa variables de entorno o un gestor de secretos.'
        ),
        'patrones': [
            r'api_key\s*=\s*["\'][^"\']{8,}["\']',
            r'token\s*=\s*["\'][^"\']{8,}["\']',
        ],
    },
]