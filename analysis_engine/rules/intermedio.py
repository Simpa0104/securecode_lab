"""
analysis_engine/rules/intermedio.py
Reglas de nivel intermedio — OWASP A03, A04, A08
Patrones mas especificos que requieren mayor conocimiento para identificar.
"""

REGLAS_INTERMEDIO = [
    {
        'id': 'INJECT-01',
        'nombre': 'Uso inseguro de eval()',
        'nivel': 'INTERMEDIO',
        'owasp': 'A03 — Inyeccion',
        'severidad': 'CRITICA',
        'descripcion': (
            'Se detecto uso de eval() con datos que podrian provenir del usuario. '
            'eval() ejecuta codigo Python arbitrario, lo que permite inyeccion de codigo.'
        ),
        'recomendacion': (
            'Evita usar eval() con cualquier dato externo. '
            'Si necesitas evaluar expresiones matematicas usa ast.literal_eval() '
            'que solo acepta literales Python seguros.'
        ),
        'patrones': [
            r'eval\s*\(',
        ],
    },
    {
        'id': 'INJECT-02',
        'nombre': 'Uso inseguro de exec()',
        'nivel': 'INTERMEDIO',
        'owasp': 'A03 — Inyeccion',
        'severidad': 'CRITICA',
        'descripcion': (
            'Se detecto uso de exec() que ejecuta codigo Python dinamicamente. '
            'Si recibe datos del usuario puede ejecutar codigo malicioso.'
        ),
        'recomendacion': (
            'Evita exec() en aplicaciones web. '
            'Si necesitas ejecutar comandos del sistema usa subprocess con lista de argumentos '
            'y nunca con shell=True.'
        ),
        'patrones': [
            r'exec\s*\(',
            r'subprocess\.call\s*\(.*shell\s*=\s*True',
            r'subprocess\.run\s*\(.*shell\s*=\s*True',
            r'os\.system\s*\(',
        ],
    },
    {
        'id': 'DESER-01',
        'nombre': 'Deserializacion insegura con pickle',
        'nivel': 'INTERMEDIO',
        'owasp': 'A08 — Fallos de Integridad',
        'severidad': 'CRITICA',
        'descripcion': (
            'Se detecto uso de pickle.loads() o pickle.load(). '
            'Deserializar datos no confiables con pickle puede ejecutar codigo arbitrario.'
        ),
        'recomendacion': (
            'Nunca uses pickle con datos que provengan de fuentes externas o del usuario. '
            'Usa JSON o MessagePack para serializar datos entre sistemas.'
        ),
        'patrones': [
            r'pickle\.loads?\s*\(',
            r'import pickle',
        ],
    },
    {
        'id': 'DESER-02',
        'nombre': 'Deserializacion insegura con yaml',
        'nivel': 'INTERMEDIO',
        'owasp': 'A08 — Fallos de Integridad',
        'severidad': 'ALTA',
        'descripcion': (
            'Se detecto uso de yaml.load() sin el parametro Loader seguro. '
            'yaml.load() sin Loader puede deserializar objetos Python arbitrarios.'
        ),
        'recomendacion': (
            'Reemplaza yaml.load(data) por yaml.safe_load(data). '
            'safe_load solo permite tipos basicos de YAML sin ejecutar codigo.'
        ),
        'patrones': [
            r'yaml\.load\s*\([^)]*\)',
        ],
    },
    {
        'id': 'COMMENT-01',
        'nombre': 'Credenciales en comentarios',
        'nivel': 'INTERMEDIO',
        'owasp': 'A04 — Diseno Inseguro',
        'severidad': 'ALTA',
        'descripcion': (
            'Se encontraron posibles credenciales o tokens escritos en comentarios del codigo. '
            'Los comentarios son visibles en el repositorio y en errores de produccion.'
        ),
        'recomendacion': (
            'Nunca escribas credenciales ni tokens en comentarios. '
            'Usa variables de entorno y elimina cualquier credencial del historial de git.'
        ),
        'patrones': [
            r'#.*password\s*[=:]\s*\S+',
            r'#.*passwd\s*[=:]\s*\S+',
            r'#.*secret\s*[=:]\s*\S+',
            r'#.*token\s*[=:]\s*\S+',
            r'#.*api_key\s*[=:]\s*\S+',
        ],
    },
    {
        'id': 'UPLOAD-01',
        'nombre': 'Subida de archivos sin validacion',
        'nivel': 'INTERMEDIO',
        'owasp': 'A04 — Diseno Inseguro',
        'severidad': 'ALTA',
        'descripcion': (
            'Se detecto manejo de archivos subidos sin validacion del tipo de contenido. '
            'Sin validacion un atacante puede subir archivos ejecutables o maliciosos.'
        ),
        'recomendacion': (
            'Valida siempre el tipo MIME y la extension del archivo. '
            'Usa una lista blanca de extensiones permitidas y verifica el contenido '
            'con python-magic antes de guardar el archivo.'
        ),
        'patrones': [
            r'request\.FILES\[',
            r'request\.FILES\.get\(',
        ],
    },
]