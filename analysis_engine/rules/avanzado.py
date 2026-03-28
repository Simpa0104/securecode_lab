REGLAS_AVANZADO = [
    {
        'id': 'HASH-01',
        'nombre': 'Algoritmo de hash debil MD5',
        'nivel': 'AVANZADO',
        'owasp': 'A02 — Fallos Criptograficos',
        'severidad': 'ALTA',
        'descripcion': (
            'Se detecto uso de MD5 para hashing. '
            'MD5 es criptograficamente roto y no debe usarse para contrasenas ni integridad de datos.'
        ),
        'recomendacion': (
            'Reemplaza MD5 por algoritmos seguros como SHA-256 o bcrypt para contrasenas. '
            'En Django usa make_password() que usa PBKDF2 por defecto.'
        ),
        'patrones': [
            r'hashlib\.md5\s*\(',
            r'md5\s*\(',
        ],
    },
    {
        'id': 'HASH-02',
        'nombre': 'Algoritmo de hash debil SHA1',
        'nivel': 'AVANZADO',
        'owasp': 'A02 — Fallos Criptograficos',
        'severidad': 'MEDIA',
        'descripcion': (
            'Se detecto uso de SHA1 para hashing. '
            'SHA1 tiene colisiones conocidas y no se recomienda para seguridad.'
        ),
        'recomendacion': (
            'Usa SHA-256 o superior para integridad de datos. '
            'Para contrasenas usa siempre bcrypt, Argon2 o PBKDF2.'
        ),
        'patrones': [
            r'hashlib\.sha1\s*\(',
            r'sha1\s*\(',
        ],
    },
    {
        'id': 'CORS-01',
        'nombre': 'Configuracion insegura de CORS',
        'nivel': 'AVANZADO',
        'owasp': 'A01 — Control de Acceso Roto',
        'severidad': 'ALTA',
        'descripcion': (
            'Se detecto CORS configurado para permitir cualquier origen (*). '
            'Esto permite que cualquier sitio web haga peticiones a tu API.'
        ),
        'recomendacion': (
            'Reemplaza CORS_ALLOW_ALL_ORIGINS = True por una lista explicita: '
            'CORS_ALLOWED_ORIGINS = ["https://tudominio.com"]'
        ),
        'patrones': [
            r'CORS_ALLOW_ALL_ORIGINS\s*=\s*True',
            r'CORS_ORIGIN_ALLOW_ALL\s*=\s*True',
        ],
    },
    {
        'id': 'REDIRECT-01',
        'nombre': 'Open Redirect',
        'nivel': 'AVANZADO',
        'owasp': 'A01 — Control de Acceso Roto',
        'severidad': 'MEDIA',
        'descripcion': (
            'Se detecto una redireccion usando datos del request sin validacion. '
            'Un atacante puede redirigir usuarios a sitios maliciosos.'
        ),
        'recomendacion': (
            'Nunca uses redirect() con datos directos del usuario sin validar. '
            'Valida que la URL de destino pertenezca a tu dominio antes de redirigir.'
        ),
        'patrones': [
            r'redirect\s*\(\s*request\.(GET|POST)',
            r'HttpResponseRedirect\s*\(\s*request\.(GET|POST)',
        ],
    },
    {
        'id': 'DEP-01',
        'nombre': 'Dependencia sin version fija',
        'nivel': 'AVANZADO',
        'owasp': 'A06 — Componentes Vulnerables',
        'severidad': 'BAJA',
        'descripcion': (
            'Se encontro una dependencia en requirements.txt sin version especificada. '
            'Sin version fija pip puede instalar versiones con vulnerabilidades conocidas.'
        ),
        'recomendacion': (
            'Especifica siempre la version exacta de cada dependencia. '
            'Ejemplo: Django==4.2.1 en lugar de solo Django. '
            'Usa pip freeze > requirements.txt para fijar todas las versiones.'
        ),
        'patrones': [
            r'^[a-zA-Z][a-zA-Z0-9_\-]*\s*$',
        ],
    },
    {
        'id': 'SSL-01',
        'nombre': 'Verificacion SSL desactivada',
        'nivel': 'AVANZADO',
        'owasp': 'A02 — Fallos Criptograficos',
        'severidad': 'ALTA',
        'descripcion': (
            'Se detecto una peticion HTTP con verificacion SSL desactivada (verify=False). '
            'Esto hace vulnerable la conexion a ataques de intermediario (MITM).'
        ),
        'recomendacion': (
            'Nunca uses verify=False en produccion. '
            'Si tienes problemas con certificados actualiza el bundle con: pip install certifi'
        ),
        'patrones': [
            r'requests\.(get|post|put|delete|patch)\s*\(.*verify\s*=\s*False',
            r'verify\s*=\s*False',
        ],
    },
]