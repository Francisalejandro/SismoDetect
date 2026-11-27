# AUDITORÍA FASE 0 — SismoDetect

> **Documento histórico.** Esta auditoría se realizó el **2026-11-25** y refleja el estado del proyecto en esa fecha: sin apps Django funcionales, sin integración real con PostgreSQL y con 0 migraciones aplicadas. Se conserva como registro del punto de partida y **no representa el estado actual** de SismoDetect. El estado vigente está en `documentacion/INFORME_IMPLEMENTACION.md`.

**Sistema web para la consulta, análisis y explicabilidad de eventos sísmicos en Cuba mediante inteligencia artificial**

| Campo | Valor |
|---|---|
| Fecha de auditoría | 2026-11-25 |
| Fase | Fase 0 — Auditoría integral previa a la implementación |
| Modo | **Solo lectura**. Sin modificaciones, instalaciones, migraciones, descargas ni entrenamiento |
| Proyecto auditado | `D:\Escuela\Inteligencia Artificial\SismoDetect` |
| Resultado | Esqueleto técnico bien organizado; CNN V1 íntegra; PostgreSQL disponible pero no integrado; aplicación funcional aún inexistente |

> **Declaración de alcance:** durante la auditoría no se creó, modificó, renombró ni eliminó ningún archivo del proyecto. No se instalaron dependencias, no se ejecutaron migraciones, no se descargaron señales, no se creó ninguna base de datos y no se modificaron los artefactos de la CNN. Las comprobaciones ejecutadas fueron `manage.py check`, `manage.py check --deploy`, `showmigrations`, lectura de archivos, verificación de hashes y una carga de modelo en memoria para comprobar su integridad. La única escritura autorizada es la creación de este informe.

---

## 1. Resumen ejecutivo

SismoDetect se encuentra en un estado de **esqueleto técnico**: la estructura de carpetas, la configuración base de Django, la documentación y los artefactos de la CNN V1 están presentes y son coherentes; sin embargo, **no existe todavía ninguna funcionalidad de aplicación**: no hay apps Django, modelos, vistas, formularios, plantillas, archivos estáticos, cliente FDSN, lector MiniSEED, pipeline de IA ni interfaz web.

La buena noticia es que **no hace falta reconstruir el proyecto**. La separación actual entre `config/`, `apps/` e `ia/` es compatible con la arquitectura objetivo. Lo que falta es implementar sobre esa base, no reemplazarla.

### 1.1 Lo que sí está listo

- Proyecto Django 6.1.3 con `manage.py check` sin incidencias.
- Estructura `config/`, `apps/`, `ia/`, `data/`, `tests/`, `requirements/` y `documentacion/`.
- CNN V1 completa: 7/7 archivos solicitados presentes; **6/6 hashes SHA-256 correctos**.
- Modelo cargable: entrada `(None, 3000, 3)`, salida `(None, 1)`, 44 705 parámetros.
- Umbral congelado verificado: `0.2927532196044922`.
- Estadísticas de normalización congeladas verificadas en `estadisticas_normalizacion.npz`.
- PostgreSQL 18.7 instalado y en ejecución en el equipo, con autenticación `scram-sha-256`.
- Documentación técnica previa de buena calidad: auditoría de compatibilidad, inspección de la CNN y revisión de integración.

### 1.2 Lo que falta

- Repositorio Git (el proyecto **no es un repositorio Git**).
- Apps Django funcionales, modelos, migraciones, vistas, formularios y plantillas.
- Integración real con PostgreSQL: base `sismodetect`, rol dedicado y `psycopg`.
- Cliente FDSN IRIS/EarthScope y lector MiniSEED (`obspy` no instalado).
- Validador de compatibilidad y regla exacta de ventana.
- Pipeline de IA: carga perezosa, preprocesamiento con estadísticas congeladas, inferencia y umbral.
- Interfaz web, identidad visual implementada, mapa y páginas funcionales.
- Autenticación/roles, historial, notificaciones, auditoría y solicitudes de revisión.
- Pruebas automatizadas (`pytest` no instalado).
- Documentación de instalación para Windows.

### 1.3 Bloqueos principales

1. **Git:** sin repositorio no hay trabajo colaborativo real ni trazabilidad de cambios.
2. **PostgreSQL:** el servidor existe, pero la base `sismodetect`, el rol de aplicación y el adaptador `psycopg` no están verificados/creados.
3. **Dependencias de adquisición:** `obspy` y `psycopg` no están instalados; `requests` está instalado pero no declarado.
4. **Decisión de modelo de usuario:** hay que decidir antes de la primera migración si se usará usuario personalizado o perfil.
5. **Regla de ventana y QC:** la documentación la describe, pero no está implementada ni probada.
6. **XAI:** depende del Equipo 2; no debe simularse.

### 1.4 Veredicto

**La arquitectura actual permite implementar el sistema sin reconstruirlo.** El proyecto está listo para comenzar la Fase 0 de implementación, pero **no está listo para operar**. Un mes es un plazo realista solo si se trabaja en paralelo con 2–3 personas y se controla el alcance; con una sola persona, el alcance completo es difícilmente alcanzable sin recortes.

### 1.5 Tablero de estado

| Área | Estado | Evidencia |
|---|---|---|
| Estructura del proyecto Django | **IMPLEMENTADO Y VERIFICADO** | `manage.py check`: 0 incidencias |
| Apps Django funcionales | **NO IMPLEMENTADO** | `apps/` solo contiene `__init__.py` |
| PostgreSQL como servidor | **IMPLEMENTADO Y VERIFICADO** | Servicio `postgresql-x64-18` en ejecución; 18.7; puerto 5432 |
| Integración Django–PostgreSQL | **NO IMPLEMENTADO** | `settings.py` usa SQLite; `psycopg` ausente |
| Artefactos CNN V1 | **IMPLEMENTADO Y VERIFICADO** | 6/6 hashes; carga correcta; predicción de humo estable |
| Código de IA | **NO IMPLEMENTADO** | Paquetes `ia/*` solo con docstrings |
| Adquisición FDSN | **NO IMPLEMENTADO** | Sin cliente, sin lector MiniSEED, sin `obspy` |
| Interfaz web | **NO IMPLEMENTADO** | Sin plantillas, CSS, JS ni estáticos |
| Autenticación y roles | **PARCIALMENTE IMPLEMENTADO** | `django.contrib.auth` instalado; sin usuarios, roles ni pantallas |
| Migraciones | **NO IMPLEMENTADO** | 0 migraciones aplicadas; 0 apps propias |
| Pruebas automatizadas | **NO IMPLEMENTADO** | `tests/` vacío; `pytest` ausente |
| Git | **NO IMPLEMENTADO** | No existe `.git`; Git 2.51 está instalado |
| Documentación | **PARCIALMENTE IMPLEMENTADO** | 4 documentos; README y `.gitkeep` desactualizados |
| Base `sismodetect` | **REQUIERE INVESTIGACIÓN** | No verificable sin credenciales de PostgreSQL |
| Conectividad FDSN actual | **REQUIERE INVESTIGACIÓN** | No se re-ejecutaron consultas en esta fase |
| Paridad numérica Keras/NumPy | **REQUIERE INVESTIGACIÓN** | Entrenamiento con Keras 3.13.2 / NumPy 2.4.6; ejecución con 3.15.1 / 2.5.5 |

---

## 2. Estructura actual del proyecto

```text
SismoDetect/
├── .idea/                         Configuración local de PyCharm (excluida de Git)
├── .venv/                         Entorno virtual local (excluido de Git)
├── apps/
│   └── __init__.py                Paquete vacío; menciona apps.catalogacion y apps.api (nombres obsoletos)
├── config/
│   ├── __init__.py
│   ├── asgi.py                    Punto de entrada ASGI estándar
│   ├── settings.py                Configuración base; SQLite, DEBUG=True, sin apps propias
│   ├── urls.py                    Solo ruta /admin/
│   └── wsgi.py                    Punto de entrada WSGI estándar
├── data/
│   ├── entrada/.gitkeep           Vacía; solo marcador
│   └── temporal/.gitkeep          Vacía; solo marcador
├── documentacion/
│   ├── AUDITORIA_COMPATIBILIDAD_SENALES.md
│   ├── INFORME_ESTRUCTURA_INICIAL.md
│   ├── INSPECCION_CNN_V1.md
│   └── REVISION_TECNICA_INTEGRACION.md
├── ia/
│   ├── __init__.py
│   ├── gestor_modelos/__init__.py Solo docstring
│   ├── inferencia/__init__.py     Solo docstring
│   ├── modelos/__init__.py        Solo docstring
│   ├── pesos/
│   │   ├── __init__.py
│   │   └── cnn_v1/                Artefactos de la CNN V1 + .gitkeep obsoleto
│   └── procesamiento/__init__.py  Solo docstring
├── requirements/
│   ├── base.txt                   Django==6.1.3
│   ├── dev.txt                    pytest, pytest-django, pytest-cov, ruff (sin fijar)
│   ├── dev-ia.txt                 Incluye tensorflow.txt + dev.txt
│   └── tensorflow.txt             tensorflow==2.21.0
├── tests/
│   └── __init__.py                Vacío
├── .gitignore
├── db.sqlite3                     0 bytes; sin migraciones
├── manage.py
└── README.md                      Desactualizado respecto a los pesos
```

### 2.1 Observaciones estructurales

