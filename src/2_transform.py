import pandas as pd
import logging
import os

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/transform.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_eliminados(df_antes, df_despues, etapa, archivo):
    eliminados = len(df_antes) - len(df_despues)
    if eliminados > 0:
        ids = df_antes[~df_antes.index.isin(df_despues.index)].iloc[:, 0].tolist()
        logging.warning(f'[{archivo}] {etapa}: {eliminados} registros eliminados | IDs: {ids}')
        print(f'  [-] {etapa}: {eliminados} eliminados | IDs: {ids}')

def transformar_ejercicios():
    logging.info('=== Transformación: ejercicios ===')
    df = pd.read_csv('data/raw/ejercicios_raw.csv')
    total_inicial = len(df)
    logging.info(f'[ejercicios] Registros iniciales: {total_inicial}')

    antes = df.copy()
    df = df.drop_duplicates()
    log_eliminados(antes, df, 'drop_duplicates', 'ejercicios')

    df = df.replace('NULL', pd.NA).replace('', pd.NA)

    antes = df.copy()
    df = df.dropna(subset=['nombre_ejercicio', 'nombre_musculo'])
    log_eliminados(antes, df, 'dropna nombre/musculo', 'ejercicios')

    df['dificultad'] = pd.to_numeric(df['dificultad'], errors='coerce')
    df['porcentaje_estimulo'] = pd.to_numeric(df['porcentaje_estimulo'], errors='coerce')

    antes = df.copy()
    df = df.dropna(subset=['dificultad', 'porcentaje_estimulo']).copy()
    log_eliminados(antes, df, 'coercion numerica', 'ejercicios')

    df.to_csv('data/processed/ejercicios_clean.csv', index=False)
    logging.info(f'[ejercicios] Resultado: {total_inicial} -> {len(df)} registros válidos')
    print(f'[OK] ejercicios: {total_inicial} -> {len(df)} registros')

def transformar_usuarios():
    logging.info('=== Transformación: usuarios ===')
    df = pd.read_csv('data/raw/usuarios_raw.csv')
    total_inicial = len(df)
    logging.info(f'[usuarios] Registros iniciales: {total_inicial}')

    antes = df.copy()
    df = df.drop_duplicates()
    log_eliminados(antes, df, 'drop_duplicates', 'usuarios')

    df = df.replace('NULL', pd.NA).replace('', pd.NA)

    antes = df.copy()
    df = df.dropna(subset=['nombre_usuario', 'correo_electronico'])
    log_eliminados(antes, df, 'dropna nombre/correo', 'usuarios')

    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    df['peso_corporal_kg'] = pd.to_numeric(df['peso_corporal_kg'], errors='coerce')
    df['estatura_cm'] = pd.to_numeric(df['estatura_cm'], errors='coerce')
    df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], errors='coerce')

    antes = df.copy()
    df = df.dropna(subset=['edad', 'peso_corporal_kg', 'estatura_cm', 'fecha_registro']).copy()
    log_eliminados(antes, df, 'coercion numerica/fecha', 'usuarios')

    df.to_csv('data/processed/usuarios_clean.csv', index=False)
    logging.info(f'[usuarios] Resultado: {total_inicial} -> {len(df)} registros válidos')
    print(f'[OK] usuarios: {total_inicial} -> {len(df)} registros')

def transformar_rutinas():
    logging.info('=== Transformación: rutinas ===')
    df = pd.read_csv('data/raw/rutinas_raw.csv')
    total_inicial = len(df)
    logging.info(f'[rutinas] Registros iniciales: {total_inicial}')

    antes = df.copy()
    df = df.drop_duplicates()
    log_eliminados(antes, df, 'drop_duplicates', 'rutinas')

    df = df.replace('NULL', pd.NA).replace('', pd.NA)

    antes = df.copy()
    df = df.dropna(subset=['nombre_rutina'])
    log_eliminados(antes, df, 'dropna nombre_rutina', 'rutinas')

    df['peso_levantado_kg'] = pd.to_numeric(df['peso_levantado_kg'], errors='coerce')
    df['repeticiones_logradas'] = pd.to_numeric(df['repeticiones_logradas'], errors='coerce')
    df['fecha_sesion'] = pd.to_datetime(df['fecha_sesion'], errors='coerce')
    df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'], errors='coerce')

    antes = df.copy()
    df = df.dropna(subset=['peso_levantado_kg', 'repeticiones_logradas', 'fecha_sesion']).copy()
    log_eliminados(antes, df, 'coercion numerica/fecha', 'rutinas')

    df.to_csv('data/processed/rutinas_clean.csv', index=False)
    logging.info(f'[rutinas] Resultado: {total_inicial} -> {len(df)} registros válidos')
    print(f'[OK] rutinas: {total_inicial} -> {len(df)} registros')

if __name__ == '__main__':
    logging.info('=== Inicio proceso de transformación ===')
    transformar_ejercicios()
    transformar_usuarios()
    transformar_rutinas()
    logging.info('=== Transformación finalizada ===')
    print('\nTransformación completada')