"""
Sistema de Búsqueda Masiva - Módulo de Visión Artificial (DENTIFYFACE)
---------------------------------------------------------
Este script captura video en tiempo real, detecta rostros utilizando
un modelo YOLOv8 personalizado y compara las codificaciones biométricas
contra un padrón masivo en MySQL y un directorio local, 
registrando avistamientos positivos.
"""

import cv2
import face_recognition
import time
import os
import mysql.connector
import shutil
import json
import numpy as np
from ultralytics import YOLO

# =========================================================
# 1. CONEXIÓN A BASE DE DATOS
# =========================================================
def conectar_bd():
    """Establece la conexión con el servidor MySQL local."""
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_busqueda_masiva"
        )
        print("[OK] Conexión a MySQL Exitosa.")
        return conexion
    except Exception as e:
        print(f"[ERROR] Conectando a BD: {e}")
        exit()

conexion = conectar_bd()
cursor = conexion.cursor()

# =========================================================
# 2. CARGA DE MODELOS Y SINCRONIZACIÓN DE DATOS
# =========================================================
print("\n[INFO] Cargando modelo de detección YOLO (best.pt)...")
modelo_yolo = YOLO('best.pt')

nombres_conocidos = []
encodings_conocidos = []
nombres_a_ids = {} 

# --- 2.1 Cargar el padrón masivo desde MySQL al instante ---
print("\n[INFO] Cargando padrón masivo desde MySQL (Esto tomará solo unos segundos)...")
try:
    cursor.execute("SELECT id_persona, nombre_completo, vector_biometrico FROM reportes_desaparecidos WHERE vector_biometrico IS NOT NULL")
    registros_bd = cursor.fetchall()
    
    for id_persona, nombre, vector_json in registros_bd:
        # Convertimos el texto JSON de regreso a la matriz matemática de numpy
        vector_array = np.array(json.loads(vector_json))
        encodings_conocidos.append(vector_array)
        nombres_conocidos.append(nombre)
        nombres_a_ids[nombre] = id_persona
        
    print(f"  -> {len(registros_bd)} perfiles cargados desde MySQL a la memoria RAM.")
except Exception as e:
    print(f"[ERROR] No se pudo cargar de BD: {e}")

# --- 2.2 Sincronización en caliente del directorio local (Zero-Shot Learning) ---
print("\n[INFO] Sincronizando directorio local /registrados/...")
carpeta_fotos = "registrados"

if not os.path.exists(carpeta_fotos):
    os.makedirs(carpeta_fotos)

# Lee todas las imágenes del directorio y extrae características faciales
for nombre_archivo in os.listdir(carpeta_fotos):
    if nombre_archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
        nombre_persona = os.path.splitext(nombre_archivo)[0].replace("_", " ")
        ruta_completa = os.path.join(carpeta_fotos, nombre_archivo)
        
        # Omitimos si ya lo cargamos desde la base de datos para no duplicar trabajo
        if nombre_persona in nombres_conocidos:
            continue
            
        imagen = face_recognition.load_image_file(ruta_completa)
        encodings = face_recognition.face_encodings(imagen)
        
        if len(encodings) > 0:
            vector_actual = encodings[0]
            encodings_conocidos.append(vector_actual)
            nombres_conocidos.append(nombre_persona)
            
            # Sincronización con MySQL: Verifica si existe, si no, lo registra con todo y vector
            cursor.execute("SELECT id_persona FROM reportes_desaparecidos WHERE nombre_completo = %s", (nombre_persona,))
            resultado_db = cursor.fetchone()
            
            if not resultado_db:
                vector_json_nuevo = json.dumps(vector_actual.tolist())
                sql_insert = "INSERT INTO reportes_desaparecidos (nombre_completo, nombre_foto, vector_biometrico) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (nombre_persona, nombre_archivo, vector_json_nuevo))
                conexion.commit()
                id_persona = cursor.lastrowid
                print(f"  -> Nuevo registro local creado en BD: {nombre_persona}")
            else:
                id_persona = resultado_db[0]
            
            nombres_a_ids[nombre_persona] = id_persona
        else:
            print(f"[ADVERTENCIA] Calidad insuficiente o rostro no detectado en: {nombre_archivo}")
            # Movemos el archivo a la lista de inválidos
            carpeta_invalidos = "invalidos"
            if not os.path.exists(carpeta_invalidos):
                os.makedirs(carpeta_invalidos)
            
            ruta_invalida = os.path.join(carpeta_invalidos, nombre_archivo)
            shutil.move(ruta_completa, ruta_invalida)
            print(f"  -> Archivo movido a la carpeta de registros inválidos.")

