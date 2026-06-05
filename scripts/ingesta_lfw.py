import os
import face_recognition
import mysql.connector
import json

def inyectar_lfw_a_mysql():
    print("[INFO] Conectando a MySQL para inyección masiva...")
    conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sistema_busqueda_masiva")
    cursor = conexion.cursor()

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    ruta_lfw = os.path.join(directorio_actual, "lfw-deepfunneled")
    contador = 0

    print("[INFO] Leyendo carpetas de LFW...")
    for nombre_persona in os.listdir(ruta_lfw):
        carpeta_persona = os.path.join(ruta_lfw, nombre_persona)
        
        if os.path.isdir(carpeta_persona):
            for archivo in os.listdir(carpeta_persona):
                if archivo.lower().endswith(('.jpg', '.png')):
                    ruta_imagen = os.path.join(carpeta_persona, archivo)
                    
                    try:
                        imagen = face_recognition.load_image_file(ruta_imagen)
                        encodings = face_recognition.face_encodings(imagen)
                        
                        if len(encodings) > 0:
                            # Convertimos el arreglo de numpy a una lista normal para guardarlo como JSON
                            vector_json = json.dumps(encodings[0].tolist())
                            nombre_limpio = nombre_persona.replace("_", " ")
                            
                            sql = "INSERT INTO reportes_desaparecidos (nombre_completo, nombre_foto, vector_biometrico) VALUES (%s, %s, %s)"
                            cursor.execute(sql, (nombre_limpio, archivo, vector_json))
                            conexion.commit()
                            
                            contador += 1
                            print(f"[{contador}] Inyectado: {nombre_limpio}")
                            
                            break # Solo tomamos la primera foto de cada persona para llegar rápido a las 1000 identidades
                    except Exception as e:
                        print(f"Error procesando {archivo}: {e}")
            
            if contador >= 1050: # Nos pasamos un poquito del mínimo para estar seguros
                break 

    cursor.close()
    conexion.close()
    print(f"\n[ÉXITO] Se inyectaron {contador} identidades únicas a MySQL con sus vectores.")

if __name__ == "__main__":
    inyectar_lfw_a_mysql()