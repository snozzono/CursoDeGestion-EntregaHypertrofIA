import pandas as pd
import logging
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv



load_dotenv()
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/load_database.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

'''
DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
'''

DB_URL = os.getenv('DB_URL')

def get_engine():
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        logging.info('Conexión a PostgreSQL exitosa')
        return engine
    except Exception as e:
        logging.error(f'Error conectando a PostgreSQL: {e}')
        raise

def crear_tablas(engine):
    ddl = """
    -- Catálogo ejercicios
    CREATE TABLE IF NOT EXISTS grupo_muscular (
        id_grupo_muscular SERIAL PRIMARY KEY,
        nombre_grupo_muscular VARCHAR(50) NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS musculo (
        id_musculo SERIAL PRIMARY KEY,
        nombre_musculo VARCHAR(50) NOT NULL UNIQUE,
        id_grupo_muscular INT REFERENCES grupo_muscular(id_grupo_muscular)
    );
    CREATE TABLE IF NOT EXISTS tipo_ejercicio (
        id_tipo_ejercicio SERIAL PRIMARY KEY,
        nombre_tipo_ej VARCHAR(50) NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS equipamiento (
        id_equipamiento SERIAL PRIMARY KEY,
        nombre_equipamiento VARCHAR(50) NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS ejercicio (
        id_ejercicio INT PRIMARY KEY,
        nombre_ejercicio VARCHAR(100) NOT NULL,
        id_musculo INT REFERENCES musculo(id_musculo),
        id_tipo_ejercicio INT REFERENCES tipo_ejercicio(id_tipo_ejercicio),
        id_equipamiento INT REFERENCES equipamiento(id_equipamiento),
        porcentaje_estimulo DECIMAL(5,2),
        dificultad INT
    );

    -- Usuarios
    CREATE TABLE IF NOT EXISTS pais (
        id_pais SERIAL PRIMARY KEY,
        nombre_pais VARCHAR(50) NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS sexo_usuario (
        id_sexo SERIAL PRIMARY KEY,
        nombre_sexo_usuario VARCHAR(15) NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INT PRIMARY KEY,
        nombre_usuario VARCHAR(100) NOT NULL,
        correo_electronico VARCHAR(100) NOT NULL UNIQUE,
        id_sexo INT REFERENCES sexo_usuario(id_sexo),
        id_pais INT REFERENCES pais(id_pais)
    );
    CREATE TABLE IF NOT EXISTS caracteristicas_fisicas_usuario (
        id_caracteristicas_fisicas SERIAL PRIMARY KEY,
        id_usuario INT REFERENCES usuario(id_usuario),
        peso_corporal_kg DECIMAL(5,2),
        estatura_cm DECIMAL(5,2),
        edad INT,
        fecha_registro DATE NOT NULL
    );

    -- Rutinas
    CREATE TABLE IF NOT EXISTS enfoque (
        id_enfoque SERIAL PRIMARY KEY,
        nombre_enfoque VARCHAR(50) NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS rutina (
        id_rutina SERIAL PRIMARY KEY,
        id_usuario INT REFERENCES usuario(id_usuario),
        id_enfoque INT REFERENCES enfoque(id_enfoque),
        nombre_rutina VARCHAR(50) NOT NULL,
        fecha_creacion DATE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sesion_entrenamiento (
        id_sesion INT PRIMARY KEY,
        id_usuario INT REFERENCES usuario(id_usuario),
        id_rutina INT REFERENCES rutina(id_rutina),
        fecha_sesion DATE NOT NULL,
        duracion_minutos INT
    );
    CREATE TABLE IF NOT EXISTS detalle_rutina (
        id_detalle_rutina SERIAL PRIMARY KEY,
        id_rutina INT REFERENCES rutina(id_rutina),
        id_ejercicio INT REFERENCES ejercicio(id_ejercicio),
        cantidad_series INT NOT NULL,
        cantidad_repeticiones INT NOT NULL,
        orden_ejercicio INT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS registro_serie (
        id_registro_serie INT PRIMARY KEY,
        id_sesion INT REFERENCES sesion_entrenamiento(id_sesion),
        id_ejercicio INT REFERENCES ejercicio(id_ejercicio),
        numero_serie INT NOT NULL,
        repeticiones_logradas INT NOT NULL,
        peso_levantado_kg DECIMAL(5,2),
        rpe INT
    );

    -- Errores
    CREATE TABLE IF NOT EXISTS registros_error (
        id SERIAL PRIMARY KEY,
        origen VARCHAR(50),
        datos_originales TEXT,
        motivo_error TEXT,
        fecha_registro TIMESTAMP DEFAULT NOW()
    );
    """
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()
    logging.info('Tablas creadas o verificadas correctamente')
    print('[OK] Tablas verificadas')