- **No existe `.git`:** el proyecto no es un repositorio Git, aunque Git 2.51.0 está disponible en el equipo.
- **No existen** carpetas `static/`, `templates/`, `migrations/` ni `management/`.
- **No existen** archivos HTML, CSS, JS, SVG, PNG o JPG en el proyecto.
- `data/` solo contiene marcadores `.gitkeep`; no hay `data/registros/` para MiniSEED.
- `db.sqlite3` existe, pero está vacío (0 bytes) y no tiene migraciones aplicadas.
- `ia/pesos/cnn_v1/` contiene los artefactos reales, aunque su `.gitkeep` afirma que los pesos “todavía NO se han copiado”.
- El `README.md` también afirma que los pesos no están implementados ni copiados; es información desactualizada.

---

## 3. Componentes existentes y su estado

| Componente | Ruta | Estado | Evidencia / observación |
|---|---|---|---|
| Proyecto Django | `config/` | **IMPLEMENTADO Y VERIFICADO** | `manage.py check`: 0 incidencias; Django 6.1.3 |
| Enrutado raíz | `config/urls.py` | **PARCIALMENTE IMPLEMENTADO** | Solo `admin/`; no hay rutas de aplicación |
| Paquete de apps | `apps/__init__.py` | **PARCIALMENTE IMPLEMENTADO** | Solo docstring; nombres de ejemplo obsoletos |
| Paquetes de IA | `ia/*/__init__.py` | **PARCIALMENTE IMPLEMENTADO** | Solo docstrings; no hay funciones ni clases |
| Artefactos CNN V1 | `ia/pesos/cnn_v1/` | **IMPLEMENTADO Y VERIFICADO** | 7/7 archivos presentes; 6/6 hashes correctos; modelo carga |
| Integración CNN | `ia/` | **NO IMPLEMENTADO** | No hay cargador, preprocesamiento ni inferencia |
| Documentación | `documentacion/` | **PARCIALMENTE IMPLEMENTADO** | 4 documentos útiles; README y `.gitkeep` desactualizados; una contradicción menor |
| Dependencias | `requirements/` | **PARCIALMENTE IMPLEMENTADO** | Faltan `psycopg`, `obspy`, `pytest`, `ruff`; `requests` no declarado |
| Configuración de datos | `data/` | **PARCIALMENTE IMPLEMENTADO** | Solo carpetas vacías; no hay retención de MiniSEED |
| Pruebas | `tests/` | **NO IMPLEMENTADO** | Solo `__init__.py`; `pytest` no instalado |
| Base de datos local | `db.sqlite3` | **NO IMPLEMENTADO** | 0 bytes; 18 migraciones contrib sin aplicar |
| Control de versiones | `.git/` | **NO IMPLEMENTADO** | No existe repositorio Git |
| Interfaz web | — | **NO IMPLEMENTADO** | Sin plantillas, CSS, JS ni estáticos |

### 3.1 Comprobaciones realizadas

- Lectura completa de `settings.py`, `urls.py`, `manage.py`, `README.md`, `.gitignore` y `requirements/`.
- `python manage.py check` → 0 incidencias.
- `python manage.py check --deploy` → 8 incidencias: 1 error (`mail.E001`) y 7 advertencias de seguridad.
- `python manage.py showmigrations` → 18 migraciones contrib, todas sin aplicar.
- Verificación de que `db.sqlite3` conserva el mismo SHA-256 antes y después de `showmigrations` (archivo vacío, hash `E3B0C442...`).
- Verificación SHA-256 de los 6 artefactos del inventario antes y después de cargar el modelo: **6/6 correctos**.
- Carga del modelo con `compile=False`: entrada `(None, 3000, 3)`, salida `(None, 1)`, 44 705 parámetros.
- Predicción de humo con ceros: `0.11681132763624191`, idéntica a la inspección previa.
- Comprobación del servicio PostgreSQL, puerto, autenticación, ruta de instalación y configuración.
- Comprobación de dependencias instaladas y ausentes.
- Comprobación de existencia de Git, Node/npm y espacio en disco.
- **No se ejecutaron consultas FDSN, no se descargaron datos y no se modificó ningún artefacto.**

---

## 4. Auditoría de Django

### 4.1 Configuración actual

| Elemento | Valor actual | Evaluación |
|---|---|---|
| Motor de base de datos | SQLite (`db.sqlite3`) | **No cumple** el requisito PostgreSQL |
| `DEBUG` | `True` | Aceptable en desarrollo; **no apto** para entrega final |
| `ALLOWED_HOSTS` | `[]` | Solo localhost con `DEBUG=True`; no permite acceso desde otro equipo |
| `SECRET_KEY` | Cadena `django-insecure-...` embebida | **Riesgo de seguridad**; debe pasar a variable de entorno |
| `LANGUAGE_CODE` | `en-us` | La interfaz debe ser en español; requiere `es` |
| `TIME_ZONE` | `UTC` | Correcto para almacenar; la UI debe mostrar hora de Cuba |
| `USE_TZ` | `True` | Correcto |
| `STATIC_URL` | `static/` | Relativa; conviene revisar y definir `STATICFILES_DIRS`/`STATIC_ROOT` |
| `TEMPLATES.DIRS` | `[]` | Correcto si cada app usa `templates/`; no hay apps todavía |
| `MAILERS` | Backend de consola | Válido en Django 6.1, pero **no envía correo real**; `check --deploy` lo marca como error |
| `LOGGING` | No definido | **Falta** registro de errores y auditoría |
| `AUTH_USER_MODEL` | No definido | Se usa `auth.User`; no hay roles ni perfil |
| `MEDIA_ROOT` / `MEDIA_URL` | No definidos | No hay gestión de archivos subidos; para MiniSEED se recomienda carpeta propia |
| `DEFAULT_AUTO_FIELD` | No definido | Django usa `BigAutoField` por defecto; aceptable |
| `SECURE_*` | Sin configurar | `check --deploy` advierte HSTS, SSL, cookies seguras |

**Nota sobre `MAILERS`:** Django 6.1 incorpora `MAILERS` y deshabilita `EMAIL_BACKEND` cuando aquel está definido. La configuración actual es válida para desarrollo, pero el backend de consola no sirve para notificaciones reales por correo. Si las notificaciones serán solo internas (base de datos), esto no bloquea; si se exigirá correo, habrá que configurar SMTP.

### 4.2 URLs y rutas

`config/urls.py` solo registra:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
]
```

No existen rutas para inicio, estaciones, búsqueda, análisis, resultados, historial, perfil ni panel administrativo propio.

### 4.3 Modelos, vistas, formularios y plantillas

| Componente | Estado |
|---|---|
| Modelos | **NO IMPLEMENTADO** — no hay `models.py` |
| Vistas | **NO IMPLEMENTADO** — no hay `views.py` |
| Formularios | **NO IMPLEMENTADO** — no hay `forms.py` |
| Plantillas | **NO IMPLEMENTADO** — no hay `templates/` |
| Archivos estáticos | **NO IMPLEMENTADO** — no hay `static/` |
| Servicios internos | **NO IMPLEMENTADO** — no hay capa de orquestación |
| Endpoints internos | **NO IMPLEMENTADO** — correcto: no debe haber API pública |

### 4.4 Autenticación y permisos

- `django.contrib.auth` y `django.contrib.admin` están instalados.
- No hay usuarios creados: `db.sqlite3` está vacío.
- No hay modelo de usuario personalizado ni perfil.
- No hay roles, grupos ni permisos definidos.
- No hay plantillas de login, logout, cambio de contraseña ni perfil.
- No hay `LOGIN_URL`, `LOGIN_REDIRECT_URL` ni `LOGOUT_REDIRECT_URL`.
- El panel `/admin/` existe, pero no tiene superusuario ni modelos registrados.

**Decisión pendiente e importante:** definir antes de la primera migración si se usará:

1. `AUTH_USER_MODEL` personalizado (`Usuario(AbstractUser)` con campo `rol`), o
2. `auth.User` + `Perfil` OneToOne con `rol`.

La opción 1 es más limpia a largo plazo y ahora es barata porque no hay migraciones aplicadas; la opción 2 es más conservadora. En ambos casos, los permisos granulares deben apoyarse en grupos/permisos de Django.

### 4.5 Estado de las migraciones

| Grupo | Migraciones | Estado |
|---|---:|---|
| `admin` | 3 | Sin aplicar |
| `auth` | 12 | Sin aplicar |
| `contenttypes` | 2 | Sin aplicar |
| `sessions` | 1 | Sin aplicar |
| Apps propias | 0 | No existen |
| **Total** | **18** | **Ninguna aplicada** |

`db.sqlite3` tiene 0 bytes. No se ejecutó ninguna migración.

### 4.6 Resultado de `check --deploy`

```text
ERRORS:
?: (mail.E001) MAILERS usa un backend de email solo para desarrollo
   (django.core.mail.backends.console.EmailBackend).

