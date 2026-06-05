# 1. DENTIFYFACE: Sistema de Búsqueda Masiva por Visión Artificial

Sistema automatizado de videovigilancia y reconocimiento facial en tiempo real enfocado en la búsqueda de perfiles activos sin requerir supervisión humana constante. Combina YOLOv8 para la detección espacial con dlib (ResNet-29) para la extracción biométrica, operando 100% on-premise con hardware estándar.

## Video de Demostración
https://youtu.be/syAlH_rWybE

---

# 2. Información del Concurso

* **Categoría:** Categoría A - Reconocimiento Facial
* **Nombre del Equipo:** DENTIFYFACE

---

# 3. Tabla de Contenidos

- [1. DENTIFYFACE: Sistema de Búsqueda Masiva por Visión Artificial](#1-dentifyface-sistema-de-búsqueda-masiva-por-visión-artificial)
- [2. Información del Concurso](#2-información-del-concurso)
- [3. Tabla de Contenidos](#3-tabla-de-contenidos)
- [4. Requisitos del sistema](#4-requisitos-del-sistema)
- [5. Instalación](#5-instalación)
- [6. Configuración](#6-configuración)
- [7. Dataset y Modelos](#7-dataset-y-modelos)
- [8. Ejecución](#8-ejecución)
- [9. Cómo probar el sistema](#9-cómo-probar-el-sistema)
- [10. Pruebas Automatizadas](#10-pruebas-automatizadas)
- [11. Estructura del Proyecto](#11-estructura-del-proyecto)
- [12. Tecnologías Utilizadas](#12-tecnologías-utilizadas)
- [13. Métricas Principales](#13-métricas-principales)
- [14. Limitaciones Conocidas](#14-limitaciones-conocidas)
- [15. Créditos y Licencia](#15-créditos-y-licencia)

---

# 4. Requisitos del sistema

* **Sistema Operativo:** Windows 10/11 o Linux (Ubuntu 22.04+).
* **Hardware Mínimo:** CPU de 4 núcleos (Ej. AMD Ryzen 5), 8 GB RAM, Cámara Web 640x480. No requiere GPU dedicada.
* **Software Base:** Python 3.13 (64-bit), MySQL Server (10.4.32), Git y Compiladores C++ (Visual Studio Build Tools en Windows / `build-essential cmake` en Linux).

---

# 5. Instalación

Asumiendo un entorno limpio, abre la terminal y ejecuta:

```bash
git clone [https://github.com/BrauSolor28/DENTIFYFACE.git](https://github.com/BrauSolor28/DENTIFYFACE.git)
cd DENTIFYFACE
python -m venv env
# En Windows: env\Scripts\activate
# En Linux: source env/bin/activate
pip install -r requirements.txt
```

---

# 6. Configuración

* Inicia tu servicio local de MySQL (ej. XAMPP o servicio nativo).
* Importa el archivo DDL ubicado en `scripts/database.sql` para generar la base de datos `sistema_busqueda_masiva`.
* Por defecto, el script se conecta al usuario `root` sin contraseña en `localhost`. Si tu entorno es distinto, edita las credenciales en la sección de conexión dentro de `src/main.py`.

---

## 7. Dataset y Modelos

* **Modelo YOLOv8:** El archivo de pesos afinado (`best.pt`) ya se encuentra incluido en el directorio raíz. Fue entrenado con 3,647 imágenes de Roboflow para detectar exclusivamente rostros humanos.
* **Padrón Masivo (Prueba de Estrés):** Para inicializar la base de datos con el padrón de control requerido (>1,000 identidades), el sistema utiliza el dataset público Labeled Faces in the Wild (LFW).
* **Fotografías de Control Local:** Imágenes estáticas (.jpg, .png) para pruebas en tiempo real se colocan dentro del directorio `/registrados/`. El sistema las sincroniza en caliente (Zero-Shot Learning).

---

## 8. Ejecución

El sistema cuenta con una arquitectura desacoplada. Para levantar el proyecto por primera vez, ejecuta los siguientes pasos:

**Paso 1: Sembrar la Base de Datos (Ingesta Masiva)**
1. Descarga el dataset LFW en su versión alineada desde: `http://vis-www.cs.umass.edu/lfw/lfw-deepfunneled.tgz`
2. Descomprime el archivo y coloca la carpeta resultante (renombrada como `lfw`) dentro del directorio `scripts/`.
3. Ejecuta el script de inyección para vectorizar los perfiles directamente en MySQL:
   `python scripts/ingesta_lfw.py`

**Paso 2: Iniciar el Sistema Principal**
Asegúrate de tener tu cámara conectada y ejecuta el orquestador:
`python src/main.py`

---

# 9. Cómo probar el sistema

1. Ejecuta el sistema. La terminal mostrará `[OK] Conexión a MySQL Exitosa`.
2. Párate frente a la cámara. Si no estás en la carpeta `/registrados/`, el sistema dibujará un cuadro gris indicando *"No en BD"*.
3. Cierra el sistema (tecla `q`), añade una foto tuya a `/registrados/` y vuelve a ejecutar.
4. Párate de nuevo frente a la cámara. El cuadro será **ROJO**, mostrará tu nombre, y si revisas tu base de datos MySQL (tabla `bitacora_avistamientos`), verás el registro de tu avistamiento insertado automáticamente.

---

# 10. Pruebas Automatizadas

Las pruebas unitarias del flujo de base de datos y procesamiento lógico se encuentran en la carpeta `tests/`. Para ejecutarlas:

```bash
# (Comando reservado para futura implementación de pytest)
python -m unittest discover -s tests
```

---

# 11. Estructura del Proyecto

```plaintext
DENTIFYFACE/
├── docs/               # Documentación técnica y Ficha de proyecto final (PDF/DOCX)
├── scripts/            # Script DDL (database.sql) y script de ingesta (ingesta_lfw.py)
├── src/                # Código fuente principal (main.py)
├── tests/              # Pruebas automatizadas y unitarias
├── registrados/        # Directorio local de ingesta de identidades (Dataset en vivo)
├── best.pt             # Pesos de red neuronal YOLOv8 entrenados
├── requirements.txt    # Dependencias de Python
└── README.md           # Este documento
```

---

# 12. Tecnologías Utilizadas

* **Python 3.13:** Orquestador principal.
* **YOLOv8 (Ultralytics):** Localización espacial (Filtro ROI).
* **dlib / face_recognition:** Extracción vectorial biométrica 128-D.
* **OpenCV 4.x:** Captura de video y renderizado HighGUI.
* **MySQL 8.x:** Persistencia relacional de identidades y bitácoras.

---

# 13. Métricas Principales

* **Desempeño nominal:** 31 FPS sosteniendo carga multi-rostro (Escenario de multitudes).
* **Precisión (Accuracy) estimada:** 96.5% configurado con distancia euclidiana estricta de 0.55 para minimizar falsos positivos.
* **Latencia I/O (Peor caso):** 111 ms de respuesta durante identificación positiva con escritura asíncrona a disco.
* **Referencia:** Para metodologías y percentiles de degradación (p50/p95), consúltese el Entregable 5 (Reporte de Pruebas de Carga).

---

# 14. Limitaciones Conocidas

* **Monoprocesamiento:** El guardado transaccional en MySQL ocurre en el hilo principal de Python, causando micro-congelamientos proporcionales a la latencia de escritura en disco.
* **Oclusión severa:** El modelo ResNet-29 de extracción facial decae dramáticamente en precisión ante oclusiones que cubren referencias geométricas clave (como el uso de cubrebocas).

---

# 15. Créditos y Licencia

**Equipo DENTIFYFACE:**
* **Francisco Hunahpu Sahagun González** - Líder de Proyecto
* **Braulio Adonahy Solorzano Santoyo** - Programador Principal
* **Miguel Mosqueda Frausto** - Investigador de Tecnologías
* **Cintya Zacmane Sandoval Torres** - Technical Writer

Este proyecto se distribuye bajo la **Licencia MIT**.
