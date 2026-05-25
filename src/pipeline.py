import subprocess
import sys

scripts = [
    'src/1_ingest.py',
    'src/2_transform.py',
    'src/3_validate.py',
    'src/4_load.py',
]

for script in scripts:
    print(f'\n>>> Ejecutando {script}...')
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f'[ERROR] Falló {script}, abortando pipeline.')
        sys.exit(1)

print('\n=== Pipeline completado exitosamente ===')