WARNINGS:
?: (security.W004) SECURE_HSTS_SECONDS no configurado.
?: (security.W008) SECURE_SSL_REDIRECT no configurado.
?: (security.W009) SECRET_KEY débil o generada automáticamente.
?: (security.W012) SESSION_COOKIE_SECURE no configurado.
?: (security.W016) CSRF_COOKIE_SECURE no configurado.
?: (security.W018) DEBUG=True en despliegue.
?: (security.W020) ALLOWED_HOSTS vacío en despliegue.
```

Para una aplicación local de demostración, varias advertencias son esperables; aun así, **`DEBUG`, `SECRET_KEY` y `ALLOWED_HOSTS` deben resolverse antes de la entrega**.

### 4.7 ¿La arquitectura actual permite implementar el sistema?

**Sí.** La separación `config/` + `apps/` + `ia/` es adecuada y no exige reconstruir el proyecto. Los cambios necesarios son de configuración y de implementación:

- cambiar SQLite por PostgreSQL;
- añadir apps dentro de `apps/`;
- definir usuario/perfil y roles;
- añadir `templates/` y `static/`;
- añadir `LOGGING`;
- separar configuración de desarrollo y entrega;
- mover secretos a variables de entorno.

No se detectó ninguna decisión estructural que obligue a empezar de cero.

## 5. Auditoría de PostgreSQL

### 5.1 Estado del servidor

| Comprobación | Resultado |
|---|---|
| Versión | **PostgreSQL 18.7** |
| Servicio | `postgresql-x64-18`, estado **Running**, inicio **Automatic** |
| Ruta de instalación | `D:\Escuela\Posgre SQL` |
| Puerto | 5432, escuchando en `0.0.0.0` y `::` |
| Autenticación | `scram-sha-256` para conexiones locales y TCP en localhost |
| `listen_addresses` | `'*'` |
| Zona horaria del servidor | `America/New_York` |
| `psql` en `PATH` | **No**; el binario está en `D:\Escuela\Posgre SQL\bin\psql.exe` |
| Credenciales disponibles en el entorno | **No**; no hay `PGPASSWORD` ni `DATABASE_URL` |
| Base `sismodetect` | **No verificada**; no se pudo consultar sin contraseña |
| Rol de aplicación | **No verificado** |
| `psycopg` en `.venv` | **No instalado** |
| Configuración Django | SQLite; **no PostgreSQL** |

**Nota de seguridad:** aunque `listen_addresses='*'`, `pg_hba.conf` solo permite conexiones `host` desde `127.0.0.1/32` y `::1/128`, además de `local`. No se observaron reglas para toda la red local. Aun así, no debe modificarse la configuración global del servidor sin coordinar con el otro proyecto que lo utiliza.

### 5.2 Implicaciones

- **No se debe instalar otro servidor PostgreSQL.** El requisito es usar el existente.
- **No se debe tocar ninguna base de datos ajena a SismoDetect.**
- La base `sismodetect` y un rol dedicado deben crearse en la Fase 0 de implementación, con autorización y credenciales.
- El rol de aplicación **no debe ser superusuario**; debe tener permisos solo sobre `sismodetect`.
- La contraseña debe ir en `.env` o variable de entorno, nunca en `settings.py`.
- La base debe crearse con codificación UTF-8 y ordenamiento adecuado para español.
- `psql` no está en `PATH`; la documentación de Windows deberá indicar la ruta completa o añadirla.
- `db.sqlite3` deberá retirarse del flujo de trabajo cuando PostgreSQL esté configurado; no eliminarlo sin autorización.

### 5.3 Esquema previsto y estado

| Elemento | Estado |
|---|---|
| Base `sismodetect` | **REQUIERE INVESTIGACIÓN / CREACIÓN** |
| Rol dedicado | **NO IMPLEMENTADO** |
| `psycopg[binary]` | **NO INSTALADO** |
| `DATABASES` en Django | **NO CONFIGURADO** |
| Modelos y migraciones | **NO IMPLEMENTADO** |
| Restricciones de integridad | **NO IMPLEMENTADO** |
| Copias de seguridad | **NO IMPLEMENTADO** |
| Auditoría de acciones | **NO IMPLEMENTADO** |

---

## 6. Auditoría de la CNN V1

### 6.1 Artefactos solicitados

| Archivo | Bytes | Estado |
|---|---:|---|
| `mejor_modelo_cnn_v1.keras` | 602 838 | **Presente y verificado** |
| `estadisticas_normalizacion.npz` | 1 344 | **Presente y verificado** |
| `manifiesto_preprocesamiento.json` | 1 011 | **Presente y verificado** |
| `seleccion_umbral_v1.json` | 756 | **Presente y verificado** |
| `configuracion_entrenamiento.json` | 1 873 | **Presente y verificado** |
| `INFORME_FINAL_CNN_V1.md` | 6 301 | **Presente y verificado** |
| `inventario_sha256.json` | 919 | **Presente** |

### 6.2 Verificación SHA-256

| Archivo | SHA-256 |
|---|---|
| `mejor_modelo_cnn_v1.keras` | `cd9e8962d1cdc2977ef15854a416a89c87591d489d870d86f2b64a05e3f2a0d5` |
| `estadisticas_normalizacion.npz` | `dea35212ca9e992ef6895e465f331e3ba43ea1e87bee15507ccf83ad16d5b32d` |
| `manifiesto_preprocesamiento.json` | `f61217fd1cad73c127993f589160067d7995dd5c81103f3439660f0cb6c6e8ed` |
| `seleccion_umbral_v1.json` | `78228b4433efb6cbe5907311003948e9af92e5952dfe6b7cf38e0c9c11680475` |
| `configuracion_entrenamiento.json` | `cb7ecf197538ed7e0d7bc4b8b4cc77a22e162324e978eaf480dd10d7f5f4cc45` |
| `INFORME_FINAL_CNN_V1.md` | `48cd811353c29a64aa3f9115274dac2c8c659c38280d70717246ac9f7527a772` |

**Resultado: 6/6 correctos antes y después de cargar el modelo.** Los artefactos no fueron alterados.

### 6.3 Carga y estructura del modelo

| Comprobación | Resultado |
|---|---|
| Carga con `keras.models.load_model(..., compile=False)` | Correcta |
| Entrada | `(None, 3000, 3)` |
| Salida | `(None, 1)` |
| Parámetros | 44 705 |
| Predicción de humo con ceros | `0.11681132763624191` |
| Formato de guardado | Keras 3.13.2, guardado el 2026-11-17 |
| Arquitectura | CNN 1D: Conv1D 32/64/128, BatchNorm + ReLU, MaxPooling, GlobalAveragePooling, Dense 64, Dropout 0.3, Dense 1 sigmoid |

La predicción con ceros **no es una evaluación de rendimiento**; solo confirma que el modelo carga, ejecuta y produce un valor estable.

### 6.4 Contrato de preprocesamiento

| Elemento | Valor congelado |
|---|---|
| Frecuencia | 100 Hz |
| Duración | 30 s |
| Muestras | 3000 |
| Canales | Z, N, E |
| Tipo | `float32` |
| Unidad | counts crudos |
| Paso 1 | Restar media temporal por segmento y canal |
| Paso 2 | Estandarizar con `media_train` y `desviacion_train` |
| Medias | `[0.0006783410790376365, 0.0007371546817012131, 3.24415486829821e-05]` |
| Desviaciones | `[14287.1103515625, 15959.3994140625, 13554.525390625]` |
| Estadísticas | Calculadas solo con TRAIN; **nunca recalcular** |
| Umbral | `0.2927532196044922` |
| Regla | `sismo` si `puntuacion >= umbral`; `ruido` si `<` |
| Prohibido | Normalización por segmento, interpolación, relleno, remuestreo, filtrado no previsto |

### 6.5 Rendimiento declarado

Métricas de **validación** (selección del umbral):

- Macro F1: `0.9093718676912796`
- F1 ruido: `0.9041095890410958`
- F1 sismo: `0.9146341463414634`
- Precisión sismo: `0.9259259259259259`
- Recall sismo: `0.9036144578313253`
- Balanced accuracy: `0.910140562248996`
- Matriz de confusión: `[[66, 6], [8, 75]]`

Métricas de **test** declaradas en el informe final:

- Accuracy: `0.9548`
- Precisión sismo: `0.9419`
- Recall sismo: `0.9759`
- Especificidad ruido: `0.9306`
- F1 sismo: `0.9586`
- F1 ruido: `0.9504`
- Macro F1: `0.9545`
- Balanced accuracy: `0.9532`
- ROC-AUC: `0.9873`
- PR-AUC: `0.9920`
- 148/155 correctas; 5 falsos positivos; 2 falsos negativos

**Estas métricas están documentadas, pero no fueron re-evaluadas en esta auditoría.** No deben presentarse como garantía de rendimiento en datos vivos ni en estaciones no representadas.

### 6.6 Deriva de versiones

| Componente | Entrenamiento | Ejecución actual | Riesgo |
|---|---|---|---|
| TensorFlow | 2.21.0 | 2.21.0 | Bajo |
| Keras | 3.13.2 | 3.15.1 | **Medio**: posible diferencia numérica |
| NumPy | 2.4.6 | 2.5.5 | **Medio**: posible diferencia numérica |
| Plataforma | Linux, CPU | Windows, CPU | Bajo para inferencia; sin GPU nativa en Windows |
| h5py | No declarado | 3.14.0 | Bajo |

La carga funciona y la predicción de humo coincide con la inspección previa, pero **no se ha medido** la diferencia numérica en un vector real. Debe añadirse una prueba de regresión con un tensor de referencia.

### 6.7 Estado de integración

| Componente | Estado |
|---|---|
| Artefactos del modelo | **IMPLEMENTADO Y VERIFICADO** |
| Cargador de artefactos | **NO IMPLEMENTADO** |
| Verificación de hashes en tiempo de ejecución | **NO IMPLEMENTADO** |
| Preprocesamiento CNN V1 | **NO IMPLEMENTADO** |
| Inferencia y umbral | **NO IMPLEMENTADO** |
| Carga perezosa de TensorFlow | **NO IMPLEMENTADO** |
| Bloqueo de concurrencia | **NO IMPLEMENTADO** |
| Registro de versión del modelo | **NO IMPLEMENTADO** |
| Pruebas de la IA | **NO IMPLEMENTADO** |
| XAI | **NO IMPLEMENTADO** (correctamente diferido) |

**Conclusión:** el modelo está listo para integrarse, pero **el código de integración no existe todavía**.

---

## 7. Auditoría de IRIS/EarthScope

### 7.1 Estado en SismoDetect

| Componente | Estado |
|---|---|
| Cliente FDSN | **NO IMPLEMENTADO** |
| Consulta de estaciones/metadatos | **NO IMPLEMENTADO** |
| Consulta de disponibilidad por fecha | **NO IMPLEMENTADO** |
| Descarga MiniSEED | **NO IMPLEMENTADO** |
| Lector MiniSEED | **NO IMPLEMENTADO** (`obspy` ausente) |
| Almacenamiento de MiniSEED original | **NO IMPLEMENTADO** |
| Verificación de compatibilidad | **NO IMPLEMENTADO** |
| Pruebas con respuestas FDSN | **NO IMPLEMENTADO** |
| `requests` | Instalado (2.34.2), pero **no declarado** en `requirements/` |

### 7.2 Evidencia previa documentada

La auditoría `AUDITORIA_COMPATIBILIDAD_SENALES.md` ya verificó, con descargas pequeñas y controladas:

- IRIS y EarthScope son espejos equivalentes para `CW.QMBU` (diferencia máxima `0` counts).
- La red `CW` tiene 21 estaciones y 87 canales en el catálogo consultado.
- 15 estaciones tienen familia `HH` de banda ancha a 100 Hz.
- Solo 9 estaciones aportaron segmentos al entrenamiento: MARV, CHIV, CCCC, QMBU, NMDO, MASC, CAIB, CAMR y SOR.
- La disponibilidad de `CW` disminuyó entre 2023 y 2026: de 10 estaciones en 2023 a 2 en septiembre de 2026.
- Las respuestas pueden tener 3000, 3001 o 6001 muestras según estación y convención de límites.
- El orden devuelto es `HHE, HHN, HHZ`; debe reordenarse a `Z, N, E`.
- `HN*` (acelerómetros) y `EH*` (sensores de 2 s) **no son compatibles** con la CNN V1.
- `CU.GTBY` usa `HH1/HH2/HHZ`, no `HHN/HHE`; es complementaria, no equivalente.
- Seis estaciones `HH` nunca fueron vistas por el modelo: GNEO, HLG, LMGC, MGV, PILO y RCC.

**Estos resultados son evidencia documentada previamente; no se re-ejecutaron consultas FDSN en esta fase.** La conectividad actual desde este equipo queda como **REQUIERE INVESTIGACIÓN**.

### 7.3 Datos de catálogo disponibles fuera del proyecto

En el proyecto del dataset (fuera de SismoDetect) existen catálogos que podrían servir de base, previa autorización y verificación de procedencia:

| Archivo | Contenido | Filas |
|---|---|---:|
| `estaciones.csv` | 21 estaciones con latitud, longitud, elevación, sitio, inicio y fin | 22 con encabezado |
| `canales.csv` | 87 canales con azimut, dip, sensor, ganancia, unidades, frecuencia e intervalos | 88 con encabezado |
| `disponibilidad_empirica.csv` | Sondeos empíricos de disponibilidad | 1 261 con encabezado |
| `catalogo_cenais.csv` | Catálogo sísmico CENAIS con 50 088 eventos | 50 089 con encabezado |

**Advertencia:** estos archivos pertenecen a otro proyecto. No deben copiarse sin autorización, ni asumirse como catálogo oficial actualizado. La disponibilidad es empírica y no continua.

### 7.4 Brechas técnicas

1. **Consulta de disponibilidad:** no está definido qué servicio se usará para listar “registros encontrados” por intervalo. `dataselect` devuelve datos, no un catálogo de segmentos. Habrá que evaluar el servicio `availability` de IRIS/EarthScope o derivar la disponibilidad del servicio `station` con épocas de canal. **REQUIERE INVESTIGACIÓN.**
2. **Normalización de trazas:** no hay código para unir trazas contiguas, rechazar huecos o detectar máscaras.
3. **Ventana exacta:** no hay implementación de la regla `i0 = round((t0 - starttime) * 100)`.
4. **Almacenamiento:** no hay carpeta `data/registros/` ni política de retención.
5. **Errores HTTP:** no hay manejo de `204`, `404`, `5xx`, timeouts ni reintentos.
6. **Seguridad:** no hay validación de URL; debe impedirse que el usuario introduzca URLs arbitrarias (SSRF).
7. **Pruebas sin red:** no hay fixtures MiniSEED ni respuestas simuladas.

### 7.5 Comportamiento recomendado del cliente FDSN

- Fuente principal: `https://service.iris.edu/fdsnws/dataselect/1/query`.
- Espejo: `https://service.earthscope.org/fdsnws/dataselect/1/query`.
- Parámetros: `net=CW`, `sta=<estación>`, `loc=00`, `cha=HHZ,HHN,HHE`, `starttime`, `endtime`, `format=miniseed`.
- `204` y `404`: tratar como “sin datos”, no como error del usuario.
- `5xx` y fallos de red: reintento limitado y alternancia de hosts.
- Timeout explícito, límite de tamaño de respuesta y `User-Agent` identificable.
- No aceptar URLs arbitrarias: construir la petición solo con estaciones y fechas validadas.
- Guardar los bytes originales y su SHA-256; no reescribir el MiniSEED.
- Ordenar explícitamente a `Z, N, E`.
- No interpolar, rellenar ni remuestrear.