print(f"\n[INFO] Sistema iniciado. Vigilando {len(nombres_conocidos)} perfiles.\n")

# =========================================================
# 3. MÓDULO DE VIDEO Y PROCESAMIENTO EN TIEMPO REAL
# =========================================================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

NOMBRE_CAMARA = "Camara_Principal_Campus"
contador_frames = 0
memoria_rostros = []
ultimos_registros = {} 
TIEMPO_COOLDOWN = 10 # Segundos entre registros del mismo sujeto

print(">> PRESIONA 'q' PARA DETENER EL SISTEMA <<")

tiempo_anterior = 0

while True:
    ret, frame = cap.read()
    if not ret: break

    # Optimización: YOLO evalúa 1 de cada 5 fotogramas
    if contador_frames % 5 == 0:
        resultados = modelo_yolo(frame, stream=True, verbose=False, conf=0.4)
        memoria_rostros.clear() 
        
        for resultado in resultados:
            for caja in resultado.boxes:
                x1, y1, x2, y2 = map(int, caja.xyxy[0])
                recorte_cara = frame[y1:y2, x1:x2]
                nombre_pantalla = "No en BD"
                color_cuadro = (200, 200, 200) 
                
                if recorte_cara.size > 0:
                    rgb_recorte = cv2.cvtColor(recorte_cara, cv2.COLOR_BGR2RGB)
    
                    # 1. Sacamos las medidas del recorte
                    alto, ancho, _ = rgb_recorte.shape
    
                    # 2. Le decimos explícitamente a dlib dónde está la cara en el recorte
                    ubicacion_exacta = [(0, ancho, alto, 0)]
    
                    # 3. Extracción vectorial optimizada
                    face_encodings_detectados = face_recognition.face_encodings(rgb_recorte, known_face_locations=ubicacion_exacta)
                    
                    if face_encodings_detectados:
                        encoding_actual = face_encodings_detectados[0]
                        
                        # Comparación vectorial masiva
                        if len(encodings_conocidos) > 0:
                            coincidencias = face_recognition.compare_faces(encodings_conocidos, encoding_actual, tolerance=0.55)
                            
                            if True in coincidencias:
                                indice_match = coincidencias.index(True)
                                nombre_pantalla = nombres_conocidos[indice_match]
                                id_detectado = nombres_a_ids[nombre_pantalla]
                                color_cuadro = (0, 0, 255) 
                                
                                # Control de spam en Base de Datos (Cooldown)
                                tiempo_actual = time.time()
                                ultimo_tiempo_registro = ultimos_registros.get(id_detectado, 0)
                                
                                if (tiempo_actual - ultimo_tiempo_registro) > TIEMPO_COOLDOWN:
                                    try:
                                        sql_avistamiento = "INSERT INTO bitacora_avistamientos (id_persona, camara_origen) VALUES (%s, %s)"
                                        cursor.execute(sql_avistamiento, (id_detectado, NOMBRE_CAMARA))
                                        conexion.commit()
                                        print(f"[ALERTA] Localización: {nombre_pantalla} en {NOMBRE_CAMARA}")
                                        ultimos_registros[id_detectado] = tiempo_actual
                                    except Exception as e:
                                        print(f"[ERROR] BD: {e}")
                
                memoria_rostros.append({"coordenadas": (x1, y1, x2, y2), "nombre": nombre_pantalla, "color": color_cuadro})

    # Renderizado gráfico fluido
    for rostro in memoria_rostros:
        x1, y1, x2, y2 = rostro["coordenadas"]
        color = rostro["color"]
        nombre = rostro["nombre"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.rectangle(frame, (x1, y1 - 25), (x2, y1), color, cv2.FILLED)
        cv2.putText(frame, nombre, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    contador_frames += 1
    if contador_frames > 1000: contador_frames = 0
    tiempo_actual = time.time()
    tiempo_procesamiento_ms = (tiempo_actual - tiempo_anterior) * 1000
    fps = 1 / (tiempo_actual - tiempo_anterior) if (tiempo_actual - tiempo_anterior) > 0 else 0
    tiempo_anterior = tiempo_actual
    
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Latencia: {int(tiempo_procesamiento_ms)} ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow('Sistema de Busqueda Masiva (DENTIFYFACE)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
if conexion.is_connected():
    cursor.close()
    conexion.close()
    print("[OK] Conexión cerrada.")
