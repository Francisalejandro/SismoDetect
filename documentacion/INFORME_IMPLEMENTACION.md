# INFORME DE IMPLEMENTACIÓN — Fase 0

**Proyecto:** SismoDetect — Sistema web para la consulta, análisis y clasificación de señales sísmicas en Cuba mediante inteligencia artificial

> La explicabilidad se mantiene como funcionalidad complementaria del sistema.

| Campo | Valor |
|---|---|
| Fecha | 2026-11-27 (actualizado) |
| Fase | Fase 0 — Base técnica |
| Estado global | **Base técnica verificada y migrada**: 19/19 migraciones aplicadas; `cuentas_usuario` creada y `auth_user` ausente |
| Base de datos | PostgreSQL 18.7, base `sismodetect` — **10 tablas**, sin `auth_user` |
| Migraciones | **19/19 aplicadas** el 2026-11-27 01:40:51 (-05:00) |
| Git | **Inicializado y publicado** el 2026-11-27: rama `main`, primer commit `e4c00a0c7bbff45ab6cbb0134106ea33ce8d29ca` |
| Repositorio | https://github.com/Francisalejandro/SismoDetect |

> **Alcance respetado:** no se implementó adquisición sísmica, ni inferencia CNN, ni XAI, ni pantallas. No se modificaron los artefactos de `ia/pesos/cnn_v1/`, ni el dataset externo, ni `db.sqlite3`. No se creó ningún repositorio Git.

> **Nota de revisión documental (2026-11-27):** se corrigieron contradicciones sobre migraciones y tablas, se identificaron los documentos históricos, se actualizó `README.md`, se aclaró la advertencia sobre una migración cosmética y se documentó la fuente canónica de las particiones del dataset (sección 14). El detalle del admin está en `documentacion/REVISION_ADMIN_CUENTAS.md`.

---

## 1. Estado de la fase

| Requisito de la fase | Estado |
|---|---|
| Verificar entorno Python/Django | **IMPLEMENTADO Y VERIFICADO** |
| Revisar configuración PostgreSQL 18 | **IMPLEMENTADO Y VERIFICADO** (servidor activo) |
| Configurar Django para PostgreSQL (`sismodetect`) | **IMPLEMENTADO Y VERIFICADO** (conexión real correcta) |
| Estructura de apps `catalogo`, `adquisicion`, `analisis`, `cuentas`, `interfaz` | **IMPLEMENTADO Y VERIFICADO** |
| Apps registradas en Django | **IMPLEMENTADO Y VERIFICADO** (`manage.py check` sin incidencias) |
| Variables de entorno y secretos | **IMPLEMENTADO Y VERIFICADO** (`.env`, `.env.example`, `.gitignore`) |
| Dependencias actualizadas | **IMPLEMENTADO Y VERIFICADO** |
| Modelo de usuario personalizado (`AbstractUser`) | **IMPLEMENTADO Y VERIFICADO** en base de datos: tabla `cuentas_usuario` creada; `auth_user` no existe |
| Roles Administrador y Usuario | **IMPLEMENTADO** (definición de modelo y `CHECK` activos en PostgreSQL) |
| Documentación de ejecución en Windows | **IMPLEMENTADO** (sección 7 de este informe) |
| Base `sismodetect` y rol `sismodetect_app` | **IMPLEMENTADO Y VERIFICADO** (existentes; no creados ni modificados en esta fase) |
| Migraciones | **IMPLEMENTADO Y VERIFICADO**: 19/19 aplicadas, sin errores |

**Conclusión:** la configuración, la conexión y las migraciones iniciales están verificadas. La base contiene las 10 tablas esperadas y no contiene `auth_user`. No se han creado usuarios ni grupos.

---

## 2. Archivos creados

### 2.1 Aplicaciones Django

Creadas con `manage.py startapp` dentro de `apps/` y con `AppConfig` ajustado al paquete `apps.*`.

| Archivo | Contenido |
|---|---|
| `apps/catalogo/{__init__,admin,apps,models,tests,views}.py` | Esqueleto; `CatalogoConfig` → `apps.catalogo`, «Catálogo sísmico» |
| `apps/adquisicion/{__init__,admin,apps,models,tests,views}.py` | Esqueleto; `AdquisicionConfig` → `apps.adquisicion`, «Adquisición de señales» |
| `apps/analisis/{__init__,admin,apps,models,tests,views}.py` | Esqueleto; `AnalisisConfig` → `apps.analisis`, «Análisis y trazabilidad» |
| `apps/cuentas/{__init__,admin,apps,models,tests,views}.py` | `CuentasConfig` → `apps.cuentas`, «Cuentas y roles» |
| `apps/interfaz/{__init__,admin,apps,models,tests,views}.py` | Esqueleto; `InterfazConfig` → `apps.interfaz`, «Interfaz web» |
| `apps/*/migrations/__init__.py` | Paquete de migraciones vacío |

Los `models.py` de `catalogo`, `adquisicion`, `analisis` e `interfaz` están vacíos a propósito: no se adelantan funcionalidades.

### 2.2 Usuario personalizado

| Archivo | Contenido |
|---|---|
| `apps/cuentas/models.py` | `Usuario(AbstractUser)` con `rol` (`administrador` / `usuario`, por defecto `usuario`), `Meta` en español, `__str__` y propiedad `es_administrador` |
| `apps/cuentas/admin.py` | `UsuarioAdmin(BaseUserAdmin)` con columna y filtro de rol |

### 2.3 Configuración y entorno

