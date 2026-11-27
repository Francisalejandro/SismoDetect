# Informe: estructura inicial del proyecto SismoDetect

> **Documento histórico.** Este informe describe la organización inicial del proyecto el **2026-11-17**, cuando todavía no existían apps Django funcionales, migraciones aplicadas ni integración con PostgreSQL. Se conserva como registro de las decisiones de estructura y **no representa el estado actual**. El estado vigente está en `documentacion/INFORME_IMPLEMENTACION.md`.

**Fecha:** 2026-11-17 (ajustes menores: misma fecha)
**Fase:** organización inicial (sin implementación funcional)

### Registro de ajustes menores (fase 2)

- Se reorganizó `requirements/`: `dev.txt` ya no arrastra TensorFlow y
  se añadió `dev-ia.txt` para el entorno de desarrollo con IA.
- Se reservó `ia/pesos/cnn_v1/` para los futuros pesos de la CNN V1.
- Se documentó el preprocesamiento de la CNN V1 (sección 4.1).

### Registro de auditoría final

- Corregido el uso de `requirements/tensorflow.txt`: es para Django
  junto con la CNN/IA; Django sin IA usa `requirements/base.txt`
  (también actualizado el comentario del archivo y el `README.md`).
- Corregida la decisión 5: el preprocesamiento se compone por modelo;
  **no** existe un pipeline único obligatorio para todos los modelos
  (consistente con la sección 4.1).
- Ampliada `.gitignore` con formatos de pesos de futuros Transformers
  (`*.onnx`, `*.pt`, `*.pth`, `*.safetensors`).

---

## 1. Carpetas y archivos creados

### Generados con `django-admin startproject config .`

| Archivo | Descripción |
|---|---|
| `manage.py` | Utilidad de línea de comandos de Django, apunta a `config.settings`. |
| `config/__init__.py` | Marca `config` como paquete Python. |
| `config/settings.py` | Configuración base de Django generada por defecto (sin modificar). |
| `config/urls.py` | Enrutado raíz (aún sin rutas de la aplicación). |
| `config/wsgi.py` / `config/asgi.py` | Puntos de entrada para servidores WSGI/ASGI. |

### Creados manualmente

| Ruta | Descripción |
|---|---|
| `apps/__init__.py` | Paquete para las futuras aplicaciones de Django. |
| `ia/__init__.py` | Paquete raíz de los componentes de IA. |
| `ia/modelos/__init__.py` | Paquete de definiciones de arquitecturas de modelos. |
| `ia/procesamiento/__init__.py` | Paquete de preprocesamiento de señales. |
| `ia/inferencia/__init__.py` | Paquete del motor de inferencia. |
| `ia/gestor_modelos/__init__.py` | Paquete del gestor centralizado de modelos. |
| `data/entrada/.gitkeep` | Conserva la carpeta de datos de entrada en Git. |
| `data/temporal/.gitkeep` | Conserva la carpeta de datos temporales en Git. |
| `documentacion/INFORME_ESTRUCTURA_INICIAL.md` | Este informe. |
| `tests/__init__.py` | Paquete de pruebas. |
| `requirements/base.txt` | Dependencias básicas. |
| `requirements/tensorflow.txt` | Dependencias de IA (incluye `base.txt`). |
| `requirements/dev.txt` | Herramientas generales de desarrollo y pruebas (incluye `base.txt`). |
| `requirements/dev-ia.txt` | Desarrollo y pruebas con IA (incluye `tensorflow.txt` y `dev.txt`). |
| `README.md` | Presentación del proyecto. |
| `.gitignore` | Reglas de exclusión para Git. |

Todos los `__init__.py` incluyen un docstring que explica el propósito
previsto del paquete, para que sirvan de guía arquitectónica sin
implementar código.

---

## 2. Para qué sirve cada carpeta

- **`config/`** — Configuración general del proyecto Django: settings,
  URLs raíz y puntos de entrada de despliegue. No contiene lógica de la
  aplicación.
- **`apps/`** — Aplicaciones funcionales de Django (por ejemplo
  `apps.catalogacion`, `apps.api`). Cada app vivirá como subpaquete.