### 7.6 Regla de ventana propuesta

La regla usada al construir el dataset está documentada en `procesar_senales.py`:

```python
i0 = int(round((inicio - tr.stats.starttime) * tr.stats.sampling_rate))
ventana = tr.data[i0:i0 + 3000]
```

Condiciones observadas en el código del dataset:

- frecuencia de muestreo dentro de `±0.01` Hz;
- la traza debe empezar antes de `inicio + 1 ms` y terminar después de `fin - 1 ms`;
- no debe ser un `MaskedArray` con máscara;
- `i0 >= 0` y `i0 + 3000 <= npts`;
- salida en `float32`;
- QC posterior: rechazar más de 50 % de ceros, desviación cero, canal constante o amplitud menor que 2 counts.

**Propuesta para SismoDetect:**

1. Solicitar exactamente `[t0, t0 + 30 s]`.
2. Exigir que cada traza empiece en `t0` o antes, con tolerancia máxima de 1 ms, y cubra hasta `t0 + 30 s`.
3. Calcular `i0 = round((t0 - starttime) * 100)`.
4. Exigir `i0 >= 0` y `i0 + 3000 <= npts`.
5. Extraer exactamente `data[i0:i0 + 3000]`.
6. Registrar `npts_recibidos`, `npts_usados`, `offset_muestras`, `t_real_inicio` y el motivo del descarte.
7. Rechazar si no se puede demostrar alineación o continuidad.

**Casos:**

| Respuesta | Acción |
|---|---|
| 3000 muestras alineadas | Aceptar |
| 3001 muestras con extremo final inclusivo | Aceptar las 3000 primeras; registrar el descarte |
| 3001 muestras con inicio 10 ms antes | Aceptar desde el índice 1; registrar el desplazamiento |
| Menos de 3000 | Rechazar |
| Más de 3001 en una petición de 30 s | Rechazar por anomalía de convención |
| Traza que empieza después de `t0` | Rechazar |
| Huecos, máscaras, NaN/Inf | Rechazar |
| Componente faltante | Rechazar |
| Varias trazas no contiguas | Rechazar |
| Varias trazas estrictamente contiguas | **Decisión pendiente**: unir solo si no hay solapamiento ni hueco, o rechazar por simplicidad |

**Detalle numérico:** Python usa redondeo bancario en `round()`; para paridad exacta con el dataset debe replicarse el mismo comportamiento y probarse con casos de media muestra.

### 7.7 Política de estaciones

| Grupo | Estaciones | Tratamiento |
|---|---|---|
| Representadas en entrenamiento | MARV, CHIV, CCCC, QMBU, NMDO, MASC, CAIB, CAMR, SOR | Compatibles; mostrar advertencia si la disponibilidad es baja |
| `HH` no vistas | GNEO, HLG, LMGC, MGV, PILO, RCC | **Experimentales**; no mezclar con el piloto sin advertencia |
| `EH` | GTMO, MOAC, PIN, SAB, YAR; históricos CAIB/PILO | **No compatibles** con V1 |
| `HN` | ECENT, LMGC, MASC, MOAC, RCC | **No compatibles** con V1 |
| `CU.GTBY` | `HH1/HH2/HHZ` | **Complementaria**: requiere mapeo por azimut, corrección de escala y advertencia; disponibilidad esporádica |

---

## 8. Auditoría de interfaz

### 8.1 Estado actual

| Componente | Estado |
|---|---|
| Plantillas HTML | **NO IMPLEMENTADO** |
| Hojas de estilo | **NO IMPLEMENTADO** |
| JavaScript | **NO IMPLEMENTADO** |
| Logotipo e identidad visual | **NO IMPLEMENTADO** |
| Mapa de estaciones | **NO IMPLEMENTADO** |
| Pantallas de autenticación | **NO IMPLEMENTADO** |
| Diseño responsive | **NO IMPLEMENTADO** |
| Accesibilidad | **NO IMPLEMENTADO** |
| Recursos locales | **NO IMPLEMENTADO** |

No existe ningún archivo HTML, CSS, JS, SVG o imagen en el proyecto. La única interfaz disponible es el admin de Django en `/admin/`, sin superusuario ni modelos registrados.

### 8.2 Identidad visual definida

La paleta aprobada es coherente con un centro científico de monitoreo sísmico. Propuesta de uso:

