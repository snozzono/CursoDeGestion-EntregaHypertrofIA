# 🏋️ HypertrophIA — Pipeline de Datos

Pipeline de ingeniería de datos para un motor de IA especializado en musculación. Procesa catálogos de ejercicios, usuarios y rutinas a través de cuatro etapas secuenciales bajo principios DataOps.

**Proyecto:** ITY1101 Gestión de Datos para IA — DuocUC  
**Integrantes:** Francisco Salazar · Gabriel Durán · Martin Higuera  
**Profesor:** Héctor Andrés Morel Briones

---

## Estructura del proyecto

```
hypertrophia/
├── src/
│   ├── 1_ingest.py          # Etapa 1: Ingesta
│   ├── 2_transform.py       # Etapa 2: Limpieza y transformación
│   ├── 3_validate.py        # Etapa 3: Validación estructural y semántica
│   ├── 4_load.py            # Etapa 4: Carga a PostgreSQL
│   └── pipeline.py          # Ejecutor secuencial del pipeline completo
├── data/
│   ├── raw/                 # CSVs fuente + copias _raw generadas en ingesta
│   ├── processed/           # CSVs limpios y validados (generado en ejecución)
│   └── errors/              # Registros rechazados con motivo (generado en ejecución)
├── logs/                    # Bitácoras por etapa (generado en ejecución)
│   ├── ingest.log
│   ├── transform.log
│   ├── validation.log
│   └── load_database.log
├── HypertrophIA_Pipeline.ipynb  # Notebook de documentación y demo
├── docker-compose.yml       # PostgreSQL local en contenedor
├── Dockerfile               # Containerización del pipeline
├── .env                     # Variables de entorno (no subir a git)
├── .gitignore
└── requirements.txt
```

---

## Requisitos

- Python 3.11+
- Docker Desktop (para BD local)

```bash
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

### Opción A — PostgreSQL local (Docker)

Levanta el contenedor:

```bash
docker compose up -d
```

`.env`:
```
DB_URL=postgresql://hypertrophia:hypertrophia123@localhost:5432/hypertrophia
```

### Opción B — Supabase (nube)

Crea un proyecto en [supabase.com](https://supabase.com), ve a **Connect → Transaction pooler** y copia la URI.

`.env`:
```
DB_URL=postgresql://postgres.<project-id>:<password>@aws-1-<region>.pooler.supabase.com:6543/postgres
```

---

## Ejecución

### Pipeline completo

```bash
python src/pipeline.py
```

### Por etapa

```bash
python src/1_ingest.py
python src/2_transform.py
python src/3_validate.py
python src/4_load.py
```

---

## Etapas del pipeline

### Etapa 1 — Ingesta (`1_ingest.py`)

Copia los archivos fuente a versiones `_raw` dejando los originales intactos. Registra tamaño y trazabilidad en `logs/ingest.log`.

```
[OK] ejercicios.csv -> ejercicios_raw.csv (1046 bytes)
[OK] usuarios.csv -> usuarios_raw.csv (1139 bytes)
[OK] rutinas.csv -> rutinas_raw.csv (1242 bytes)
Ingesta completada: 3/3 archivos
```

### Etapa 2 — Limpieza y Transformación (`2_transform.py`)

- Elimina duplicados exactos
- Normaliza `NULL` string y celdas vacías a `NaN`
- Elimina filas sin campos obligatorios
- Convierte tipos de datos (numéricos, fechas) con `errors='coerce'`
- Loguea IDs eliminados por etapa

```
[-] dropna nombre/musculo: 2 eliminados | IDs: [11, 13]
[-] coercion numerica: 1 eliminados | IDs: [14]
[OK] ejercicios: 15 -> 12 registros
[-] dropna nombre/correo: 1 eliminados | IDs: [9]
[-] coercion numerica/fecha: 1 eliminados | IDs: [12]
[OK] usuarios: 13 -> 11 registros
[-] dropna nombre_rutina: 1 eliminados | IDs: [13]
[-] coercion numerica/fecha: 2 eliminados | IDs: [10, 12]
[OK] rutinas: 13 -> 10 registros
```

### Etapa 3 — Validación Estructural y Semántica (`3_validate.py`)

Aplica reglas de negocio. Registros inválidos se desvían a `data/errors/` con motivo detallado.

| Dataset | Campo | Regla |
|---------|-------|-------|
| ejercicios | `porcentaje_estimulo` | Entre 0 y 100 |
| ejercicios | `dificultad` | Entre 1 y 5 |
| usuarios | `edad` | Entre 14 y 100 |
| usuarios | `peso_corporal_kg` | Entre 30 y 300 |
| usuarios | `estatura_cm` | Entre 100 y 250 |
| usuarios | `correo_electronico` | Formato válido (regex) |
| rutinas | `repeticiones_logradas` | Mayor a 0 |
| rutinas | `peso_levantado_kg` | Entre 0 y 500 |
| rutinas | `rpe` | Entre 1 y 10 |
| rutinas | `id_usuario` | Debe existir en usuarios válidos |

```
[OK] ejercicios -> válidos: 11 | rechazados: 1
  [X] id=12 | porcentaje_estimulo=999.9 fuera de rango [0-100]