- **`ia/`** — Componentes de inteligencia artificial **independientes de
  Django**, organizados en cuatro subpaquetes:
  - **`ia/modelos/`** — Definición de arquitecturas (CNN V1, futuros
    Transformers). Cada modelo expondrá una interfaz común.
  - **`ia/pesos/`** — Artefactos (pesos) entrenados de los modelos. Cada
    versión del modelo dispone de su propia subcarpeta
    (actualmente reservada: `ia/pesos/cnn_v1/`). Los pesos **no** se
    suben al repositorio (ver `.gitignore`) y todavía **no** se han
    copiado al proyecto.
  - **`ia/procesamiento/`** — Preprocesamiento de señales: filtrado,
    normalización, generación de espectrogramas. Funciones puras
    reutilizables.
  - **`ia/inferencia/`** — Ejecución de predicciones con el modelo activo
    y normalización del resultado (clase, confianza, metadatos).
  - **`ia/gestor_modelos/`** — Registro de modelos disponibles, selección
    del modelo activo y carga de pesos.
- **`data/entrada/`** — Señales y archivos que el usuario ingresa al sistema.
- **`data/temporal/`** — Archivos temporales generados durante el
  procesamiento (purgables).
- **`documentacion/`** — Documentación general y técnica del proyecto.
- **`tests/`** — Pruebas con pytest + pytest-django.

---

## 3. Cómo se relacionan los módulos

Flujo previsto de una inferencia (a implementar en fases posteriores):

```
Django (apps/*)          IA (independiente de Django)
┌────────────────┐   ┌─────────────────────────────────────────────┐
│ Vista / API    │   │  ia.inferencia                              │
│   │            │   │    │  pide el modelo activo                 │
│   ▼            │   │    ▼                                        │
│ Capa de        │──▶│  ia.gestor_modelos                          │
│ servicios      │   │    │  devuelve una instancia con interfaz   │
│ (fina)         │   │    ▼  común (cargar / predecir)             │
└────────────────┘   │  ia.modelos  (CNN V1, Transformers…)        │
                     │    ▲  usa arquitecturas registradas         │
                     │    │                                        │
                     │  ia.procesamiento                           │
                     │    └─ prepara la señal cruda de data/entrada│
                     └─────────────────────────────────────────────┘
```

Principios de la relación:

1. **`apps/` no importa TensorFlow directamente.** Las apps de Django
   llamarán a una capa fina de servicios que delega en `ia/`. Así la IA
   puede probarse sin levantar Django y Django no conoce el backend de IA.
2. **`ia/inferencia` depende de `ia/gestor_modelos`**, nunca de un modelo
   concreto: obtiene "el modelo activo" y le pide predicciones.
3. **`ia/gestor_modelos` depende de `ia/modelos`** a través de un registro
   de modelos (patrón *registry*), no de clases concretas.
4. **`ia/procesamiento` es común a todos los modelos**: al agregar una
   nueva clase de señal o arquitectura, el preprocesamiento existente no
   se modifica; solo se agregan pasos nuevos si son necesarios.

---

## 4. Decisiones de arquitectura

1. **Proyecto Django generado con `django-admin startproject config .`**
   en la raíz (no dentro de una subcarpeta extra), usando el
   `django-admin.exe` del propio `.venv`. Esto garantiza archivos estándar
   y compatibles con Django 6.1.3 sin asumir que el proyecto ya existía.
2. **`config/` como paquete de configuración** en lugar del clásico
   nombre del proyecto: separa claramente configuración de funcionalidad
   y facilita que `apps/` e `ia/` vivan al mismo nivel.
3. **IA fuera de Django (`ia/`):** los componentes de IA son paquetes
   Python normales. Esto permite:
   - Probar y ejecutar la IA sin Django.
   - Sustituir el framework web sin tocar la lógica de IA.
   - Evitar que las migraciones de Django dependan de TensorFlow.
