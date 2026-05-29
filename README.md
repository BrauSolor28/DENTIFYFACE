# Sistema de Búsqueda Masiva por Visión Artificial

Sistema automatizado de reconocimiento facial diseñado para identificar personas desaparecidas mediante cámaras de seguridad, utilizando YOLOv8 para la detección de rostros y Face Recognition para la identificación biométrica cruzada con una base de datos MySQL.

## Requisitos Previos (Dependencias del Sistema)

- **Python 3.10 o superior**
- **Servidor MySQL** (XAMPP o instalación nativa)
- **Compiladores C++**: 
  - *Windows*: Visual Studio Build Tools (C++).
  - *Linux*: `sudo apt install build-essential cmake`.

## Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone [https://github.com/BrauSolor28/DENTIFYFACE.git](https://github.com/BrauSolor28/DENTIFYFACE.git)
cd DENTIFYFACE
```

### 2. Crear y activar un entorno virtual (Recomendado)

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos
- Inicia tu servidor MySQL (ej. arranca XAMPP).
- Importa el archivo `database.sql` en tu gestor de base de datos (como phpMyAdmin) para crear la estructura de tablas.

### 5. Añadir perfiles a buscar
- Coloca las fotografías de las personas en la carpeta `registrados/` (crea la carpeta si no existe).
- El nombre del archivo debe ser el nombre exacto de la persona (Ej. `Juan_Perez.jpg`).

### 6. Ejecutar el sistema
```bash
python main.py
```

## Arquitectura del Proyecto

El proyecto separa el almacenamiento de archivos pesados de la base de datos transaccional para garantizar escalabilidad:

- **Imágenes:** Se procesan de forma local mediante lectura de directorios.
- **Datos Estructurados:** La identidad, estatus y bitácoras de avistamiento residen en MySQL.
- **Filtro Primario:** El modelo YOLOv8 (`best.pt`) actúa como filtro inicial de detección humana, reduciendo drásticamente la carga de procesamiento del escáner biométrico.