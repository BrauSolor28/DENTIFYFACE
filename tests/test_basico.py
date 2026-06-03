import unittest
import os
import sys

# Agregamos la ruta principal para poder importar módulos si fuera necesario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEntornoDentifyface(unittest.TestCase):
    
    def test_directorio_registrados_existe(self):
        """Verifica que el directorio de ingesta de imágenes exista en la raíz"""
        ruta_esperada = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'registrados'))
        self.assertTrue(os.path.exists(ruta_esperada), f"Falta el directorio crítico: {ruta_esperada}")

    def test_modelo_yolo_existe(self):
        """Verifica que el archivo de pesos de la red neuronal esté presente"""
        ruta_modelo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'best.pt'))
        self.assertTrue(os.path.exists(ruta_modelo), "No se encontró el archivo best.pt")

    def test_importacion_librerias_criticas(self):
        """Verifica que las librerías de visión y base de datos estén instaladas"""
        try:
            import cv2
            import mysql.connector
            import face_recognition
            import ultralytics
            librerias_ok = True
        except ImportError:
            librerias_ok = False
            
        self.assertTrue(librerias_ok, "Faltan dependencias críticas. Ejecuta: pip install -r requirements.txt")

if __name__ == '__main__':
    unittest.main()
