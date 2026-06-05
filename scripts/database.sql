-- Estructura de la Base de Datos para Sistema de Búsqueda Masiva
CREATE DATABASE IF NOT EXISTS sistema_busqueda_masiva;
USE sistema_busqueda_masiva;

-- Tabla 1: El Registro (La ficha de la persona)
CREATE TABLE IF NOT EXISTS reportes_desaparecidos (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    nombre_foto VARCHAR(100) NOT NULL, -- Aquí guardas "001_Braulio.jpg"
    vector_biometrico JSON, -- Almacena el vector 128-D matemático extraído
    estatus_alerta VARCHAR(50) DEFAULT 'Activa', -- 'Activa' o 'Localizada'
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla 2: La Bitácora (Dónde y a qué hora los vio la cámara)
CREATE TABLE IF NOT EXISTS bitacora_avistamientos (
    id_avistamiento INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    camara_origen VARCHAR(100) DEFAULT 'Camara_Principal',
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_persona) REFERENCES reportes_desaparecidos(id_persona) ON DELETE CASCADE
);
