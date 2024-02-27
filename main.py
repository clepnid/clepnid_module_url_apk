#!/usr/bin/python

import shutil
from bottle import route, post, request, run, app, response
import base64
import sys
import bottle
import re
import mimetypes
import json
import os
import subprocess


app_apk='./app/build/outputs/apk/debug/app-debug.apk'
app_com_file='./app/build.gradle.kts'
app_com_variable = "applicationId"
nombre_variable_main_activity = 'BASE_URL'
nombre_variable_android_manisfest = "android:icon"
archivo_main_activity = "./app/src/main/java/com/example/myapplication/MainActivity.kt"
archivo_strings_xml = "./app/src/main/res/values/strings.xml"
archivo_android_manifest = "./app/src/main/AndroidManifest.xml"
nombre_etiqueta = "string"
cImg1 = "./app/src/main/res/mipmap-hdpi"
cImg2 = "./app/src/main/res/mipmap-mdpi"
cImg3 = "./app/src/main/res/mipmap-xhdpi"
cImg4 = "./app/src/main/res/mipmap-xxhdpi"
cImg5 = "./app/src/main/res/mipmap-xxxhdpi"

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

def obtener_nombre_sin_extension(nombre_archivo):
    nombre_base, extension = os.path.splitext(nombre_archivo)
    return nombre_base

def borrar_contenido_carpeta(ruta_carpeta):
    # Verificar si la carpeta existe
    if os.path.exists(ruta_carpeta):
        # Iterar sobre todos los archivos y carpetas dentro de la carpeta
        for archivo in os.listdir(ruta_carpeta):
            ruta_completa = os.path.join(ruta_carpeta, archivo)

            # Verificar si es un archivo y borrarlo
            if os.path.isfile(ruta_completa):
                os.remove(ruta_completa)
            # Verificar si es una carpeta y borrar su contenido recursivamente
            elif os.path.isdir(ruta_completa):
                shutil.rmtree(ruta_completa)

    else:
        sys.stdout.write(f"La carpeta {ruta_carpeta} no existe.")

def borrar_contenido_carpeta_imagenes():
    # Esperar a que termine la ejecución del comando
    borrar_contenido_carpeta(cImg1)
    borrar_contenido_carpeta(cImg2)
    borrar_contenido_carpeta(cImg3)
    borrar_contenido_carpeta(cImg4)
    borrar_contenido_carpeta(cImg5)

def cambiar_valor_variable_en_archivo(archivo, nombre_variable, nuevo_valor):
    with open(archivo, 'r') as file:
        contenido = file.read()

    # Utilizar expresiones regulares para buscar la variable y su valor entre comillas
    patron = re.compile(re.escape(nombre_variable) + r'\s*=\s*["\'](.*?)["\']', re.DOTALL)
    contenido_modificado = patron.sub(f'{nombre_variable} = "{nuevo_valor}"', contenido)

    with open(archivo, 'w') as file:
        file.write(contenido_modificado)

def cambiar_valor_etiqueta_en_archivo(archivo, nombre_etiqueta, nuevo_valor):
    with open(archivo, 'r') as file:
        contenido = file.read()

    # Buscar la etiqueta específica
    inicio_etiqueta = f"<{nombre_etiqueta}"
    fin_etiqueta = f"</{nombre_etiqueta}>"

    inicio_indice = contenido.find(inicio_etiqueta)
    fin_indice = contenido.find(fin_etiqueta, inicio_indice)

    if inicio_indice != -1 and fin_indice != -1:
        # Extraer la etiqueta completa
        etiqueta_completa = contenido[inicio_indice:fin_indice + len(fin_etiqueta)]

        # Buscar el valor actual de la etiqueta
        inicio_valor = etiqueta_completa.find('>') + 1
        fin_valor = etiqueta_completa.find('</')

        if inicio_valor != -1 and fin_valor != -1:
            valor_actual = etiqueta_completa[inicio_valor:fin_valor]

            # Reemplazar el valor
            nueva_etiqueta = etiqueta_completa.replace(valor_actual, nuevo_valor)

            # Reemplazar la etiqueta completa en el contenido
            contenido_modificado = contenido[:inicio_indice] + nueva_etiqueta + contenido[fin_indice + len(fin_etiqueta):]

            with open(archivo, 'w') as file:
                file.write(contenido_modificado)
        else:
            
            sys.stdout.write(f"No se encontró el valor dentro de la etiqueta {nombre_etiqueta}.")
    else:
        sys.stdout.write(f"No se encontró la etiqueta {nombre_etiqueta} en el archivo.")
        