| Color | Hex | Uso recomendado |
|---|---|---|
| Azul profundo | `#14283D` | Fondo de cabecera, navegación, texto principal sobre claro |
| Azul | `#244B68` | Botones primarios, encabezados de sección, enlaces |
| Azul petróleo | `#287C91` | Acentos, iconos, estados informativos |
| Turquesa | `#35B8A5` | Estados correctos, indicadores activos, detalles científicos |
| Dorado | `#E4A64B` | Advertencias, umbral, elementos destacados; no usar como texto pequeño sobre fondo claro |
| Fondo claro | `#F3F6F8` | Fondo general de la aplicación y tarjetas |

Recomendaciones:

- Tipografía del sistema (`Segoe UI`, `system-ui`, `Roboto`, `sans-serif`) para evitar fuentes externas.
- Tarjetas blancas sobre `#F3F6F8`, bordes sutiles y sombras discretas.
- Cabecera oscura `#14283D` con acentos turquesa/dorado.
- Formas de onda y gráficos en SVG/canvas propios, sin CDN.
- Contraste WCAG AA; no comunicar estados solo por color.
- Iconografía local en SVG; evitar librerías externas innecesarias.

### 8.3 Pantallas previstas

| Pantalla | Contenido mínimo | Estado | Prioridad |
|---|---|---|---|
| Inicio | Propósito, alcance, advertencia de no predicción ni alerta temprana, accesos principales | **NO IMPLEMENTADO** | Must |
| Estaciones y mapa | Catálogo CW, coordenadas, canales, sensores, disponibilidad, marca de “representada en entrenamiento” o “experimental” | **NO IMPLEMENTADO** | Must |
| Búsqueda de registros | Estación, intervalo UTC/local, consulta de disponibilidad, listado de segmentos encontrados | **NO IMPLEMENTADO** | Must |
| Nuevo análisis | Selección de estación y ventana; paso 1 “Comprobar compatibilidad”; paso 2 “Clasificar” | **NO IMPLEMENTADO** | Must |
| Resultado | Clase, puntuación, umbral, versión/hash del modelo, fecha, forma de onda Z/N/E, estadísticas por canal, advertencias | **NO IMPLEMENTADO** | Must |
| Historial | Filtros por estación, estado, fecha y usuario; rechazos sin puntuación; detalle trazable | **NO IMPLEMENTADO** | Must |
| Modelo | Ficha técnica, arquitectura, métricas declaradas, umbral, limitaciones, hashes | **NO IMPLEMENTADO** | Should |
| Perfil y configuración | Nombre, zona horaria de visualización, estación predeterminada, notificaciones | **NO IMPLEMENTADO** | Should |
| Panel administrativo | Usuarios, roles, catálogo, versiones de modelo, auditoría, solicitudes de revisión | **NO IMPLEMENTADO** | Should |
| Explicabilidad | Estado “Explicación no disponible” hasta que el Equipo 2 entregue el método | **NO IMPLEMENTADO** | Could |
| Inicio de sesión | Login, logout, cambio de contraseña, recuperación local | **NO IMPLEMENTADO** | Must |

### 8.4 Herramientas de diseño disponibles

En este entorno:

- **Generación de imágenes:** disponible para crear moodboards, referencias visuales o mockups de pantallas. No se usó en esta fase.
- **Agentes de código:** `explore` y `general`; no son agentes de diseño UI/UX.
- **Documentación técnica:** Context7 para consultar Django, ObsPy, Leaflet u otras librerías cuando se autorice.
- **No hay integración con Figma, navegador automatizado ni herramienta de captura visual.**

**Herramienta que utilizaría:** el generador de imágenes para mockups de referencia, y CSS propio con variables para la implementación. No hace falta instalar nada. Para el mapa, recomiendo un SVG local de Cuba con marcadores proyectados, no teselas externas.

### 8.5 Mapa

- Las coordenadas de las 21 estaciones están disponibles en el catálogo externo.
- No hay GeoJSON ni SVG de Cuba en el proyecto.
- Opción recomendada para V1: contorno simplificado de Cuba en SVG local + proyección equirectangular + marcadores por estación.
- Opción con teselas (OpenStreetMap, Carto, etc.): dependencia externa y posible conflicto con el requisito de sistema local; **requiere decisión**.
- El mapa debe distinguir estaciones representadas, experimentales y no compatibles, y mostrar la disponibilidad de forma comprensible.

### 8.6 Mensajes y ética de la interfaz

- Mostrar siempre: “SismoDetect no predice terremotos ni es un sistema de alerta temprana”.
- La salida se llama **“puntuación del modelo”**, nunca “probabilidad calibrada”.
- El umbral se muestra como valor técnico congelado, no como verdad absoluta.
- Los rechazos deben explicar el motivo sin culpar al usuario y sugerir una acción: otra estación, otra fecha, otra ventana.
- Las estaciones no vistas por el modelo deben mostrar advertencia de generalización no verificada.
- No mostrar explicaciones XAI simuladas; mientras no exista método real, indicar “Explicación no disponible”.
- No usar lenguaje de alarma, predicción ni certeza.

### 8.7 Roles y permisos de interfaz

| Rol | Capacidades |
|---|---|
| Administrador | Gestionar usuarios, roles, catálogo, versiones de modelo, auditoría y solicitudes de revisión |
| Analista | Crear análisis, ver historial propio o global según política, solicitar revisión |
| Consulta | Ver resultados e historial en modo lectura; no modificar configuración ni modelo |

La matriz definitiva debe aprobarse antes de implementar las vistas.

## 9. Dependencias y versiones

### 9.1 Entorno actual

| Componente | Versión / estado |
|---|---|
| Python | 3.13.0 |
| Django | 6.1.3 |
| TensorFlow | 2.21.0 |
| Keras | 3.15.1 |
| NumPy | 2.5.5 |
| h5py | 3.14.0 |
| `requests` | 2.34.2 |
| `urllib3` | 2.8.0 |
| `certifi` | 2026.10.23 |
| `sqlparse` | 0.6.1 |
| `tzdata` | 2026.6 |
| PostgreSQL | 18.7 |
| Git | 2.51.0.windows.2 |
| Node.js | 20.20.1 |
| npm | 10.8.2 |
| Espacio libre en `D:` | ~10.07 GB |

### 9.2 Dependencias ausentes

| Dependencia | Necesidad | Estado |
|---|---|---|
| `psycopg[binary]` | Conexión Django–PostgreSQL | **Ausente** |
| `obspy` | Lectura MiniSEED y manejo de trazas | **Ausente en SismoDetect**; 1.5.1 verificada en el `.venv` del dataset |
| `pytest` | Pruebas | **Ausente** |
| `pytest-django` | Integración Django | **Ausente** |
| `pytest-cov` | Cobertura | **Ausente** |
| `ruff` | Calidad de código | **Ausente** |
| `Pillow` | Imágenes, solo si se requieren | **Ausente** |
| `djangorestframework` | API pública | **No necesario**; el requisito prohíbe API pública |
| `django-filter` | Filtros avanzados | **Opcional**; se puede resolver con QuerySets |
| `python-dotenv` / `django-environ` | Variables de entorno | **Opcional**; puede usarse `os.environ` |
| `whitenoise` | Estáticos en entrega | **Opcional**; depende del modo de ejecución final |
| `gunicorn` / `waitress` | Servidor de aplicación | **No necesario** para demo local |

### 9.3 Estado de `requirements/`

| Archivo | Contenido actual | Problema |
|---|---|---|
| `base.txt` | `Django==6.1.3` | Falta `psycopg` y `requests` |
| `tensorflow.txt` | `-r base.txt` + `tensorflow==2.21.0` | Falta fijar Keras/NumPy/h5py |
| `dev.txt` | `-r base.txt` + pytest/ruff sin fijar | Sin versiones; sin `psycopg` |
| `dev-ia.txt` | `-r tensorflow.txt` + `-r dev.txt` | Correcto como composición |

Recomendación:

- Añadir `psycopg[binary]` a `base.txt` o a un `postgres.txt`.
- Añadir `obspy` a un `adquisicion.txt`.
- Añadir `requests==2.34.2` explícitamente.
- Fijar `keras==3.15.1`, `numpy==2.5.5`, `h5py==3.14.0`.
- Fijar `pytest`, `pytest-django`, `pytest-cov` y `ruff` tras instalarlos.
- Generar un lock o `pip freeze` reproducible.
- No añadir DRF: no hay API pública.
- No introducir Node/Tailwind si no es imprescindible; CSS propio reduce el riesgo y el tiempo.

ObsPy es pesada (arrastra `scipy`, `matplotlib`, `lxml`, `sqlalchemy`), pero es la opción estándar. Un lector MiniSEED propio no es recomendable para V1.

---

## 10. Problemas encontrados

