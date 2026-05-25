# HypertrophIA — Pipeline de Datos

Pipeline de ingeniería de datos para un motor de IA especializado en musculación. Procesa un catálogo de ejercicios con base científica a través de cuatro etapas secuenciales: ingesta, limpieza/transformación, validación y carga a PostgreSQL.

**Proyecto:** ITY1101 Gestión de Datos para IA — DuocUC  
**Integrantes:** Francisco Salazar · Gabriel Durán · Martin Higuera

---

## Estructura del proyecto

```
hypertrophia/
├── src/
│   ├── 1_ingest.py          # Etapa 1: Ingesta
│   ├── 2_transform.py       # Etapa 2: Limpieza y transformación
│   ├── 3_validate.py        # Etapa 3: Validación estructural y semántica
│   └── 4_load.py            # Etapa 4: Carga a PostgreSQL
├── data/
│   ├── raw/
│   │   └── ejercicios.csv   # Dataset fuente
│   └── processed/           # Generado en tiempo de ejecución
├── logs/                    # Generado en tiempo de ejecución
├── docker-compose.yml       # PostgreSQL en contenedor
├── Dockerfile               # Containerización del pipeline
├── .env                     # Variables de entorno (no subir a git)
├── .gitignore
└── requirements.txt
```

---

## Requisitos

- Python 3.11+
- Docker Desktop

```
pip install -r requirements.txt
```

`requirements.txt`:
```
pandas
sqlalchemy
psycopg2-binary
python-dotenv
```

---

## Configuración

### 1. Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hypertrophia
DB_USER=hypertrophia
DB_PASSWORD=hypertrophia123
```

### 2. Levantar la base de datos

```bash
docker compose up -d
```

Verificar que el contenedor esté corriendo:

```bash
docker ps
```

---

## Ejecución del pipeline

Cada etapa se ejecuta de forma independiente desde la raíz del proyecto:

```bash
python src/1_ingest.py
python src/2_transform.py
python src/3_validate.py
python src/4_load.py
```

### Etapa 1 — Ingesta (`1_ingest.py`)

Copia el archivo fuente `data/raw/ejercicios.csv` a `data/raw/ejercicios_raw.csv` dejando el original intacto. Registra la operación en `logs/ingest.log`.

**Output esperado:**
```
[OK] Ingesta completada -> data/raw/ejercicios_raw.csv
```

### Etapa 2 — Limpieza y Transformación (`2_transform.py`)
> 🚧 En desarrollo

- Elimina duplicados
- Reemplaza strings `'NULL'` y campos vacíos por `NaN`
- Elimina filas sin `nombre` o `grupo_muscular_primario`
- Rellena columnas opcionales con valores por defecto
- Parsea rangos (`"3-4"`, `"8-12"`) extrayendo el valor mínimo
- Calcula `volumen_total = series_min * repeticiones_min`
- Exporta a `data/processed/ejercicios_clean.csv`

### Etapa 3 — Validación (`3_validate.py`)
> 🚧 En desarrollo

- Validación estructural: tipos de datos, formatos
- Validación semántica: rangos lógicos de negocio
- Separa registros válidos (`ejercicios_validos.csv`) e inválidos (`ejercicios_invalidos.csv`)
- Registra observaciones en `logs/validation.log`

### Etapa 4 — Carga (`4_load.py`)
> 🚧 En desarrollo

- Conecta a PostgreSQL vía SQLAlchemy
- Crea tablas `ejercicios_clean` y `ejercicios_error` si no existen
- Inserta registros válidos e inválidos en sus respectivas tablas
- Registra la operación en `logs/load_database.log`

---

## Logs

Cada etapa genera su propio log en la carpeta `logs/`:

| Archivo | Etapa |
|---|---|
| `ingest.log` | Ingesta |
| `transform.log` | Limpieza y transformación |
| `validation.log` | Validación |
| `load_database.log` | Carga a base de datos |

---

## Dataset

**Archivo:** `ejercicios.csv`  
**Filas:** 15 registros  
**Columnas:** `id, nombre, grupo_muscular_primario, grupo_muscular_secundario, tipo, nivel_dificultad, equipo_requerido, series_recomendadas, repeticiones_recomendadas, descanso_segundos, fuente_cientifica, notas`

**Problemas conocidos en el dataset fuente:**

| id | Problema |
|---|---|
| 13 | `nombre` vacío — registro eliminado en limpieza |
| 4 | `series_recomendadas` vacío — eliminado en limpieza |
| 8 | `grupo_muscular_secundario` = `'NULL'` string — normalizado |
| 12 | `descanso_segundos` vacío — se mantiene como `NaN` |
| 7, 15 | `fuente_cientifica` vacía — rellena con `'Sin referencia'` |

---

## Docker

### Base de datos (PostgreSQL)

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    container_name: hypertrophia_db
    environment:
      POSTGRES_USER: hypertrophia
      POSTGRES_PASSWORD: hypertrophia123
      POSTGRES_DB: hypertrophia
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
```

### Pipeline

El `Dockerfile` containeriza los scripts del pipeline:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY data/ ./data/
COPY .env .
RUN mkdir -p logs data/processed
CMD ["python", "src/1_ingest.py"]
```

---

## .gitignore

```
.env
logs/
data/processed/
__pycache__/
*.pyc
```