| Archivo | Cambio |
|---|---|
| `config/settings.py` | Reescrito: `python-dotenv`, `SECRET_KEY` obligatoria por entorno, `DEBUG`/`ALLOWED_HOSTS` por entorno, PostgreSQL, `AUTH_USER_MODEL = "cuentas.Usuario"`, `LANGUAGE_CODE = "es"`, estáticos, `LOGGING` con rotación, apps propias registradas |
| `.env` | Creado con `SECRET_KEY` aleatoria, `DEBUG=True`, hosts locales y datos de conexión. **`DB_PASSWORD` configurado**; la conexión PostgreSQL fue verificada el 2026-11-26. El valor del secreto nunca se mostró ni se copió en la documentación |
| `.env.example` | Plantilla documentada sin secretos |
| `.gitignore` | Añadidas reglas para `data/registros/` y `logs/` |
| `requirements/base.txt` | `Django==6.1.3`, `psycopg[binary]==3.3.9`, `python-dotenv==1.2.4` |
| `requirements/tensorflow.txt` | Añadidos pins `keras==3.15.1`, `numpy==2.5.5`, `h5py==3.14.0` |

### 2.4 Carpetas base

| Ruta | Uso |
|---|---|
| `static/.gitkeep` | Estáticos del proyecto |
| `templates/.gitkeep` | Plantillas globales |
| `logs/.gitkeep` | Registro rotativo (ignorado por Git salvo el marcador) |
| `data/registros/.gitkeep` | Reservado para MiniSEED original (ignorado por Git) |

---

## 3. Dependencias añadidas

Instaladas en `.venv`:

| Paquete | Versión |
|---|---|
| `psycopg` | 3.3.9 |
| `psycopg-binary` | 3.3.9 |
| `python-dotenv` | 1.2.4 |

No se instaló nada más. Siguen ausentes, por no ser necesarias en esta fase: `obspy`, `pytest`, `pytest-django`, `pytest-cov`, `ruff`, `Pillow`, DRF.

---

## 4. Verificaciones ejecutadas

| Comprobación | Comando | Resultado |
|---|---|---|
| Entorno Python | `python -V` | 3.13.0 |
| Versión Django | `django.get_version()` | 6.1.3 |
| Servicio PostgreSQL | `Get-Service postgresql-x64-18` | Running / Automatic |
| Puertos PostgreSQL | `pg_isready -h localhost -p 5432` | «aceptando conexiones» |
| Comprobación Django | `manage.py check` | **0 incidencias** |
| Modelo de usuario | `get_user_model()` | `apps.cuentas.models.Usuario` |
| Roles definidos | `Usuario.Rol.choices` | `[("administrador","Administrador"), ("usuario","Usuario")]` |
| Motor de BD | `settings.DATABASES` | `django.db.backends.postgresql` |
| Nombre de BD | `settings.DATABASES` | `sismodetect` |
| Idioma | `settings.LANGUAGE_CODE` | `es` |
| Conexión real a PostgreSQL | `connection.ensure_connection()` | **CONEXION_OK**: `postgresql` |
| Usuario efectivo | `SELECT current_user` | `sismodetect_app` |
| Base efectiva | `SELECT current_database()` | `sismodetect` |
| Superusuario | `pg_roles.rolsuper` | **`False`** |
| `CREATEROLE` / `CREATEDB` | `pg_roles` | **`False`** / **`False`** |
| `CONNECT` sobre `sismodetect` | `has_database_privilege` | **`True`** |
| `USAGE` en `public` | `has_schema_privilege` | **`True`** |
| `CREATE` en `public` | `has_schema_privilege` | **`True`** |
| Tablas en `public` | `information_schema.tables` | **10** tras migrar (0 antes) |
| Comprobación Django con BD | `manage.py check --database default` | **0 incidencias** |
| Migraciones | `makemigrations cuentas` (con `LANGUAGE_CODE="en"` temporal) | Generó solo `apps/cuentas/migrations/0001_initial.py`; revisada |
| SQL de la migración | `sqlmigrate cuentas 0001` | `cuentas_usuario` + 2 tablas M2M; sin `auth_user` |
| Plan de migraciones | `showmigrations --plan` y `migrate --plan` | 19 migraciones; orden válido |
| Aplicación de migraciones | `python manage.py migrate` | **19/19 OK**, salida 0, 1.39 s |
| `auth_user` | `to_regclass('public.auth_user')` | **`NULL`** (no existe) |
| Integridad CNN V1 | Sin cambios | Artefactos intactos |

La contraseña se leyó desde `.env` y **no se mostró** en ningún momento. Las consultas de verificación fueron de solo lectura; la única escritura fue el `migrate` autorizado. El servidor informa **PostgreSQL 18.7**.

**Observación de privilegios:** el rol también tiene `CONNECT` sobre `postgres` y `medicamentos_cuba` por herencia de `PUBLIC`, no por un permiso concedido directamente. Revocar un permiso directo al rol no elimina lo que hereda de `PUBLIC`; cualquier cambio de ACL queda pendiente de autorización (sección 8, I11). No se ejecutó ningún `GRANT` ni `REVOKE`.

---

## 5. Conexión verificada con PostgreSQL

### 5.1 Resultado de la verificación (2026-11-26)