| ID | Problema | Evidencia | Impacto | Severidad |
|---|---|---|---|---|
| P01 | No hay repositorio Git | No existe `.git`; Git sí está instalado | Sin trazabilidad ni colaboración real | **BLOQUEO** |
| P02 | No hay apps Django funcionales | `apps/` solo contiene `__init__.py` | No hay producto que ejecutar | **BLOQUEO** |
| P03 | PostgreSQL no integrado | `settings.py` usa SQLite; `psycopg` ausente; base/rol no verificados | No se cumple el requisito de BD | **BLOQUEO** |
| P04 | No hay modelo de usuario/roles | `AUTH_USER_MODEL` sin definir; sin usuarios ni grupos | Cambiarlo después de migrar es costoso | **BLOQUEO** |
| P05 | No hay adquisición FDSN | Sin cliente, sin `obspy`, sin MiniSEED | No se pueden obtener señales | **BLOQUEO** |
| P06 | No hay código de IA | `ia/*` solo contiene docstrings | No se puede clasificar | **BLOQUEO** |
| P07 | No hay esquema de BD ni restricciones | Sin modelos ni migraciones propias | No hay historial ni trazabilidad | **BLOQUEO** |
| P08 | No hay interfaz | Sin `templates/`, `static/`, HTML/CSS/JS | No hay sistema web | **BLOQUEO** |
| P09 | No hay pruebas ni `pytest` | `tests/` vacío; `pytest` ausente | Calidad no verificable | **ALTO** |
| P10 | No hay logging, auditoría ni notificaciones | Sin `LOGGING`; sin modelos de auditoría | Incidentes no rastreables | **ALTO** |
| P11 | Configuración insegura para entrega | `DEBUG=True`, `SECRET_KEY` embebida, `ALLOWED_HOSTS=[]` | Riesgo de exposición y sesiones | **ALTO** |
| P12 | Deriva de versiones y falta de fijado | Keras 3.13.2→3.15.1; NumPy 2.4.6→2.5.5; sin pins | Posible cambio numérico | **ALTO** |
| P13 | Documentación desactualizada | README y `.gitkeep` dicen que no hay pesos; `apps/__init__` menciona `apps.api` | Confusión para el equipo | **MEDIO** |
| P14 | Configuración local incompleta | `en-us`, `STATIC_URL` relativa, sin `STATIC_ROOT`/`STATICFILES_DIRS` | UI en inglés y estáticos frágiles | **MEDIO** |
| P15 | Sin retención de MiniSEED | No existe `data/registros/`; `.gitignore` no lo cubre | Pérdida de trazabilidad o commits accidentales | **MEDIO** |
| P16 | `check --deploy` falla por correo | `mail.E001`: backend de consola | Notificaciones por correo no reales | **MEDIO** |
| P17 | `psql` fuera del `PATH` | Solo accesible en `D:\Escuela\Posgre SQL\bin` | Fricción en instalación Windows | **BAJO** |
| P18 | `db.sqlite3` vacío pero presente | 0 bytes; sin migraciones | Confusión sobre el estado real | **BAJO** |
| P19 | Sin LICENSE, CI ni `pyproject.toml` | No existen | Falta de estándares y automatización | **BAJO** |
| P20 | Ambigüedad de alcance | “Eventos”, carga manual y notificaciones no están cerrados | Riesgo de retrabajo | **ALTO** |

---

## 11. Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Plazo de un mes insuficiente para todo el alcance | Alta | Alto | Priorizar Must; paralelizar; recortar Should/Could |
| Disponibilidad decreciente de `CW` | Alta | Medio | Manejo elegante de `204`; catálogo de respaldo; mensajes claros |
| Estaciones fuera de distribución | Media | Alto | Marcarlas como experimentales; no mezclar métricas |
| Convención de 3000/3001/6001 muestras | Alta | Medio | Regla exacta de alineación; fixtures; registrar offset |
| Deriva numérica Keras/NumPy | Media | Medio | Tensor dorado; prueba de regresión; fijar versiones |
| Uso accidental del umbral 0.5 | Media | Alto | Leer siempre el JSON; prueba que prohíba valores literales |
| Carga de TensorFlow lenta o concurrente | Media | Medio | Carga perezosa, lock, caché por proceso, `compile=False` |
| Credenciales/BD equivocadas o ajenas | Media | Alto | Rol dedicado, `.env`, no tocar otras bases |
| Secretos expuestos | Media | Alto | Variables de entorno; `.env` ignorado; rotar `SECRET_KEY` |
| Crecimiento de MiniSEED y temporales | Media | Medio | Retención, limpieza, límites y monitoreo de disco |
| XAI no entregado a tiempo | Alta | Medio | Interfaz reservada; no simular; no bloquear el núcleo |
| Fallos de red o respuestas FDSN inconsistentes | Media | Medio | Timeouts, reintentos, espejo, fixtures, mensajes claros |
| Errores de permisos entre roles | Media | Alto | Matriz de permisos; pruebas por rol |
| Confusión UTC/Havana | Media | Bajo | Guardar UTC; mostrar ambas; usar zoneinfo |
| Licencia del mapa/geodatos | Baja | Bajo | SVG propio o datos de dominio público verificados |
| Documentación que se vuelve a desactualizar | Media | Bajo | Revisión al cierre de cada fase; README único |

---

## 12. Funcionalidades pendientes

### 12.1 Núcleo backend

| Funcionalidad | Prioridad | Dependencia |
|---|---|---|
| Cliente FDSN con hosts, timeouts, reintentos y `204` | Must | `requests` |
| Lector MiniSEED y normalización de trazas | Must | `obspy` |
| Catálogo de estaciones/canales importable | Must | Datos verificados |
| Validador de compatibilidad y regla de ventana | Must | Regla aprobada |
| Cargador de artefactos con hashes | Must | — |
| Preprocesamiento CNN V1 con estadísticas congeladas | Must | — |
| Inferencia con umbral congelado y bloqueo | Must | TensorFlow |
| Registro de versión del modelo | Must | BD |
| Orquestación en dos pasos con caché y hash | Must | Adquisición + IA |
| Modelos, migraciones y restricciones | Must | PostgreSQL |
| Logging de rechazos y errores | Must | BD + `LOGGING` |
| Retención de MiniSEED original | Must | `data/registros/` |
| Pruebas unitarias e integración | Must | `pytest` |

### 12.2 Interfaz

| Funcionalidad | Prioridad | Dependencia |
|---|---|---|
| Layout base y sistema de diseño | Must | Paleta aprobada |
| Inicio con advertencias | Must | — |
| Estaciones y mapa | Must | Catálogo + SVG |
| Búsqueda de registros | Must | Servicio de disponibilidad |
| Nuevo análisis en dos pasos | Must | Backend |
| Resultado con forma de onda y estadísticas | Must | Backend |
| Historial con filtros y rechazos | Must | BD |
| Login/logout | Must | Auth |
| Perfil y configuración | Should | Auth |
| Panel administrativo por rol | Should | Auth + admin |
| Notificaciones internas | Should | BD |
| Solicitudes de revisión | Should | BD |
| Auditoría visible | Should | BD |
| Explicabilidad | Could | Equipo 2 |

### 12.3 Recortes recomendados si el tiempo aprieta

- Notificaciones por correo → solo notificaciones internas.
- Panel administrativo propio → usar Django admin.
- Teselas de mapa → SVG local.
- Unión de trazas múltiples → rechazar por simplicidad.
- Catálogo de eventos CENAIS → fuera de V1; “evento” = ventana seleccionada.
- Carga manual de archivos → fuera de V1; solo FDSN.
- Exportación PDF → fuera de V1.

## 13. Recomendación de arquitectura

### 13.1 Aplicaciones Django propuestas

La revisión previa proponía cuatro apps. El alcance actual —usuarios, roles, notificaciones, auditoría y solicitudes de revisión— justifica una quinta app de cuentas.

| App | Responsabilidad | No debe hacer |
|---|---|---|
| `apps.catalogo` | Estaciones, canales, disponibilidad, importación y actualización del catálogo | Llamar a TensorFlow ni ejecutar inferencia |
| `apps.adquisicion` | Cliente FDSN, descarga MiniSEED, lectura con ObsPy, extracción de ventana y validador de compatibilidad | Conocer modelos de Django de análisis ni importar `ia` |
| `apps.analisis` | Orquestación, `VersionModelo`, `Analisis`, `MetricaCanal`, rechazos, historial y XAI | Renderizar HTML ni llamar directamente a FDSN |
| `apps.cuentas` | Usuario/perfil, roles, notificaciones, solicitudes de revisión y auditoría de acciones | Contener lógica sísmica |
| `apps.interfaz` | Vistas, formularios, plantillas, CSS, JS, mapa y panel administrativo | Importar TensorFlow ni construir URLs FDSN |

### 13.2 Flujo de dependencias

```text
interfaz ──▶ analisis ──▶ adquisicion ──▶ catalogo
    │            │
    │            └──▶ ia (paquete independiente, sin Django)
    └──▶ cuentas
```

Reglas:

- `interfaz` no contiene lógica sísmica ni llamadas directas a TensorFlow.
- `adquisicion` no importa `ia`; solo entrega una señal cruda validada.
- `analisis` es el único punto que coordina adquisición + IA + persistencia.
- `ia` no importa Django en ningún caso.
- `cuentas` no depende de `analisis`; las notificaciones se enlazan por identificador.

### 13.3 Estructura de IA

```text
ia/
├── gestor_modelos/
│   ├── artefactos.py       Lectura de JSON/NPZ, hashes y metadatos
│   └── registro.py         Registro y carga perezosa del modelo activo
├── procesamiento/
│   └── cnn_v1.py           Media por canal + estandarización congelada + float32
├── inferencia/
│   └── cnn_v1.py           Predicción, umbral congelado y resultado normalizado
└── modelos/
    └── cnn_v1.py           Adaptador de la CNN V1 (sin reconstruir la red)
```

Reglas obligatorias:

- `gestor_modelos` lee JSON y `.npz` **sin importar TensorFlow**.
- TensorFlow/Keras se importa **solo dentro de la función de predicción**.
- La carga se protege con `threading.Lock` y se cachea una vez por proceso.
- Se usa `keras.models.load_model(..., compile=False)`.
- El umbral se lee de `seleccion_umbral_v1.json`; nunca se escribe `0.5`.
- `clase = "sismo" if puntuacion >= umbral else "ruido"`.
- El preprocesamiento trabaja sobre una copia; no muta la señal original.
- Orden exacto: quitar media por segmento/canal → estandarizar con `media_train`/`desviacion_train` → `float32`.
- No recalcular estadísticas, no filtrar, no detrendizar, no remuestrear.
- Un rechazo de compatibilidad **no debe importar TensorFlow ni llamar al modelo**.