def cargar_ejercicios(engine):
    df = pd.read_csv('data/processed/ejercicios_validos.csv')

    with engine.connect() as conn:
        # Grupos musculares
        for gm in df['nombre_grupo_muscular'].unique():
            conn.execute(text(
                "INSERT INTO grupo_muscular (nombre_grupo_muscular) VALUES (:v) ON CONFLICT DO NOTHING"
            ), {'v': gm})

        # Músculos
        for _, row in df[['nombre_musculo', 'nombre_grupo_muscular']].drop_duplicates().iterrows():
            conn.execute(text("""
                INSERT INTO musculo (nombre_musculo, id_grupo_muscular)
                SELECT :m, id_grupo_muscular FROM grupo_muscular WHERE nombre_grupo_muscular = :gm
                ON CONFLICT DO NOTHING
            """), {'m': row['nombre_musculo'], 'gm': row['nombre_grupo_muscular']})

        # Tipos de ejercicio
        for te in df['nombre_tipo_ejercicio'].unique():
            conn.execute(text(
                "INSERT INTO tipo_ejercicio (nombre_tipo_ej) VALUES (:v) ON CONFLICT DO NOTHING"
            ), {'v': te})

        # Equipamiento
        for eq in df['nombre_equipamiento'].unique():
            conn.execute(text(
                "INSERT INTO equipamiento (nombre_equipamiento) VALUES (:v) ON CONFLICT DO NOTHING"
            ), {'v': eq})

        # Ejercicios
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO ejercicio (id_ejercicio, nombre_ejercicio, id_musculo, id_tipo_ejercicio, id_equipamiento, porcentaje_estimulo, dificultad)
                SELECT :id, :nombre,
                    (SELECT id_musculo FROM musculo WHERE nombre_musculo = :musculo),
                    (SELECT id_tipo_ejercicio FROM tipo_ejercicio WHERE nombre_tipo_ej = :tipo),
                    (SELECT id_equipamiento FROM equipamiento WHERE nombre_equipamiento = :equipo),
                    :pct, :dif
                ON CONFLICT DO NOTHING
            """), {
                'id': int(row['id_ejercicio']),
                'nombre': row['nombre_ejercicio'],
                'musculo': row['nombre_musculo'],
                'tipo': row['nombre_tipo_ejercicio'],
                'equipo': row['nombre_equipamiento'],
                'pct': float(row['porcentaje_estimulo']),
                'dif': int(row['dificultad'])
            })

        conn.commit()
    logging.info(f'ejercicios cargados: {len(df)} registros')
    print(f'[OK] ejercicios cargados: {len(df)} registros')

def cargar_usuarios(engine):
    df = pd.read_csv('data/processed/usuarios_validos.csv')

    with engine.connect() as conn:
        for pais in df['nombre_pais'].unique():
            conn.execute(text(
                "INSERT INTO pais (nombre_pais) VALUES (:v) ON CONFLICT DO NOTHING"
            ), {'v': pais})

        for sexo in df['nombre_sexo'].unique():
            conn.execute(text(
                "INSERT INTO sexo_usuario (nombre_sexo_usuario) VALUES (:v) ON CONFLICT DO NOTHING"
            ), {'v': sexo})

        for _, row in df.iterrows():
            result = conn.execute(text("""
                INSERT INTO usuario (id_usuario, nombre_usuario, correo_electronico, id_sexo, id_pais)
                SELECT :id, :nombre, :correo,
                    (SELECT id_sexo FROM sexo_usuario WHERE nombre_sexo_usuario = :sexo),
                    (SELECT id_pais FROM pais WHERE nombre_pais = :pais)
                ON CONFLICT DO NOTHING
                RETURNING id_usuario
            """), {
                'id': int(row['id_usuario']),
                'nombre': row['nombre_usuario'],
                'correo': row['correo_electronico'],
                'sexo': row['nombre_sexo'],
                'pais': row['nombre_pais']
            })

            # Solo insertar características si el usuario fue insertado (no era duplicado)
            if result.rowcount > 0:
                conn.execute(text("""
                    INSERT INTO caracteristicas_fisicas_usuario (id_usuario, peso_corporal_kg, estatura_cm, edad, fecha_registro)
                    VALUES (:id, :peso, :estatura, :edad, :fecha)
                    ON CONFLICT DO NOTHING
                """), {
                    'id': int(row['id_usuario']),
                    'peso': float(row['peso_corporal_kg']),
                    'estatura': float(row['estatura_cm']),
                    'edad': int(row['edad']),
                    'fecha': row['fecha_registro']
                })

        conn.commit()
    logging.info(f'usuarios cargados: {len(df)} registros')
    print(f'[OK] usuarios cargados: {len(df)} registros')

def cargar_rutinas(engine):
    df = pd.read_csv('data/processed/rutinas_validas.csv')

    with engine.connect() as conn:
        for enfoque in df['nombre_enfoque'].unique():
            conn.execute(text(
                "INSERT INTO enfoque (nombre_enfoque) VALUES (:v) ON CONFLICT DO NOTHING"
            ), {'v': enfoque})

        for _, row in df[['id_usuario', 'nombre_rutina', 'nombre_enfoque', 'fecha_creacion']].drop_duplicates(subset=['id_usuario', 'nombre_rutina']).iterrows():
            conn.execute(text("""
                INSERT INTO rutina (id_usuario, id_enfoque, nombre_rutina, fecha_creacion)
                SELECT :uid,
                    (SELECT id_enfoque FROM enfoque WHERE nombre_enfoque = :enfoque),
                    :nombre, :fecha
                ON CONFLICT DO NOTHING
            """), {
                'uid': int(row['id_usuario']),
                'enfoque': row['nombre_enfoque'],
                'nombre': row['nombre_rutina'],
                'fecha': row['fecha_creacion']
            })

        for _, row in df[['id_sesion', 'id_usuario', 'nombre_rutina', 'fecha_sesion', 'duracion_minutos']].drop_duplicates(subset=['id_sesion']).iterrows():
            conn.execute(text("""
                INSERT INTO sesion_entrenamiento (id_sesion, id_usuario, id_rutina, fecha_sesion, duracion_minutos)
                SELECT :sid, :uid,
                    (SELECT id_rutina FROM rutina WHERE id_usuario = :uid AND nombre_rutina = :nombre LIMIT 1),
                    :fecha, :dur
                ON CONFLICT DO NOTHING
            """), {
                'sid': int(row['id_sesion']),
                'uid': int(row['id_usuario']),
                'nombre': row['nombre_rutina'],
                'fecha': row['fecha_sesion'],
                'dur': int(row['duracion_minutos'])
            })

        for _, row in df[['id_sesion', 'id_ejercicio', 'cantidad_series', 'cantidad_repeticiones', 'orden_ejercicio', 'nombre_rutina', 'id_usuario']].drop_duplicates(subset=['id_sesion', 'id_ejercicio']).iterrows():
            conn.execute(text("""
                INSERT INTO detalle_rutina (id_rutina, id_ejercicio, cantidad_series, cantidad_repeticiones, orden_ejercicio)
                SELECT
                    (SELECT id_rutina FROM rutina WHERE id_usuario = :uid AND nombre_rutina = :nombre LIMIT 1),
                    :ej, :series, :reps, :orden
                ON CONFLICT DO NOTHING
            """), {
                'uid': int(row['id_usuario']),
                'nombre': row['nombre_rutina'],
                'ej': int(row['id_ejercicio']),
                'series': int(row['cantidad_series']),
                'reps': int(row['cantidad_repeticiones']),
                'orden': int(row['orden_ejercicio'])
            })

        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO registro_serie (id_registro_serie, id_sesion, id_ejercicio, numero_serie, repeticiones_logradas, peso_levantado_kg, rpe)
                VALUES (:id, :sid, :ej, :nserie, :reps, :peso, :rpe)
                ON CONFLICT DO NOTHING
            """), {
                'id': int(row['id_registro_serie']),
                'sid': int(row['id_sesion']),
                'ej': int(row['id_ejercicio']),
                'nserie': int(row['numero_serie']),
                'reps': int(row['repeticiones_logradas']),
                'peso': float(row['peso_levantado_kg']),
                'rpe': int(row['rpe'])
            })

        conn.commit()
    logging.info(f'rutinas cargadas: {len(df)} registros')
    print(f'[OK] rutinas cargadas: {len(df)} registros')