| Elemento | Valor comprobado |
|---|---|
| Motor | `django.db.backends.postgresql` |
| Base configurada | `sismodetect` |
| Usuario configurado | `sismodetect_app` |
| Host / puerto | `localhost` / `5432` |
| Conexión | **Correcta** |
| `current_user` | `sismodetect_app` |
| `current_database()` | `sismodetect` |
| Versión del servidor | PostgreSQL 18.7 |
| `rolsuper` | `False` |
| `rolcreaterole` / `rolcreatedb` | `False` / `False` |
| `CONNECT` sobre `sismodetect` | `True` |
| `USAGE` / `CREATE` en `public` | `True` / `True` |
| Tablas en `public` | Ninguna **en esa fecha**; tras el `migrate` del 2026-11-27 hay 10 |
| `manage.py check` | 0 incidencias |
| `manage.py check --database default` | 0 incidencias |

- La contraseña se cargó desde `.env` y no se imprimió.
- **En la verificación del 2026-11-26** no se ejecutaron migraciones. El `migrate` autorizado se ejecutó después, el 2026-11-27 (19/19 OK); el estado posterior está en la sección 13.
- En esa verificación no se creó, alteró ni eliminó ningún rol, base, tabla u objeto.
- `sismodetect_appwith` no se consultó ni se modificó.

### 5.2 Privilegios heredados de `PUBLIC`

`has_database_privilege` devolvió `True` también para `postgres` y `medicamentos_cuba`. Ese resultado proviene del privilegio que PostgreSQL concede por defecto al rol público `PUBLIC`, no de un permiso concedido directamente a `sismodetect_app`.

**Limitación importante:** en PostgreSQL los privilegios son aditivos. El conjunto efectivo de un rol incluye lo que se le concedió directamente **y** lo que hereda de `PUBLIC` (o de otros roles de los que sea miembro). Por tanto, intentar quitar el `CONNECT` únicamente a `sismodetect_app` no elimina el privilegio heredado: la herencia desde `PUBLIC` sigue otorgándolo. No se ha ejecutado ningún `GRANT` ni `REVOKE`.

Para restringir realmente el acceso a otras bases habría que modificar la ACL de `PUBLIC` en esas bases o aplicar una política equivalente a nivel de servidor. Esa acción afectaría a **todos** los roles que dependen de `PUBLIC`, no solo a `sismodetect_app`, por lo que queda **pendiente de autorización expresa** y debe evaluarla el administrador del servidor. Mientras tanto se documenta la limitación, sin presentar como solución una revocación dirigida solo al rol.

### 5.3 Pasos posteriores (estado real)

1. ~~Generar la migración inicial.~~ **Cumplido el 2026-11-27**: solo `cuentas.0001_initial`, revisada en `documentacion/REVISION_MIGRACION_CUENTAS.md`.
2. ~~Aplicar: `manage.py migrate`.~~ **Cumplido el 2026-11-27 01:40:51 (-05:00)**: 19/19 OK.
3. ~~Confirmar que existe `cuentas_usuario` y que **no** se creó `auth_user`.~~ **Cumplido**: `cuentas_usuario` existe; `auth_user` no.
4. ~~Verificar `django_migrations`, `django_content_type` y los índices/restricciones del modelo.~~ **Cumplido**: 19 filas en `django_migrations`, 6 tipos de contenido, 24 permisos, restricciones e índices correctos.
5. Crear el superusuario administrativo (solo si se autoriza). **Pendiente.**

---

## 6. Decisiones aplicadas

| Decisión | Implementación |
|---|---|
| Usuario personalizado `AbstractUser` | `apps.cuentas.models.Usuario`, registrado como `AUTH_USER_MODEL` **antes** de cualquier migración |
| Roles Administrador y Usuario | `TextChoices` con valor por defecto `usuario` |
| PostgreSQL 18, base `sismodetect` | `DATABASES` apunta a `sismodetect`; conexión verificada con `sismodetect_app` |
| Interfaz pública personalizada | No se usó ni configuró el login de Django; no hay pantallas todavía |
| Django Admin como herramienta interna | `Usuario` registrado en el admin |
| CNN V1 y dataset intactos | No se abrió ni escribió ningún artefacto |
| Migración inicial generada y aplicada | `cuentas.0001_initial` + 18 migraciones de Django; 10 tablas creadas |
| Repositorio Git | Inicializado y publicado en GitHub el 2026-11-27 (detalle en la sección 15) |
| Sin funcionalidades adelantadas | Apps vacías, sin vistas ni plantillas |

---

## 7. Cómo ejecutar en Windows

Requisitos previos: Python 3.13, PostgreSQL 18 en ejecución, proyecto en `D:\Escuela\Inteligencia Artificial\SismoDetect`.

```powershell
cd 'D:\Escuela\Inteligencia Artificial\SismoDetect'

# 1. Activar el entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias (si hace falta)
python -m pip install -r requirements\base.txt

# 3. Configurar variables de entorno
Copy-Item .env.example .env
# Editar .env: generar DJANGO_SECRET_KEY y poner DB_PASSWORD

# Generar una clave nueva (si se necesita)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Comprobar configuración
python manage.py check

# 5. Aplicar migraciones (ya aplicadas el 2026-11-27; repetir solo en una base nueva)
python manage.py makemigrations cuentas
python manage.py migrate

# 6. Crear superusuario (opcional, requiere autorización)
python manage.py createsuperuser

# 7. Ejecutar el servidor local
python manage.py runserver
```

Acceso: `http://127.0.0.1:8000/` (sin páginas todavía) y `http://127.0.0.1:8000/admin/`.

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Para añadir `psql` al `PATH` de la sesión:

```powershell
$env:Path += ';D:\Escuela\Posgre SQL\bin'
```

### 7.1 Variables de `.env`