### 13.4 Contratos internos

```python
@dataclass(frozen=True)
class SenalCruda:
    datos: np.ndarray              # (3000, 3), float32, Z,N,E, counts
    red: str                       # "CW"
    estacion: str                  # "MASC"
    localizacion: str              # "00"
    canales: tuple[str, str, str]  # ("HHZ","HHN","HHE")
    t0: datetime                   # UTC
    fs: float                      # 100.0
    npts: int                      # 3000
    metadatos_canal: dict          # min/max/media/std/pct_ceros
    sha256_miniseed: str
    ruta_miniseed: Path
    proveedor: str                 # "iris" | "earthscope"

@dataclass(frozen=True)
class ResultadoCNN:
    puntuacion: float
    umbral: float
    clase: Literal["sismo", "ruido"]
    version_modelo: str
    sha256_modelo: str
    advertencia: str

@dataclass(frozen=True)
class Rechazo:
    codigo: str                    # "FS_NO_100", "COMPONENTE_FALTANTE", ...
    mensaje: str                   # texto para el usuario
    detalles: dict                 # datos técnicos para el historial
```

### 13.5 Modelo de datos PostgreSQL

| Tabla | Campos principales | Restricciones |
|---|---|---|
| `Usuario` | `AbstractUser` + `rol`, `nombre_mostrado` | Rol en `administrador`, `analista`, `consulta` |
| `Perfil` (opcional) | `usuario` OneToOne, preferencias, zona horaria | Solo si no se usa usuario personalizado |
| `Estacion` | red, código, nombre, lat, lon, elevación, inicio, fin, en_entrenamiento, experimental, prioridad, fuente, actualizado | Único `(red, codigo)` |
| `Canal` | estación FK, loc, channel, fs, unidades, ganancia, azimut, dip, sensor, inicio, fin | Único `(estacion, loc, channel, inicio)` |
| `VersionModelo` | nombre, versión, ruta, hashes, umbral, fecha_verificación, activo | Un solo `activo=True` |
| `Analisis` | UUID, usuario, estación, versión, t0/t1, fs, npts, offset, estado, resultado, puntuación, umbral, motivo, proveedor, URL, HTTP, SHA-256, ruta, detalles JSON, creado | Ver restricciones abajo |
| `MetricaCanal` | análisis FK, canal, min, max, media, std, pct_ceros | Único `(analisis, canal)` |
| `Explicacion` | análisis, método, versión, artefacto, SHA-256, fecha, datos JSON | Nulo hasta el Equipo 2 |
| `Notificacion` | usuario, tipo, mensaje, leída, URL, creada | — |
| `SolicitudRevision` | usuario, análisis, motivo, estado, respuesta, revisor, fechas | Estados `pendiente`, `aprobada`, `rechazada` |
| `AuditoriaAccion` | usuario, acción, objeto_tipo, objeto_id, detalles, IP, user_agent, fecha | Append-only |

Restricciones de integridad obligatorias:

- Si `estado == "completado"`: `resultado`, `puntuacion` y `umbral_aplicado` no nulos; `motivo_codigo` nulo.
- Si `estado` es de rechazo o error: `resultado`, `puntuacion` y `umbral_aplicado` **nulos**; `motivo_codigo` no nulo.
- `puntuacion` entre 0 y 1.
- Índices por `(estacion, t0_registro)`, `fecha_procesamiento`, `estado` y `usuario`.
- `AuditoriaAccion` no se actualiza ni se elimina desde la aplicación.

Estados propuestos: `completado`, `rechazado`, `error_adquisicion`, `error_inferencia`.

`VersionModelo` se poblará con un comando de gestión que verifique el inventario SHA-256; no se codificarán el umbral ni el hash a mano en las vistas.

### 13.6 Flujos principales

**Análisis en dos pasos:**

1. El usuario elige estación y ventana UTC.
2. `adquisicion` descarga MiniSEED, guarda bytes y SHA-256.
3. `adquisicion` valida frecuencia, canales, localización, continuidad, alineación y QC.
4. Si no es compatible: se persiste `rechazado`, se muestra el motivo y **no se importa TensorFlow**.
5. Si es compatible: se muestra “Comprobar compatibilidad” superado y se habilita “Clasificar”.
6. Al clasificar, se reutiliza el MiniSEED cacheado y se verifica su SHA-256.
7. `ia` preprocesa e infiere; `analisis` persiste resultado, métricas y versión del modelo.
8. La UI muestra puntuación, umbral, clase, hash, fecha y advertencias.

**Rechazo:**

- Código (`FS_NO_100`, `COMPONENTE_FALTANTE`, `MUESTRAS_INSUFICIENTES`, `HUECO`, `DESALINEADO`, `CANAL_CONSTANTE`, `MAYORIA_CEROS`, `TRAZAS_MULTIPLES`, `SIN_DATOS_204`, `ERROR_FDSN`, `MINISEED_ILEGIBLE`).
- Mensaje claro, en español, sin culpar al usuario.
- Registro en PostgreSQL con detalles técnicos.
- Sin resultado, sin puntuación, sin umbral aplicado.

**XAI:**

- Interfaz reservada: `generar_explicacion(analisis, modelo, tensor_normalizado)`.
- Estado inicial: “Explicación no disponible”.
- No se simula ni se inventa ninguna explicación.
- El método del Equipo 2 no puede modificar pesos, umbral ni arquitectura.

### 13.7 Decisiones de arquitectura pendientes

1. Usuario personalizado vs. `auth.User` + `Perfil`.
2. Unir trazas estrictamente contiguas o rechazar siempre.
3. Rechazar señales constantes/mayoría de ceros como QC adicional.
4. Retención de MiniSEED y limpieza de temporales.
5. Catálogo de eventos CENAIS dentro o fuera de V1.
6. Carga manual de archivos dentro o fuera de V1.
7. Notificaciones solo internas o también por correo.
8. Mapa SVG local o teselas externas.
9. Almacenar tensores normalizados para XAI o recalcularlos.
10. Modo de ejecución final: `runserver` de demo o servidor con estáticos.

### 13.8 Lo que no debe hacerse

- No crear una API pública ni instalar DRF.
- No usar CDN externos para CSS, JS, fuentes o iconos.
- No modificar pesos, umbral, estadísticas ni arquitectura del modelo.
- No sustituir el umbral por 0.5.
- No interpolar, rellenar, remuestrear ni normalizar por segmento.
- No simular explicaciones XAI.
- No presentar la puntuación como probabilidad calibrada.
- No afirmar predicción de terremotos ni alerta temprana.
- No tocar bases de datos ajenas a `sismodetect`.
- No copiar datos del proyecto del dataset sin autorización y verificación.

---

## 14. Plan de desarrollo por fases

Fechas orientativas desde el 2026-11-25 hasta el 2026-12-29. Las fases pueden solaparse si hay varias personas.

| Fase | Ventana | Entregables | Puerta de aceptación |
|---|---|---|---|
| F0. Entorno y configuración | 25–27 nov | Git, PostgreSQL `sismodetect`, rol, `psycopg`, `.env`, settings, apps esqueleto, usuario/perfil | `manage.py check`, conexión a PostgreSQL y migraciones iniciales correctas |
| F1. Núcleo de IA | 28 nov–3 dic | `gestor_modelos`, `procesamiento/cnn_v1`, `inferencia/cnn_v1`, pruebas y tensor dorado | Hashes, formas, umbral y rechazos probados sin Django |
| F2. Adquisición | 2–9 dic | Cliente FDSN, lector MiniSEED, catálogo, validador, fixtures y manejo de errores | Respuestas 200/204/404/5xx y ventanas 3000/3001/offset probadas |
| F3. Base de datos | 7–10 dic | Modelos, migraciones, restricciones, admin y comando de verificación de modelo | Un análisis completo y un rechazo persistidos correctamente |
| F4. Orquestación | 9–12 dic | Flujo en dos pasos, caché, hash, logging, historial y códigos de rechazo | Ningún rechazo importa TensorFlow ni guarda puntuación |
| F5. Interfaz | 10–19 dic | Layout, inicio, estaciones/mapa, búsqueda, análisis, resultado, historial, modelo | Flujo completo desde estación hasta resultado/historial |
| F6. Cuentas y administración | 14–18 dic | Login, roles, permisos, perfil, notificaciones internas, auditoría, solicitudes de revisión | Matriz de permisos probada por rol |
| F7. Pruebas y documentación | 19–29 dic | E2E, seguridad, regresión, manual de Windows, manual de usuario, revisión final | Criterios de aceptación de la sección 16 cumplidos |
| F8. XAI | Después del Equipo 2 | Interfaz de explicación, artefacto, versión y hash | Solo con método real; sin simulación |

**Hitos críticos:** F0 y F1 deben cerrarse antes de F4; F2 y F3 antes de F5. XAI no debe bloquear la entrega del núcleo.

---

## 15. Estimación realista para un mes

### 15.1 Esfuerzo por fase

| Fase | Persona-días |
|---|---:|
| F0. Entorno y configuración | 3 |
| F1. Núcleo de IA | 5 |
| F2. Adquisición | 6 |
| F3. Base de datos | 3 |
| F4. Orquestación | 3 |
| F5. Interfaz | 7 |
| F6. Cuentas y administración | 4 |
| F7. Pruebas y documentación | 5 |
| Colchón para imprevistos | 4 |
| **Total** | **40 persona-días** |

No incluye XAI (3–5 persona-días adicionales, después de la entrega del Equipo 2).

### 15.2 Escenarios

