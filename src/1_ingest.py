import shutil
import logging
import os
from datetime import datetime

# Directorios
os.makedirs('logs', exist_ok=True)
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

logging.basicConfig(
    filename='logs/ingest.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ORIGEN = 'data/raw/ejercicios.csv'
DESTINO = 'data/raw/ejercicios_raw.csv'

def ingestar():
    logging.info('Inicio del proceso de ingesta')

    if not os.path.exists(ORIGEN):
        logging.error(f'Archivo origen no encontrado: {ORIGEN}')
        raise FileNotFoundError(f'No se encontró {ORIGEN}')

    try:
        shutil.copy(ORIGEN, DESTINO)
        logging.info(f'Archivo copiado de {ORIGEN} a {DESTINO}')
        print(f'[OK] Ingesta completada -> {DESTINO}')
    except Exception as e:
        logging.error(f'Error en ingesta: {e}')
        raise

if __name__ == '__main__':
    ingestar()