def crear_archivo_desde_base64(base64_string, nombre_archivo):
    try:
        # Decodificar el string en base64 a bytes
        bytes_decodificados = base64.b64decode(base64_string)

        # Escribir los bytes en un archivo
        with open(nombre_archivo, 'wb') as archivo:
            archivo.write(bytes_decodificados)

        sys.stdout.write(f"Archivo '{nombre_archivo}' creado exitosamente.")
    except Exception as e:
        sys.stdout.write(f"Error al crear el archivo: {e}")
        
def get_mime_type(file_path):
    mime_type, encoding = mimetypes.guess_type(file_path)
    return mime_type

def cambiar_nombre_archivo(nombre_original, nuevo_nombre):
    # Obtener la extensión del archivo
    _, extension = os.path.splitext(nombre_original)

    # Construir el nuevo nombre con la misma extensión
    nuevo_nombre_con_extension = nuevo_nombre + extension

    return nuevo_nombre_con_extension


def file_to_base64_json(file_path):
    try:
        with open(file_path, "rb") as file:
            # Leer el contenido del archivo en bytes
            file_content = file.read()

            # Codificar el contenido en base64
            base64_encoded = base64.b64encode(file_content).decode('utf-8')

            response_data = {
                'base64_content': base64_encoded,
                'mime_type': get_mime_type(file_path)
            }

            # Devolver como JSON
            
            return response_data
    except Exception as e:
        sys.stdout.write(f"Error al convertir el archivo a base64: {e}")
        return None

@route('/url_apk', method='POST')
@enable_cors
def receive_data():
    sys.stdout = open('archivo_salida_url2apk.txt', "w")
    # Obtener el cuerpo (body) de la solicitud y imprimirlo
    body = request.body.read().decode('utf-8')
    datos_json = json.loads(body)
    url_pagina_web = datos_json.get("urlPaginaWeb")
    nombre_app = datos_json.get("nombreApp")
    nombre_archivo = datos_json.get("nombreArchivo")
    nuevo_nombre_con_extension = cambiar_nombre_archivo(nombre_archivo, "imagen")
    imagen = datos_json.get("imagen")
    
    crear_archivo_desde_base64(imagen, cImg1+"/"+nuevo_nombre_con_extension)
    crear_archivo_desde_base64(imagen, cImg2+"/"+nuevo_nombre_con_extension)
    crear_archivo_desde_base64(imagen, cImg3+"/"+nuevo_nombre_con_extension)
    crear_archivo_desde_base64(imagen, cImg4+"/"+nuevo_nombre_con_extension)
    crear_archivo_desde_base64(imagen, cImg5+"/"+nuevo_nombre_con_extension)

    cambiar_valor_variable_en_archivo(archivo_main_activity, nombre_variable_main_activity, url_pagina_web)
    cambiar_valor_variable_en_archivo(app_com_file, app_com_variable, "com.clepnid."+nombre_app)
    cambiar_valor_etiqueta_en_archivo(archivo_strings_xml, nombre_etiqueta, nombre_app)
    cambiar_valor_variable_en_archivo(archivo_android_manifest, nombre_variable_android_manisfest, "@mipmap/"+obtener_nombre_sin_extension(nuevo_nombre_con_extension))
    
    sys.stdout.write("procesando")
    comando = ["gradlew.bat", "assembleDebug"]

    # Ejecutar el comando y capturar la salida
    p = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Esperar a que el proceso termine y obtener la salida
    salida, error = p.communicate()

    # Verificar si hubo algún error en la ejecución del comando
    if p.returncode == 0:
        # Imprimir la salida del comando
        sys.stdout.write(salida)
        sys.stdout.write("Salida del comando:")
        borrar_contenido_carpeta_imagenes()
        json_data = file_to_base64_json(app_apk)
        
        response.content_type = 'application/json'
        sys.stdout.flush()  # Vacía el buffer de salida para escribir en el archivo en tiempo real
        return json.dumps(json_data)
    else:
        # Imprimir el mensaje de error
        sys.stdout.write(error)
        sys.stdout.write("Error en la ejecución del comando:")
        borrar_contenido_carpeta_imagenes()
        sys.stdout.flush()  # Vacía el buffer de salida para escribir en el archivo en tiempo real
        return ('none')


    

#/@post('/logines') # or @route('/login', method='POST')
#/def do_login():
#/   username = request.forms.get('username')
#/    password = request.forms.get('password')
#/    systemPerformance = {'cpu': username, 'ram': password}

#/    return dict(data=systemPerformance)
#/logines?username=pavon&password=1234

run(host='localhost', port=7171, debug=True)