| Escenario | Duración estimada | Viabilidad |
|---|---|---|
| 1 desarrollador a tiempo completo | ~8 semanas | **No cabe en un mes** sin recortar Must |
| 2 desarrolladores | ~4 semanas | **Ajustado pero viable** si trabajan en paralelo y no hay bloqueos |
| 3 desarrolladores | ~3 semanas | **Cómodo**, con margen para pruebas y documentación |

### 15.3 Supuestos

- Los artefactos de la CNN siguen disponibles e íntegros.
- El Equipo 2 no bloquea la entrega del núcleo; XAI es posterior.
- No se implementa catálogo de eventos ni carga manual en V1.
- No se implementa panel administrativo propio; se usa Django admin.
- No se usan teselas externas ni CDN.
- PostgreSQL existente funciona y se obtienen credenciales.
- No hay cambios mayores en IRIS/EarthScope.

### 15.4 Recortes si el plazo se complica

1. Notificaciones por correo → solo internas.
2. Panel administrativo propio → Django admin.
3. Mapa con teselas → SVG local.
4. Catálogo de eventos → fuera de V1.
5. Carga manual → fuera de V1.
6. Unión de trazas → rechazar.
7. Exportación PDF → fuera de V1.
8. Auditoría visible → solo registro y consulta básica.

**Conclusión:** el flujo núcleo (FDSN → validación → CNN → resultado → historial) es alcanzable en un mes con 2–3 personas. El alcance completo con todas las funciones Should/Could no es realista con una sola persona.

---

## 16. Pruebas que deberán realizarse

### 16.1 IA

- Verificación SHA-256 de los 6 artefactos.
- Lectura de JSON/NPZ y comparación con valores congelados.
- Umbral leído del JSON; prueba que falle si aparece `0.5` literal.
- Forma `(3000, 3)`, orden ZNE y `float32`.
- Media por canal y estandarización contra un tensor dorado.
- Predicción de humo reproducible (`0.116811...`).
- Rechazo sin importar TensorFlow (comprobar `sys.modules`).
- Carga perezosa, caché por proceso y bloqueo de concurrencia.

### 16.2 Adquisición

- Ventana de 3000 muestras alineada.
- Respuesta de 3001 muestras con extremo final inclusivo.
- Respuesta de 3001 muestras con inicio 10 ms antes.
- Menos de 3000, más de 3001, huecos, máscaras, NaN/Inf.
- Frecuencia distinta de 100 Hz, canal faltante, localización incorrecta.
- Señal constante, mayoría de ceros, amplitud nula.
- Varias trazas contiguas y varias trazas no contiguas.
- HTTP 200, 204, 404, 5xx, timeout y respuesta ilegible.
- Reintentos, alternancia de hosts y límite de tamaño.
- Construcción de URL sin parámetros arbitrarios.
- SHA-256 del MiniSEED y conservación de bytes originales.

### 16.3 Base de datos

- Restricción: completado exige resultado, puntuación y umbral.
- Restricción: rechazado/error prohíben resultado, puntuación y umbral.
- Puntuación entre 0 y 1.
- Índices y unicidad.
- Migraciones desde cero y reversibilidad.
- Borrado protegido de estaciones/versiones con análisis asociados.
- Auditoría append-only.

### 16.4 Django e interfaz

- Login, logout, cambio de contraseña y permisos por rol.
- CSRF, formularios y validación de entrada.
- Flujo en dos pasos: compatibilidad y clasificación.
- Reutilización del MiniSEED y verificación de hash entre pasos.
- Historial con filtros; rechazos sin puntuación.
- Mensajes de rechazo claros y no culpabilizantes.
- Plantillas sin XSS; enlaces y estáticos locales.
- Responsive y accesibilidad básica.

### 16.5 Integración y extremo a extremo

- Fixtures MiniSEED y respuestas FDSN simuladas.
- Flujo completo con estación compatible.
- Flujo de rechazo sin TensorFlow.
- Admin: usuarios, catálogo, versiones y auditoría.
- Notificaciones internas y solicitudes de revisión.
- Estado “Explicación no disponible” sin simulación.

### 16.6 Seguridad y rendimiento

- `check --deploy` con `DEBUG=False`, `ALLOWED_HOSTS` y secretos por entorno.
- SSRF: no aceptar URLs arbitrarias.
- Path traversal en rutas MiniSEED.
- Límites de tamaño y timeouts.
- Tiempo de carga de TensorFlow y latencia de inferencia.
- Concurrencia de dos solicitudes simultáneas.
- Número de consultas por página.

### 16.7 Criterios de aceptación

- Ningún registro rechazado contiene clase, puntuación o umbral.
- Ningún rechazo importa TensorFlow.
- Ningún resultado usa un umbral distinto de `0.2927532196044922`.
- Ninguna explicación XAI se muestra si no existe método real.
- Ninguna página depende de CDN externos.
- Todos los mensajes de rechazo son claros y no culpabilizan al usuario.
- Los artefactos conservan sus hashes antes y después de las pruebas.

---

## 17. Archivos y componentes que deben protegerse

| Componente | Motivo | Regla |
|---|---|---|
| `ia/pesos/cnn_v1/mejor_modelo_cnn_v1.keras` | Modelo entrenado | Solo lectura; hash; respaldo externo; no editar |
| `ia/pesos/cnn_v1/estadisticas_normalizacion.npz` | Estadísticas congeladas | Solo lectura; nunca recalcular |
| `ia/pesos/cnn_v1/manifiesto_preprocesamiento.json` | Contrato de preprocesamiento | Solo lectura; hash |
| `ia/pesos/cnn_v1/seleccion_umbral_v1.json` | Umbral congelado | Solo lectura; nunca sustituir por 0.5 |
| `ia/pesos/cnn_v1/configuracion_entrenamiento.json` | Evidencia de entrenamiento | Solo lectura |
| `ia/pesos/cnn_v1/INFORME_FINAL_CNN_V1.md` | Métricas y limitaciones declaradas | Solo lectura; no recalcular ni reescribir |
| `ia/pesos/cnn_v1/inventario_sha256.json` | Inventario de integridad | Solo lectura; verificar antes de cargar |
| `documentacion/*.md` | Evidencia y trazabilidad | Append-only; no borrar auditorías |
| `db.sqlite3` | Base legada vacía | No eliminar sin autorización |
| `D:\Escuela\Posgre SQL\data` | Datos del servidor PostgreSQL | No tocar; solo `sismodetect`; backups |
| `.env` | Secretos y credenciales | Nunca en Git; permisos restringidos |
| `data/registros/` | MiniSEED original | Hash; retención; fuera de Git |
| `data/temporal/` | Archivos temporales | Limpieza periódica; fuera de Git |
| `tests/fixtures/` | Fixtures pequeños | Versionables; sin datos masivos |
| `.venv/` y `.idea/` | Entorno local | No versionar |
| Proyecto del dataset | Referencia externa | Solo lectura; no modificar |
| Repositorio Git | Código y configuración | Sin pesos, sin BD, sin datos, sin secretos |

Reglas de Git y respaldo:

- Inicializar Git y crear un remoto privado.
- Versionar código, migraciones, plantillas, CSS, JS, pruebas, documentación y fixtures pequeños.
- **No versionar** `.keras`, MiniSEED, bases de datos, `.env` ni temporales.
- Respaldar `ia/pesos/cnn_v1/` fuera del repositorio y verificar hashes al restaurar.
- Etiquetar la entrega y documentar la versión exacta del modelo.
- No reescribir la historia de una rama compartida.
- Revisar `.gitignore` para incluir `data/registros/` antes de crearla.

---

## 18. Decisiones que requieren autorización

1. Inicializar Git, crear remoto privado y hacer el primer commit.
2. Usar el PostgreSQL 18 existente; crear la base `sismodetect` y un rol dedicado.
3. Instalar `psycopg[binary]`, `obspy`, `pytest`, `pytest-django`, `pytest-cov` y `ruff`.
4. Modificar `config/settings.py`: PostgreSQL, `LANGUAGE_CODE='es'`, estáticos, logging, secretos por entorno.
5. Crear las apps `catalogo`, `adquisicion`, `analisis`, `cuentas` e `interfaz`.
6. Decidir usuario personalizado vs. `Perfil`.
7. Aprobar la regla de ventana y la política de trazas múltiples.
8. Aprobar el QC adicional de señales constantes/mayoría de ceros.
9. Definir `data/registros/`, retención y limpieza de temporales.
10. Confirmar el flujo de interfaz en dos pasos.
11. Cerrar el alcance: eventos, carga manual, notificaciones por correo y teselas de mapa.
12. Autorizar mockups con el generador de imágenes, si se desean.
13. Integrar XAI solo cuando el Equipo 2 entregue método, artefacto y versión.
14. Elaborar la documentación de Windows en la fase final.

---

## 19. Cierre

La auditoría confirma que:

- El proyecto es un esqueleto coherente y no requiere reconstrucción.
- La CNN V1 está íntegra, carga correctamente y su contrato está documentado.
- PostgreSQL está disponible como servidor, pero la integración con Django no existe.
- No hay apps, interfaz, adquisición, pipeline de IA ni pruebas.
- Los bloqueos principales son Git, PostgreSQL, dependencias de adquisición, modelo de usuario y regla de ventana.
- El plazo de un mes es viable para el flujo núcleo con 2–3 personas y control de alcance.

**Siguiente paso recomendado:** revisar este informe, cerrar las decisiones de la sección 18 y autorizar expresamente la Fase 0 de implementación. No se debe avanzar a implementación sin esa autorización.

---

**Fin del informe — Auditoría Fase 0**

