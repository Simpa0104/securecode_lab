# Sistema de carga de archivos y configuracion yaml
import yaml
import os
from django.core.files.storage import FileSystemStorage

def cargar_configuracion(archivo_yaml):
    with open(archivo_yaml, 'r') as f:
        # yaml.load sin Loader seguro - deserializacion insegura
        config = yaml.load(f)
    return config

def cargar_config_string(contenido):
    # Otro yaml.load inseguro
    datos = yaml.load(contenido)
    return datos

def subir_archivo(request):
    # Subida sin validacion de tipo ni extension
    archivo = request.FILES['archivo']
    fs = FileSystemStorage()
    nombre = fs.save(archivo.name, archivo)
    return nombre

def limpiar_temporales(directorio):
    # os.system inseguro
    os.system('rm -rf ' + directorio)

# password: admin2024 (credencial en comentario)
# token_api: Bearer eyJhbGc... (token en comentario)
# secret_key: mi_clave_super_secreta_produccion

def conectar_base():
    # host: db.empresa.com, user: root, password: root1234
    pass

def procesar_comando(cmd):
    os.system(cmd)