| Variable | Ejemplo | Obligatoria |
|---|---|---|
| `DJANGO_SECRET_KEY` | cadena aleatoria | **Sí** |
| `DJANGO_DEBUG` | `True` | No (por defecto `False`) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | No |
| `DJANGO_TIME_ZONE` | `UTC` | No |
| `DB_NAME` | `sismodetect` | No |
| `DB_USER` | `sismodetect_app` | No |
| `DB_PASSWORD` | clave del rol | **Sí** para conectar |
| `DB_HOST` | `localhost` | No |
| `DB_PORT` | `5432` | No |

`settings.py` falla de forma explícita si `DJANGO_SECRET_KEY` no está definida.

---

## 8. Problemas pendientes

| ID | Problema | Impacto | Siguiente acción |
|---|---|---|---|
| I01 | ~~Base `sismodetect` y rol no verificados~~ | **RESUELTO** | Conexión verificada el 2026-11-26 |
| I02 | ~~`DB_PASSWORD` vacío en `.env`~~ | **RESUELTO** | Contraseña configurada por el usuario |
| I03 | ~~Migración inicial no generada~~ | **RESUELTO el 2026-11-27** | `cuentas.0001_initial` generada, revisada y aplicada; 19/19 migraciones OK |
| I12 | Creación de usuarios, superusuario temporal y grupo `Administradores` | Sin cuentas todavía | Requiere autorización expresa |
| I04 | `mail.E001` en `check --deploy` (backend de consola) | Solo afecta a correo real | Decidir si habrá correo; para local no bloquea |
| I05 | `DEBUG=True` y `SECRET_KEY` local | Aceptable en desarrollo | Endurecer antes de entrega |
| I06 | `obspy` y herramientas de prueba ausentes | Necesarias en fases 1–2 | Instalar cuando se autoricen |
| I07 | ~~`apps/__init__.py` menciona `catalogacion` y `api`~~ | **RESUELTO** | Docstring actualizado a las cinco apps reales |
| I08 | `README.md` desactualizado | Confusión menor | **RESUELTO el 2026-11-27**: actualizado al estado real (implementado / pendiente) |
| I09 | ~~Sin repositorio Git~~ | **RESUELTO el 2026-11-27** | Repositorio inicializado, primer commit creado y publicado en GitHub |
| I10 | `db.sqlite3` vacío conservado | Ninguno funcional | No eliminar sin autorización |
| I11 | `CONNECT` heredado de `PUBLIC` sobre `postgres` y `medicamentos_cuba` | El rol puede conectarse a bases ajenas aunque no tenga permisos sobre objetos | No se elimina revocando solo al rol; exige modificar la ACL de `PUBLIC` o la política del servidor. **Pendiente de autorización**; sin `GRANT`/`REVOKE` ejecutados |

---

## 9. Lo que NO se ha implementado (correctamente diferido)

- Modelos de catálogo, adquisición, análisis, notificaciones o auditoría.
- Cliente FDSN y descarga MiniSEED.
- Lector MiniSEED y validador de ventana.
- Carga de la CNN, preprocesamiento o inferencia.
- Vistas, formularios, plantillas, CSS, JS o mapa.
- Login/logout personalizados.
- XAI.
- Pruebas funcionales de `catalogo`, `adquisicion`, `analisis`, `interfaz` y del flujo completo con base migrada.
- Git.

### 9.1 Implementado que no forma parte de lo diferido

- **Pruebas automatizadas de cuentas:** 52 implementadas en `apps/cuentas/tests.py` (`SimpleTestCase`, sin base de datos).
- **Migraciones:** 19/19 aplicadas y **10 tablas** creadas en PostgreSQL el 2026-11-27. `cuentas_usuario` existe y `auth_user` no.

---

## 10. Criterio para cerrar la Fase 0

La fase se considerará cerrada cuando:

1. ~~`connection.ensure_connection()` devuelva `CONEXION_OK` contra `sismodetect`.~~ **Cumplido el 2026-11-26.**
2. ~~`manage.py migrate` aplique las migraciones sin errores.~~ **Cumplido el 2026-11-27 01:40:51 (-05:00)**: 19/19 OK.
3. ~~Exista la tabla `cuentas_usuario` y **no** exista `auth_user`.~~ **Cumplido**: `cuentas_usuario` existe; `auth_user` no.
4. ~~`manage.py check` siga sin incidencias.~~ **Cumplido el 2026-11-27**: 0 incidencias.
5. ~~La migración inicial exista y esté revisada.~~ **Cumplido el 2026-11-27** (`REVISION_MIGRACION_CUENTAS.md`).
6. ~~Este informe se actualice con los resultados reales de esos pasos.~~ **Cumplido el 2026-11-27.**

**Criterios técnicos de la Fase 0 cumplidos.** La Fase 0 fue cerrada oficialmente el 2026-11-27 por decisión del propietario.

---

## 11. Fase 1 — Modelo de usuarios (implementado; migraciones aplicadas, sin usuarios)

**Estado:** cambios aplicados y verificados el 2026-11-26. El 2026-11-27 se generó `cuentas.0001_initial` y se aplicaron las 19 migraciones. No se crearon usuarios ni grupos. No se ha iniciado formalmente la Fase 1.

El detalle completo está en **`documentacion/FASE_01_MODELO_USUARIOS.md`**. Esta sección resume las decisiones y su impacto.

### 11.1 Decisiones registradas

