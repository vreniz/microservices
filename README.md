# Guía de Inicialización del Proyecto de Microservicios

## Paso 1: Crear la estructura base del proyecto
Crea el directorio raíz e inicializa los microservicios usando **`uv`**.

```bash
# Crear y entrar a la carpeta principal
mkdir booking
cd booking

# Inicializar cada microservicio
uv init user-service
uv init resources-service
uv init payments-service
uv init notifications-service
uv init booking-service
```

---

## Paso 2: Configurar dependencias en `user-service`
Entra al servicio de usuarios e instala los paquetes necesarios para la API, el ORM, las migraciones y los drivers de la base de datos (PostgreSQL).

```bash
cd user-service

# Instalar dependencias base
uv add "fastapi[standard]" sqlmodel alembic python-dotenv

# Instalar el driver moderno para PostgreSQL (Psycopg 3)
uv add psycopg psycopg-binary
```

### Configuración final del archivo `pyproject.toml`
Para evitar errores si eliminaste o modificaste archivos de empaquetado por defecto como `__init__.py`, añade la regla `package = false`. Tu archivo debe lucir exactamente así:

```toml
[project]
name = "user-service"
version = "0.1.0"
description = "Microservicio de usuarios"
readme = "README.md"
authors = [
    { name = "vreniz", email = "vreniz@uninorte.edu.co" }
]
requires-python = ">=3.12"
dependencies = [
    "alembic>=1.20.0",
    "fastapi[standard]>=0.156.8",
    "psycopg>=3.3.6",
    "psycopg-binary>=3.3.6",
    "python-dotenv>=1.2.4",
    "sqlmodel>=0.0.48",
]

[tool.uv]
package = false
```

---

## Paso 3: Crear la estructura de arquitectura limpia
Crea la distribución de directorios siguiendo las buenas prácticas de desarrollo. **Asegúrate de incluir los archivos `__init__.py`** en las carpetas raíz del código para que Python reconozca los módulos correctamente.

```text
user-service/
├── app/
│   ├── __init__.py
│   └── src/
│       ├── __init__.py
│       ├── application/
│       ├── presentation/
│       ├── infrastructure/
│       └── domain/
│           └── models/
│               └── user_model.py
```

### Definición del Modelo de Usuario (`app/src/domain/models/user_model.py`)
```python
import datetime
import uuid
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):  
    __tablename__ = "usr_users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    identification_type: str
    identification_number: str
    birth_date: datetime.date
    is_active: bool = True
    is_superuser: bool = False
```

---

## Paso 4: Inicializar y configurar Alembic

1. **Inicializa el entorno de Alembic:**
   ```bash
   uv run alembic init alembic
   ```

2. **Configurar `alembic.ini`:**
   Busca la línea de configuración de la base de datos y añade tu cadena de conexión (ejemplo usando **Neon** con *connection pooling*).
   ```ini
   sqlalchemy.url = "postgresql://neondb_owner:npg_xlB21mKgVdbh@ep-dawn-queen-b59hwwxy-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
   ```

3. **Modificar el entorno de ejecuciones (`alembic/env.py`):**
   Abre el archivo generado en la carpeta de alembic y edítalo para que lea las variables de entorno, registre `SQLModel` y detecte automáticamente el modelo de usuario:
   ```python
   import os
   from logging.config import fileConfig
   from alembic import context
   from sqlmodel import SQLModel

   # Importar el modelo para registrarlo en los metadatos de SQLAlchemy
   from app.src.domain.models.user_model import User

   config = context.config

   if config.config_file_name is not None:
       fileConfig(config.config_file_name)

   # Asignar los metadatos de SQLModel para el autogenerate
   target_metadata = SQLModel.metadata

   def run_migrations_offline() -> None:
       url = config.get_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
       context.configure(
           url=url,
           target_metadata=target_metadata,
           literal_binds=True,
           dialect_opts={"paramstyle": "named"},
       )
   ```

4. **Editar la plantilla de migraciones (`alembic/script.py.mako`):**
   Añade el import global de `sqlmodel` para que las futuras migraciones se generen sin errores de referencia:
   ```python
   from typing import Sequence, Union
   from alembic import op
   import sqlalchemy as sa
   import sqlmodel
   ${imports if imports else ""}
   ```

---

## Paso 5: Crear y aplicar la primera migración

Crea el archivo `.env` en la raíz de `user-service/` para las variables de entorno locales:
```text
DATABASE_URL="tu_url_de_conexion_a_base_de_datos"
```

Ejecuta los comandos de Alembic a través de `uv run` para asegurar el uso del entorno virtual correcto:

```bash
# 1. Generar la migración automáticamente detectando el modelo User
uv run alembic revision --autogenerate -m "First migration"

# 2. Aplicar la migración en la base de datos de Neon
uv run alembic upgrade head
```

*¡Listo! Puedes ingresar a tu consola de Neon para verificar que tanto la tabla de control de Alembic como tu tabla `usr_users` se hayan creado con la estructura correcta.*