4. **`gestor_modelos` como punto único de acceso a los modelos** (patrón
   registro + carga perezosa): incorporar la CNN V1 hoy y Transformers
   mañana consistirá en registrar el nuevo modelo; el resto del sistema
   no cambia. Es la respuesta directa al requisito de extensibilidad.
5. **Preprocesamiento como funciones puras y reutilizables** para que
   cada modelo compose su propio pipeline con los pasos que necesite
   (ver sección 4.1: cada arquitectura puede tener su propio pipeline y
   no se comparte por defecto entre modelos).
6. **No se crearon módulos vacíos innecesarios:** solo existen los
   `__init__.py` que convierten las carpetas en paquetes (con docstrings
   orientativos) y los `.gitkeep` para preservar `data/` en Git.
7. **Ajuste respecto a la propuesta original:** se subdividió `data/` en
   `data/entrada/` y `data/temporal/`, porque el manejo y la limpieza de
   archivos temporales difiere del de las señales de entrada del usuario;
   y `requirements/` se organizó con archivos encadenados (`-r`) para
   evitar duplicar versiones.

### 4.1 Preprocesamiento de la CNN V1 (especificación reservada)

La CNN V1 ya entrenada fue construida sobre un preprocesamiento
específico que **debe respetarse tal cual** cuando se implemente el
pipeline de `ia/procesamiento/`:

| Aspecto | Especificación |
|---|---|
| Componente DC | Se elimina **por segmento y por canal** (no globalmente). |
| Normalización | Estadísticas (media/desviación) **globales calculadas exclusivamente con los datos de Train**. |
| Aplicación de estadísticas | Las **mismas estadísticas de Train** se aplican a validación, prueba e inferencia. Nunca se recalculan con otros datos. |
| Forma de entrada | **3000 muestras × 3 canales** (Z, N, E — orientación ZNE). |
| Frecuencia de muestreo | **100 Hz**. |

Advertencias importantes:

- **No se deben sustituir estos pasos por un preprocesamiento genérico**
  (por ejemplo, normalizar cada segmento por sus propias estadísticas o
  usar estadísticas de todo el conjunto): alteraría la distribución con
  la que la red fue entrenada y degradaría las predicciones.
- Cada futuro modelo (por ejemplo, un Transformer) podrá disponer de su
  **propio pipeline de preprocesamiento**; los pipelines no se comparten
  por defecto entre arquitecturas. El diseño de `ia/procesamiento/`
  (funciones puras reutilizables) permite que un modelo nuevo reutilice
  un paso solo si su especificación coincide.

---

## 5. Dependencias separadas

| Archivo | Contenido |
|---|---|
| `requirements/base.txt` | `Django==6.1.3` (fijado a la versión ya presente en `.venv`). |
| `requirements/tensorflow.txt` | `-r base.txt` + `tensorflow==2.21.0` (fijado a `.venv`). |
| `requirements/dev.txt` | `-r base.txt` + herramientas generales de desarrollo y pruebas **sin fijar** (pytest, pytest-django, pytest-cov, ruff). No incluye TensorFlow. |
| `requirements/dev-ia.txt` | `-r tensorflow.txt` + `-r dev.txt`: entorno completo de desarrollo y pruebas con IA. No duplica ninguna dependencia: reutiliza los archivos anteriores mediante `-r`. |

Encadenamiento (`-r`) entre archivos:

```
dev-ia.txt ─┬─▶ tensorflow.txt ──▶ base.txt
            └─▶ dev.txt ─────────▶ base.txt
```

Notas:

- **No se instaló ningún paquete** ni se modificó el entorno virtual; los
  archivos solo documentan las dependencias.
- Las herramientas de desarrollo no están fijadas todavía; se fijarán con
  `pip freeze` cuando se decida instalarlas.
- `.venv/` está excluido en `.gitignore` y **no** se sube al repositorio.
- Uso típico:
  - Solo Django (backend sin IA): `pip install -r requirements/base.txt`
  - Django junto con CNN/IA (ejecución): `pip install -r requirements/tensorflow.txt`
  - Desarrollo y pruebas sin TensorFlow: `pip install -r requirements/dev.txt`
  - Desarrollo y pruebas completos (Django + IA): `pip install -r requirements/dev-ia.txt`

