import shutil
import logging
import os

os.makedirs('logs', exist_ok=True)
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/errors', exist_ok=True)

logging.basicConfig(
    filename='logs/ingest.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ARCHIVOS = [
    'ejercicios.csv',
    'usuarios.csv',
    'rutinas.csv',
]

def ingestar():
    logging.info('=== Inicio proceso de ingesta ===')
    exitosos = 0

    for archivo in ARCHIVOS:
        origen = f'data/raw/{archivo}'
        nombre, ext = os.path.splitext(archivo)
        destino = f'data/raw/{nombre}_raw{ext}'

        if not os.path.exists(origen):
            logging.error(f'[MISSING] Archivo no encontrado: {origen}')
            print(f'[ERROR] No se encontró {origen}')
            continue

        try:
            size = os.path.getsize(origen)
            shutil.copy(origen, destino)
            logging.info(f'[OK] {archivo} copiado -> {destino} ({size} bytes)')
            print(f'[OK] {archivo} -> {nombre}_raw{ext} ({size} bytes)')
            exitosos += 1
        except Exception as e:
            logging.error(f'[FAIL] Error copiando {archivo}: {e}')
            print(f'[ERROR] {archivo}: {e}')

    logging.info(f'=== Ingesta finalizada: {exitosos}/{len(ARCHIVOS)} archivos procesados ===')
    print(f'\nIngesta completada: {exitosos}/{len(ARCHIVOS)} archivos')

if __name__ == '__main__':
    ingestar()