| ID | Decisión | Estado |
|---|---|---|
| D01 | Crear un superusuario **temporal** solo para la configuración inicial | Aprobada |
| D02 | Eliminar el superusuario temporal tras verificar el Administrador definitivo | Aprobada |
| D03 | El Administrador definitivo tendrá `rol="administrador"`, `is_staff=True` y acceso a `/admin/` | Aprobada |
| D04 | Todo superusuario de Django tendrá `rol="administrador"` | Aprobada e implementada |
| D05 | `es_administrador` reconocerá el rol y también `is_superuser` | Aprobada e implementada |
| D06 | `rol` se validará en la base con `CheckConstraint` | Aprobada e implementada |
| D07 | `is_staff` seguirá siendo el permiso de acceso al panel, independiente del rol funcional | Aprobada e implementada |
| D08 | `email` seguirá sin ser único en V1 | Aprobada |
| D09 | La cuenta definitiva será `is_superuser=False` y usará un grupo `Administradores` | Aprobada |

### 11.2 Corrección implementada

| Archivo | Cambio |
|---|---|
| `apps/cuentas/models.py` | `UsuarioManager.create_superuser()` asigna `rol="administrador"`; `save()` sincroniza el rol del superusuario y añade `rol` a `update_fields`; `es_administrador` contempla `is_superuser`; dos `CheckConstraint` (`rol` válido y coherencia superusuario/rol) |
| `apps/__init__.py` | Docstring actualizado a `catalogo`, `adquisicion`, `analisis`, `cuentas`, `interfaz` |
| `apps/cuentas/admin.py` | Restricciones iniciales; posteriormente reforzadas según la política aprobada (ver sección 12) |
| `apps/cuentas/tests.py` | 19 pruebas iniciales; ampliadas a 46 tras el refuerzo (ver sección 12) |

La migración `cuentas.0001` **incluye** los dos `CheckConstraint` y el gestor `UsuarioManager`. `save()` y la propiedad `es_administrador` no generan operaciones de migración.

**Verificación ejecutada en su momento:** `manage.py check`, `check --tag models` y `check --tag admin` → 0 incidencias; `manage.py test apps.cuentas` → 19/19 OK sin base de datos; 0 migraciones propias; ninguna tabla en `public` y ninguna base `test_*`. Tras el refuerzo de la sección 12 el resultado fue 46/46; tras la protección contra auto-desactivación es **52/52**.

### 11.3 Protocolo del superusuario temporal

1. ~~Aplicar migraciones.~~ **Cumplido el 2026-11-27** (19/19 OK).
2. `python manage.py createsuperuser` → `bootstrap_temp`; el manager le asigna `rol="administrador"`.
3. Con esa sesión, crear el grupo `Administradores` con permisos `add/change/view usuario` (sin `delete`; para retirar una cuenta se desmarca `is_active`).
4. Crear la cuenta definitiva en dos pasos: en el alta se asignan `username`, contraseña y `rol="administrador"`; tras guardar, Django abre la edición, donde se marca `is_staff=True`, se añade el grupo `Administradores` y se confirma `is_superuser=False`. `is_active` queda marcado por defecto.
5. Verificar inicio de sesión, acceso a `/admin/` y gestión de usuarios.
6. Exportar el `LogEntry` del temporal.
7. Eliminar `bootstrap_temp` y confirmar que ya no existe.
8. Volver a iniciar sesión con la cuenta definitiva y confirmar que todo sigue operativo.

**Advertencia:** `admin.LogEntry.user` es `CASCADE`; al borrar el temporal se pierden sus entradas de auditoría. Deben exportarse antes y registrarse en `FASE_01_MODELO_USUARIOS.md`.

### 11.4 Riesgo detectado si se migraba sin generar `cuentas.0001`

Antes de generar la migración, el plan fallaba al resolver la FK de `admin.LogEntry`:

```text
ValueError: The field admin.LogEntry.user was declared with a lazy reference
to 'cuentas.usuario', but app 'cuentas' isn't installed.
```

**Resuelto el 2026-11-27** con la generación de `cuentas.0001_initial`. El orden aplicado fue: `makemigrations cuentas` → revisar → `migrate` (19/19 OK).

### 11.5 Estado de la Fase 1

| Elemento | Estado |
|---|---|
| Código del modelo | Implementado y verificado |
| Manager y restricciones | Implementados; incluidos en `cuentas.0001_initial` y presentes en PostgreSQL |
| Restricciones del admin | Implementadas y reforzadas (sección 12) |
| Pruebas | 19/19 iniciales; 46/46 tras el refuerzo; 52/52 tras la protección anti auto-desactivación (sección 12) |
| `manage.py check` | 0 incidencias |
| Migraciones | **19/19 aplicadas** el 2026-11-27 01:40:51 (-05:00) |
| Superusuario temporal | No creado |
| Administrador definitivo | No creado |
| Grupo `Administradores` | No creado |
| Documentación | Actualizada (`FASE_01_MODELO_USUARIOS.md`, `REVISION_MIGRACION_CUENTAS.md`) |
| Autorización para crear usuarios | **Pendiente** |

**Siguiente paso:** autorización expresa para crear el superusuario temporal y el grupo `Administradores`.

---

## 12. Refuerzo de seguridad del panel de administración

**Estado:** implementado y verificado el 2026-11-26 como **continuación de la Fase 0**. No implica el inicio formal de la Fase 1 y no declara cerrada ninguna fase.

El detalle previo está en `documentacion/REVISION_ADMIN_CUENTAS.md`; el plan de Fase 1 en `documentacion/FASE_01_MODELO_USUARIOS.md`.

### 12.1 Política de permisos implementada