[OK] usuarios -> válidos: 9 | rechazados: 2
  [X] id=10 | email="correo-invalido" formato inválido
  [X] id=11 | edad=-5 fuera de rango [14-100]
[OK] rutinas -> válidas: 8 | rechazadas: 2
  [X] id=9 | id_usuario=99 no existe en usuarios válidos
  [X] id=11 | repeticiones_logradas=-3 debe ser > 0
```

### Etapa 4 — Carga a PostgreSQL (`4_load.py`)

Normaliza y carga los datos validados en 14 tablas relacionales. Usa `ON CONFLICT DO NOTHING` para idempotencia. Registros rechazados se persisten en `registros_error`.

```
[OK] Tablas verificadas
[OK] ejercicios cargados: 11 registros
[OK] usuarios cargados: 9 registros
[OK] rutinas cargadas: 8 registros
[OK] errores cargados: 5 registros
Carga completada
```

#### Tablas generadas

| Grupo | Tablas |
|-------|--------|
| Catálogo | `grupo_muscular`, `musculo`, `tipo_ejercicio`, `equipamiento`, `ejercicio` |
| Usuarios | `pais`, `sexo_usuario`, `usuario`, `caracteristicas_fisicas_usuario` |
| Rutinas | `enfoque`, `rutina`, `detalle_rutina`, `sesion_entrenamiento`, `registro_serie` |
| Auditoría | `registros_error` |

---

## Datasets

| Archivo | Filas | Errores intencionales |
|---------|-------|----------------------|
| `ejercicios.csv` | 15 | nombre vacío, porcentaje imposible, NULL string, dificultad string, duplicado |
| `usuarios.csv` | 13 | nombre vacío, email inválido, edad negativa, peso imposible + fecha mal formato, duplicado |
| `rutinas.csv` | 13 | usuario inexistente, fecha mal formato, repeticiones negativas, peso string, nombre vacío |

---

## Logs

Cada etapa genera su bitácora en `logs/`:

| Archivo | Contenido |
|---------|-----------|
| `ingest.log` | Archivos copiados, tamaños, errores de lectura |
| `transform.log` | IDs eliminados por etapa y motivo |
| `validation.log` | IDs rechazados con motivo detallado por regla |
| `load_database.log` | Registros insertados por tabla, errores de BD |

---

## Docker

### BD local

```bash
docker compose up -d    # Levantar
docker compose down     # Detener
docker ps               # Verificar estado
```

### Pipeline containerizado

```bash
docker build -t hypertrophia .
docker run --env-file .env hypertrophia
```

---

## .gitignore

```
.env
logs/
data/processed/
data/errors/
__pycache__/
*.pyc
```