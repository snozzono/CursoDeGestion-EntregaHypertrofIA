import pandas as pd
import logging
import os
import re

os.makedirs('logs', exist_ok=True)
os.makedirs('data/errors', exist_ok=True)

logging.basicConfig(
    filename='logs/validation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_rechazados(df_errores, archivo, columna_id):
    for _, row in df_errores.iterrows():
        logging.warning(f'[{archivo}] RECHAZADO id={row[columna_id]} | motivo: {row["motivo_error"]}')
        print(f'  [X] id={row[columna_id]} | {row["motivo_error"]}')

def validar_ejercicios():
    logging.info('=== Validación: ejercicios ===')
    df = pd.read_csv('data/processed/ejercicios_clean.csv')

    def get_motivo(row):
        motivos = []
        if not (0 <= row['porcentaje_estimulo'] <= 100):
            motivos.append(f'porcentaje_estimulo={row["porcentaje_estimulo"]} fuera de rango [0-100]')
        if not (1 <= row['dificultad'] <= 5):
            motivos.append(f'dificultad={row["dificultad"]} fuera de rango [1-5]')
        return ' | '.join(motivos) if motivos else None

    df['motivo_error'] = df.apply(get_motivo, axis=1)
    validos = df[df['motivo_error'].isna()].drop(columns='motivo_error').copy()
    errores = df[df['motivo_error'].notna()].copy()

    validos.to_csv('data/processed/ejercicios_validos.csv', index=False)
    errores.to_csv('data/errors/ejercicios_errores.csv', index=False)

    logging.info(f'[ejercicios] válidos: {len(validos)} | rechazados: {len(errores)}')
    print(f'[OK] ejercicios -> válidos: {len(validos)} | rechazados: {len(errores)}')
    log_rechazados(errores, 'ejercicios', 'id_ejercicio')

def validar_usuarios():
    logging.info('=== Validación: usuarios ===')
    df = pd.read_csv('data/processed/usuarios_clean.csv')

    def email_valido(correo):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', str(correo)))

    def get_motivo(row):
        motivos = []
        if not (14 <= row['edad'] <= 100):
            motivos.append(f'edad={row["edad"]} fuera de rango [14-100]')
        if not (30 <= row['peso_corporal_kg'] <= 300):
            motivos.append(f'peso={row["peso_corporal_kg"]} fuera de rango [30-300]')
        if not (100 <= row['estatura_cm'] <= 250):
            motivos.append(f'estatura={row["estatura_cm"]} fuera de rango [100-250]')
        if not email_valido(row['correo_electronico']):
            motivos.append(f'email="{row["correo_electronico"]}" formato inválido')
        return ' | '.join(motivos) if motivos else None

    df['motivo_error'] = df.apply(get_motivo, axis=1)
    validos = df[df['motivo_error'].isna()].drop(columns='motivo_error').copy()
    errores = df[df['motivo_error'].notna()].copy()

    validos.to_csv('data/processed/usuarios_validos.csv', index=False)
    errores.to_csv('data/errors/usuarios_errores.csv', index=False)

    logging.info(f'[usuarios] válidos: {len(validos)} | rechazados: {len(errores)}')
    print(f'[OK] usuarios -> válidos: {len(validos)} | rechazados: {len(errores)}')
    log_rechazados(errores, 'usuarios', 'id_usuario')

def validar_rutinas():
    logging.info('=== Validación: rutinas ===')
    df = pd.read_csv('data/processed/rutinas_clean.csv')
    usuarios_validos = pd.read_csv('data/processed/usuarios_validos.csv')
    ids_validos = set(usuarios_validos['id_usuario'].tolist())

    def get_motivo(row):
        motivos = []
        if row['repeticiones_logradas'] <= 0:
            motivos.append(f'repeticiones_logradas={row["repeticiones_logradas"]} debe ser > 0')
        if not (0 <= row['peso_levantado_kg'] <= 500):
            motivos.append(f'peso_levantado_kg={row["peso_levantado_kg"]} fuera de rango [0-500]')
        if not (1 <= row['rpe'] <= 10):
            motivos.append(f'rpe={row["rpe"]} fuera de rango [1-10]')
        if row['id_usuario'] not in ids_validos:
            motivos.append(f'id_usuario={row["id_usuario"]} no existe en usuarios válidos')
        return ' | '.join(motivos) if motivos else None

    df['motivo_error'] = df.apply(get_motivo, axis=1)
    validos = df[df['motivo_error'].isna()].drop(columns='motivo_error').copy()
    errores = df[df['motivo_error'].notna()].copy()

    validos.to_csv('data/processed/rutinas_validas.csv', index=False)
    errores.to_csv('data/errors/rutinas_errores.csv', index=False)

    logging.info(f'[rutinas] válidas: {len(validos)} | rechazadas: {len(errores)}')
    print(f'[OK] rutinas -> válidas: {len(validos)} | rechazadas: {len(errores)}')
    log_rechazados(errores, 'rutinas', 'id_registro_serie')

if __name__ == '__main__':
    logging.info('=== Inicio proceso de validación ===')
    validar_ejercicios()
    validar_usuarios()
    validar_rutinas()
    logging.info('=== Validación finalizada ===')
    print('\nValidación completada')