| Tipo de cuenta | Permisos efectivos en `/admin/` |
|---|---|
| Superusuario temporal | Gestiona todas las cuentas; crea y configura al administrador definitivo; asigna `rol`, `is_staff`, `is_superuser`, grupos y permisos; gestiona otros superusuarios |
| Administrador normal | Accede al panel; crea, consulta, edita y gestiona **usuarios normales** y su propia cuenta; no ve ni modifica otros administradores; no cambia contraseñas, `is_active` ni datos de otros administradores; **no puede desactivar su propia cuenta**; no borra usuarios; no crea administradores ni superusuarios; no modifica campos reservados ni `last_login`/`date_joined`; no gestiona grupos ni permisos de Django; puede cambiar su propia contraseña |
| Usuario normal | Sin acceso al panel; no gestiona cuentas |

### 12.2 Archivos modificados

| Archivo | Cambio |
|---|---|
| `apps/cuentas/admin.py` | Lista blanca de campos por rol; `get_queryset` excluye otros administradores; `has_view_permission`, `has_change_permission` y `has_delete_permission` reforzados; `user_change_password` protegido; `save_model` y `save_related` imponen la política en el servidor; `get_readonly_fields` bloquea fechas y `is_active` en la propia cuenta; `get_actions` retira `delete_selected` |
| `apps/cuentas/tests.py` | Ampliado de 19 a 52 pruebas `SimpleTestCase`, sin base de datos |

No se modificó `models.py`, `settings.py`, `.env` ni ningún otro archivo de código.

### 12.3 Cambios concretos en `apps/cuentas/admin.py`

- `get_queryset()`: para no superusuarios devuelve solo la propia cuenta y usuarios con `is_superuser=False` y `rol != "administrador"`.
- `get_fieldsets()` y `get_form()`: para no superusuarios usan listas blancas distintas para alta y edición. El formulario no puede contener `rol`, `is_staff`, `is_superuser`, `groups`, `user_permissions`, `last_login` ni `date_joined`.
- `get_readonly_fields()`: `last_login` y `date_joined` son de solo lectura para no superusuarios; `is_active` también lo es al editar la propia cuenta.
- `has_view_permission()` / `has_change_permission()`: deniegan cualquier administrador distinto del propio usuario.
- `has_delete_permission()`: siempre `False` para no superusuarios; `get_actions()` elimina `delete_selected`.
- `user_change_password()`: antes de delegar en Django, verifica que el objetivo no sea otro administrador; permite la propia contraseña y la de usuarios normales.
- `save_model()`: al crear usuario lo fuerza a `rol="usuario"`, `is_staff=False`, `is_superuser=False`; al editar usuario normal mantiene esos valores; al editar otro administrador lanza `PermissionDenied`; permite editar la propia cuenta salvo que se intente guardarla con `is_active=False`, caso en que lanza `PermissionDenied`.
- `save_related()`: al crear usuario limpia `groups` y `user_permissions`.

El superusuario temporal conserva todos los campos y capacidades: `get_queryset` sin filtro, campos reservados disponibles en edición, `rol` disponible en alta, permisos de cambio/borrado y delegación directa en `user_change_password`.

### 12.4 Pruebas ejecutadas y resultados reales

| Comando | Resultado |
|---|---|
| `manage.py check` | 0 incidencias |
| `manage.py check --tag models` | 0 incidencias |
| `manage.py check --tag admin` | 0 incidencias |
| `manage.py check --database default` | 0 incidencias |
| `manage.py test apps.cuentas -v 1` | **52/52 OK** en 0.079 s |
| Base de datos en pruebas | `Skipping setup of unused database(s): default` |
| Tablas en `public` | Ninguna **en la verificación del 2026-11-26**; tras el `migrate` del 2026-11-27 hay 10 |
| Bases `test_*` | Ninguna |
| Migraciones propias | 0 archivos **en esa fecha**; el 2026-11-27 se añadió `cuentas.0001_initial` |

> **Nota:** los resultados de esta tabla corresponden a la verificación del 2026-11-26, **antes** de generar `cuentas.0001_initial`. El estado posterior a la migración está en la sección 13.

Cobertura añadida: consulta filtrada, denegación de ver/editar/borrar, contraseña de otro administrador, contraseña propia, campos de formulario por alta y edición, campos de solo lectura, acciones de borrado, `save_model` y `save_related`, acceso al panel de usuario normal y protección contra auto-desactivación, incluida una llamada directa a `save_model()` con un `formulario` simulado.

### 12.5 Limitaciones y comprobaciones pendientes

- Las pruebas son `SimpleTestCase` con mocks: verifican lógica y rutas, **no** persistencia real.
- No se ejecutó HTTP real contra `/admin/`; todavía no hay usuarios.
- No se verificó el grupo `Administradores` en base: debe crearse solo con `add_usuario`, `change_usuario`, `view_usuario` y sin permisos `auth.*`.
- Los dos `CheckConstraint` ya existen en PostgreSQL con sus nombres exactos; falta comprobar el rechazo real con un `INSERT` inválido (no autorizado).
- La aclaración documental del flujo alta → edición ya está incorporada en `FASE_01_MODELO_USUARIOS.md` (sección 4.3) y en la sección 11.3 de este informe; lo pendiente es su **ejecución y verificación real** con usuarios.
- Sigue vigente el riesgo operativo: tras eliminar al superusuario temporal no habrá superusuarios; crear uno exigirá consola/`createsuperuser`.
- El 2026-11-27 se ejecutó `makemigrations` solo para `cuentas` y después `migrate` (19/19 OK); no se crearon usuarios; no se ejecutaron `GRANT`/`REVOKE`; no hubo commits ni push.