def cargar_errores(engine):
    archivos = {
        'ejercicios': 'data/errors/ejercicios_errores.csv',
        'usuarios': 'data/errors/usuarios_errores.csv',
        'rutinas': 'data/errors/rutinas_errores.csv',
    }

    total = 0
    with engine.connect() as conn:
        for origen, path in archivos.items():
            if not os.path.exists(path):
                continue
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                motivo = row.get('motivo_error', 'Sin especificar')
                conn.execute(text("""
                    INSERT INTO registros_error (origen, datos_originales, motivo_error)
                    VALUES (:origen, :datos, :motivo)
                """), {
                    'origen': origen,
                    'datos': row.to_json(),
                    'motivo': motivo
                })
                logging.warning(f'[{origen}] Error registrado: {motivo}')
                total += 1
        conn.commit()

    logging.info(f'=== registros_error cargados: {total} ===')
    print(f'[OK] errores cargados: {total} registros')

if __name__ == '__main__':
    logging.info('=== Inicio proceso de carga ===')
    engine = get_engine()
    crear_tablas(engine)
    cargar_ejercicios(engine)
    cargar_usuarios(engine)
    cargar_rutinas(engine)
    cargar_errores(engine)
    logging.info('=== Carga finalizada ===')
    print('\nCarga completada')