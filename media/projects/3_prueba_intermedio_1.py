# Procesador de datos con deserializacion y ejecucion insegura
import pickle
import subprocess
import sqlite3

DEBUG = True

def ejecutar_formula(formula_usuario):
    # Eval inseguro - permite ejecucion de codigo arbitrario
    resultado = eval(formula_usuario)
    return resultado

def procesar_script(codigo):
    # Exec inseguro
    exec(codigo)

def ejecutar_sistema(comando):
    # subprocess con shell=True
    resultado = subprocess.run(comando, shell=True, capture_output=True)
    return resultado.stdout

def cargar_sesion(datos_sesion):
    # Deserializacion insegura con pickle
    import pickle
    sesion = pickle.loads(datos_sesion)
    return sesion

def guardar_sesion(objeto):
    return pickle.dumps(objeto)

def buscar_producto(nombre):
    conn = sqlite3.connect('tienda.db')
    cursor = conn.cursor()
    password = 'clave_bd_123'
    cursor.execute("SELECT * FROM productos WHERE nombre = '" + nombre + "'")
    return cursor.fetchall()