### 12.6 Protección contra auto-desactivación del administrador normal

**Implementado.** La recomendación registrada en la auditoría anterior fue autorizada y aplicada. Un administrador normal ya **no puede desactivar su propia cuenta**.

La protección se aplica en dos capas:

1. **Formulario:** `get_readonly_fields()` añade `is_active` a los campos de solo lectura cuando el objeto editado es la propia cuenta y quien edita no es superusuario. `get_form()` excluye ese campo, por lo que un valor enviado en un POST manipulado es ignorado.
2. **Servidor:** `save_model()` comprueba, antes de guardar, si el objeto es la propia cuenta y llega con `is_active=False`. En ese caso lanza `PermissionDenied`, aunque el valor provenga de una petición manipulada o de un `formulario` simulado que afirme lo contrario.

Detalle de la barrera de servidor:

```python
if (
    change
    and self._es_propia_cuenta(request.user, obj)
    and not getattr(obj, "is_active", True)
):
    raise PermissionDenied(
        "Un administrador normal no puede desactivar su propia cuenta."
    )
```

La comprobación usa `_es_propia_cuenta()`, que compara la clave primaria del usuario autenticado con la del objeto y exige `is_authenticated=True`. Solo se aplica a no superusuarios: el superusuario temporal conserva su comportamiento anterior, incluida la posibilidad de desactivarse si lo decide.

El cambio de contraseña propia sigue funcionando porque transcurre por `user_change_password()`, no por `save_model()`. Los administradores normales pueden seguir desactivando **usuarios normales**; la restricción afecta únicamente a su propia cuenta.

**Comprobación ejecutada:** `manage.py check` → 0 incidencias; `manage.py test apps.cuentas -v 1` → **52/52 OK**.

---

## 13. Migración inicial `cuentas.0001_initial` (generada y aplicada el 2026-11-27)

**Estado:** generada, revisada y **aplicada**. PostgreSQL contiene las 10 tablas previstas y no contiene `auth_user`.

### 13.1 Método de generación

El proyecto usa `LANGUAGE_CODE = "es"`. Con ese idioma, el autodetector propone además migraciones accesorias de `auth` y `contenttypes` (solo textos traducidos). Para generar exclusivamente `cuentas.0001` se usó un módulo de ajustes temporal **fuera del proyecto**:

```python
from config.settings import *  # noqa: F401,F403

LANGUAGE_CODE = "en"
```

Comando ejecutado:

```powershell
$env:PYTHONPATH = 'C:\Users\Francis\AppData\Local\Temp\opencode'
python manage.py makemigrations cuentas --settings=settings_en
```

`config/settings.py` **no** se modificó. El módulo temporal se eliminó al finalizar.

### 13.2 Resultado

| Dato | Valor |
|---|---|
| Archivo | `apps/cuentas/migrations/0001_initial.py` (único creado) |
| Tamaño | 3 416 bytes, 45 líneas |
| SHA-256 | `979660A2426E49CA03B379B8A09153AA22D1DA88E23664414862DDA4ADD69052` |
| Operaciones | 1 `CreateModel Usuario` |
| Campos | 14 (`AbstractUser` + `rol` + 2 M2M) |
| Restricciones | `cuentas_usuario_rol_valido`, `cuentas_usuario_superusuario_administrador` |
| Gestor | `UsuarioManager` (heredado `use_in_migrations=True`) |
| Dependencia | `('auth', '0012_alter_user_first_name_max_length')` |
| Tabla | `cuentas_usuario` |

### 13.3 Verificaciones previas a la aplicación

| Comando | Resultado |
|---|---|
| `manage.py check` | 0 incidencias |
| `manage.py test apps.cuentas -v 1` | **52/52 OK** en 0.028 s |
| `manage.py sqlmigrate cuentas 0001` | Tabla principal, 2 tablas M2M, 2 `CHECK`, FK e índices correctos; sin `auth_user` |
| `manage.py showmigrations --plan` | 19 migraciones pendientes; grafo válido |
| `manage.py migrate --plan` | Orden correcto (`cuentas.0001` tras `auth.0012`) |
| `sqlmigrate auth 0001` | Crea `auth_permission`, `auth_group` y `auth_group_permissions`; **0 apariciones de `auth_user`** |
| `public` en PostgreSQL (antes) | **0 tablas** |

### 13.4 Limitación conocida y aclaración sobre una futura migración cosmética

Como el archivo se generó con `LANGUAGE_CODE="en"`, los `verbose_name` y `help_text` heredados quedaron en inglés. No afectan al esquema ni al funcionamiento.

La revisión de `REVISION_MIGRACION_CUENTAS.md` (hallazgo H02) advirtió, **por inspección**, de que un futuro `makemigrations` con el idioma normal (`es`) podría proponer `cuentas.0002_alter_usuario_*` con 12 `AlterField` cosméticos. Esa advertencia **no se ha reproducido con la configuración real**: el 2026-11-27, ya aplicada `cuentas.0001`, `manage.py makemigrations --check --dry-run` y `manage.py makemigrations cuentas --dry-run` respondieron `No changes detected`. Por tanto, no debe afirmarse que `0002` se generará necesariamente.

Si en el futuro el autodetector propone una migración de ese tipo, debe revisarse su contenido y su SQL antes de generarla o aplicarla; no ejecutarla a ciegas. Detalle en `documentacion/REVISION_MIGRACION_CUENTAS.md` (H02) y `documentacion/INVESTIGACION_AUTODETECTOR_MIGRACIONES.md`.