---

## 6. Archivos existentes conservados

Antes de crear nada se inspeccionó la carpeta. Solo existía:

| Elemento | Estado |
|---|---|
| `.idea/` | **Conservado sin modificar** (configuración de PyCharm). Excluido del repositorio en `.gitignore`. |
| `.venv/` | **Conservado sin modificar** (no se instaló ni desinstaló nada). Excluido del repositorio en `.gitignore`. |

No había ningún archivo propio del proyecto, por lo que no se
sobrescribió ni eliminó nada.

---

## 7. Elementos todavía no implementados

- Aplicaciones de Django dentro de `apps/` (modelos, vistas, migraciones).
- Rutas en `config/urls.py` (queda con la configuración por defecto).
- Definición de la arquitectura CNN V1 en `ia/modelos/`.
- **Pesos de la CNN V1: aún no se copian al proyecto.** Ya está reservada
  su ubicación en `ia/pesos/cnn_v1/`.
- Pipeline de preprocesamiento en `ia/procesamiento/` (cuando se
  implemente, deberá seguir la especificación de la sección 4.1).
- Motor de inferencia en `ia/inferencia/`.
- Registro y selección de modelos en `ia/gestor_modelos/`.
- Interfaz común de modelos (clase base / protocolo).
- Pruebas en `tests/`.
- Categorías de señales sísmicas: no se ha definido el catálogo de clases,
  lo que se hará al integrar la CNN V1 (su capa de salida define las
  clases actuales).
- Configuración de producción (variables de entorno, `ALLOWED_HOSTS`, etc.).

---

## 8. Posibles mejoras futuras

1. **Interfaz común de modelos** (`ia/modelos/base.py`): clase base o
   protocolo `cargar()` / `predecir()` que unificará CNN y Transformers.
2. **Catálogo de clases configurable** (archivo de configuración o
   tabla en base de datos) en lugar de etiquetas fijas en el código, para
   agregar clases sin reescribir la inferencia.
3. **Registro declarativo de modelos**: los modelos se autoregistran en
   `gestor_modelos` mediante un decorador; el modelo activo se define en
   settings.
4. **Configuración por entornos** en `config/settings/` (`base.py`,
   `development.py`, `production.py`) y lectura de secretos con variables
   de entorno.
5. **Versionado de modelos** en disco (`ia/pesos/cnn_v1/…`) con un
   manifiesto (versión, fecha, métricas) para trazabilidad.
6. **Tarea asíncrona para inferencia** (hilo de fondo o cola) si las
   predicciones resultan lentas, sin bloquear la interfaz.
7. **CI básica** (lint con ruff + pytest) cuando se instalen las
   dependencias de desarrollo.
8. **Conversión de la CNN V1 a TensorFlow Lite** si se requiere
   despliegue ligero en equipos de recursos limitados.

---

## 9. Árbol completo de la estructura final

```
SismoDetect/
├── .gitignore
├── README.md
├── manage.py
├── apps/
│   └── __init__.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── data/
│   ├── entrada/
│   │   └── .gitkeep
│   └── temporal/
│       └── .gitkeep
├── documentacion/
│   └── INFORME_ESTRUCTURA_INICIAL.md
├── ia/
│   ├── __init__.py
│   ├── gestor_modelos/
│   │   └── __init__.py
│   ├── inferencia/
│   │   └── __init__.py
│   ├── modelos/
│   │   └── __init__.py
│   ├── pesos/
│   │   ├── __init__.py
│   │   └── cnn_v1/
│   │       └── .gitkeep      (ubicación reservada; pesos aún no copiados)
│   └── procesamiento/
│       └── __init__.py
├── requirements/
│   ├── base.txt
│   ├── dev-ia.txt
│   ├── dev.txt
│   └── tensorflow.txt
├── tests/
│   └── __init__.py
├── .idea/          (existente, conservado, excluido de Git)
└── .venv/          (existente, conservado, excluido de Git)
```
