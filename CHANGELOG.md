# Changelog - DENTIFYFACE

Todas las actualizaciones notables de este proyecto se documentarán en este archivo. El formato está basado en Keep a Changelog.

## [1.1.0] - 2026-06-05

### Añadido
- Nuevo script de ingesta masiva asíncrona (`scripts/ingesta_lfw.py`) para procesar el dataset LFW.
- Nueva columna `vector_biometrico` (JSON) en la tabla `reportes_desaparecidos` para persistencia matemática y evitar el recálculo en cada inicio.

### Optimizado
- **Rendimiento de Inicialización:** Se redujo el tiempo de arranque de 34 minutos a ~2 segundos al cargar vectores pre-calculados desde MySQL directamente a la RAM.
- Escalabilidad aumentada a >1,000 identidades simultáneas estables, cumpliendo con los requisitos de la Categoría A.

## [1.0.0] - 2026-05-25

### Añadido
- Integración final del pipeline YOLOv8 + dlib (ResNet-29).
- Sincronización automática (carga perezosa) de la carpeta `/registrados/` hacia la memoria RAM.
- Tabla `bitacora_avistamientos` en MySQL para persistencia de detecciones.
- Lógica de "Cooldown" (10 segundos) para evitar saturación de inserts en base de datos.
- Archivo de pesos `best.pt` con Fine-Tuning para detección exclusiva de rostros.

## [0.8.0] - 2026-04-15

### Añadido
- Módulo de extracción vectorial de 128 dimensiones usando `face_recognition`.
- Primeras pruebas de estrés en CPU (Ryzen 5) alcanzando 8 FPS en operaciones de match positivo.
- Renderizado asíncrono de bounding boxes en la interfaz de OpenCV.

## [0.5.0] - 2026-03-20

### Añadido
- Inicialización del proyecto.
- Pruebas iniciales de captura de video con OpenCV forzando el backend DirectShow (CAP_DSHOW).
- Diseño del esquema relacional DDL (database.sql).