### 13.5 Aplicación de las migraciones (2026-11-27)

Comprobaciones previas: base `sismodetect`, usuario `sismodetect_app`, esquema `public` con 0 tablas, sin `django_migrations`, `check` sin incidencias y plan de 19 migraciones coincidente con el revisado.

```powershell
python manage.py migrate
```

| Dato | Valor |
|---|---|
| Inicio | 2026-11-27 01:40:51 (-05:00) |
| Fin | 2026-11-27 01:40:52 (-05:00) |
| Duración | 1.39 s |
| Código de salida | 0 |
| Errores / advertencias | Ninguno |
| Migraciones aplicadas | **19/19** |

Resultado posterior:

| Comprobación | Resultado |
|---|---|
| `django_migrations` | Existe; **19 filas** |
| `showmigrations` | 19/19 marcadas `[X]` |
| Tablas en `public` | **10**: `auth_group`, `auth_group_permissions`, `auth_permission`, `cuentas_usuario`, `cuentas_usuario_groups`, `cuentas_usuario_user_permissions`, `django_admin_log`, `django_content_type`, `django_migrations`, `django_session` |
| `cuentas_usuario` | Existe; 12 columnas |
| `cuentas_usuario_groups` / `..._user_permissions` | Existen, con FK y unicidad por par |
| `cuentas_usuario_rol_valido` | Presente como `CHECK` |
| `cuentas_usuario_superusuario_administrador` | Presente como `CHECK` |
| `auth_user` | **No existe** (`to_regclass` → `NULL`) |
| `django_content_type` / `auth_permission` | 6 / 24 filas (generadas por `post_migrate`) |
| `auth_group` / `cuentas_usuario` | **0 / 0** (no se crearon cuentas ni grupos) |
| `manage.py check` | 0 incidencias |
| `manage.py test apps.cuentas -v 1` | **52/52 OK** en 0.034 s |

**La Fase 0 está oficialmente cerrada desde el 2026-11-27. No se ha creado ningún usuario ni grupo y no se autoriza iniciar otra fase.**

---

## 14. Dataset externo y fuente canónica de las particiones (2026-11-27)

### 14.1 Ubicación

La copia local del dataset utilizada para entrenar y evaluar la CNN V1 se encuentra **fuera del repositorio SismoDetect**, en:

```text
D:\Escuela\Inteligencia Artificial\Dataset\dataset_sismico_cubano
```

Esta ruta se verificó durante la auditoría de solo lectura del 2026-11-27. **No forma parte del repositorio**: SismoDetect no copia, versiona ni redistribuye el dataset. Si la carpeta se mueve en otro equipo, esta referencia debe actualizarse.

### 14.2 Fuente canónica de la partición

- La fuente canónica de la partición final utilizada por la CNN V1 es **`colab/splits_alternativo.csv`**, y la columna vigente es **`split_alternativo`**.
- Su resumen está en **`colab/split_alternativo_resumen.json`**: 1245 segmentos de entrenamiento, 155 de validación y 155 de prueba.
- El dataset principal tiene 1555 segmentos (827 sismo / 728 ruido), 3 canales `HHZ;HHN;HHE` procesados en orden Z, N, E, 100 Hz y 3000 muestras por segmento.

### 14.3 Advertencia sobre otras fuentes

- **`metadata.csv`** contiene **1383 filas** y **no cubre** los 1555 identificadores del split final. Parece una versión anterior o incompleta y no debe usarse como fuente de la partición.
- El mismo CSV conserva una columna antigua **`split`** con 1292/123/140, que **no debe confundirse** con `split_alternativo`. Solo esta última coincide con el resumen y con la partición usada por la CNN.
- No se modificó ningún CSV, JSON ni archivo del dataset durante esta revisión.

**Conclusión:** para reproducir la partición de la CNN V1, usar `colab/splits_alternativo.csv` (columna `split_alternativo`) y contrastar con `colab/split_alternativo_resumen.json`. `metadata.csv` y la columna `split` son referencias históricas, no la fuente vigente.

---

## 15. Publicación inicial en GitHub (2026-11-27)

Con autorización expresa del propietario se completó la primera publicación del proyecto, conservando el estado técnico validado de la Fase 0.

| Elemento | Resultado comprobado |
|---|---|
| Repositorio local | Inicializado con `git init -b main`; sin historial previo que sobrescribir |
| Remoto | `origin` → `https://github.com/Francisalejandro/SismoDetect.git`; el remoto estaba vacío |
| Primer commit | `e4c00a0c7bbff45ab6cbb0134106ea33ce8d29ca` — `chore: initial publication of SismoDetect` |
| Contenido publicado | 82 archivos; ~0.88 MiB; 7044 inserciones |
| Publicación | `git push -u origin main` correcto; sin `--force` |
| Sincronización | `main` = `origin/main` = commit anterior; árbol de trabajo limpio |
| CNN V1 | Los seis artefactos y su inventario aparecen en el repositorio; SHA-256 6/6 correctos también en el índice Git |
| Exclusiones | `.env`, `.venv/`, `.idea/`, `__pycache__/`, `db.sqlite3`, logs, cachés y datos sísmicos locales no fueron publicados |

El detalle de preparación, reglas de `.gitignore`, contenido de `.gitattributes` y verificaciones está en `documentacion/INFORME_PREPARACION_GIT.md`.

**La Fase 0 está oficialmente cerrada. No se ha iniciado la Fase 1.**
