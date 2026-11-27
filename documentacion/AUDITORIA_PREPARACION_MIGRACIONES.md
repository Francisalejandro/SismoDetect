# Auditoría y preparación de migraciones iniciales — SismoDetect

> **Documento histórico.** Esta auditoría se realizó el **2026-11-26**, antes de generar y aplicar `cuentas.0001_initial`. Refleja el estado previo: 0 tablas en `public` y 19 migraciones pendientes. Se conserva como registro del análisis que precedió a la migración y **no representa el estado actual**. El estado vigente está en `documentacion/INFORME_IMPLEMENTACION.md`.

**Proyecto:** SismoDetect — Sistema web para la consulta, análisis y clasificación de señales sísmicas en Cuba mediante inteligencia artificial

> La explicabilidad se mantiene como funcionalidad complementaria del sistema.

| Campo | Valor |
|---|---|
| Fecha | 2026-11-26 |
| Fase | Fase 0 — Base técnica (**continúa abierta**) |
| Alcance | Auditoría de solo lectura; sin `makemigrations` ni `migrate` |
| Django | 6.1.3 |
| PostgreSQL | 18.7, base `sismodetect`, sin tablas de aplicación |

---

## 1. Estado actual de la configuración Django

`config/settings.py` fue revisado íntegramente. Puntos relevantes:

| Elemento | Estado |
|---|---|
| `ENGINE` | `django.db.backends.postgresql` |
| `NAME` | `sismodetect` |
| `USER` | `sismodetect_app` |
| `AUTH_USER_MODEL` | `cuentas.Usuario` (línea 126) |
| `DEFAULT_AUTO_FIELD` | `django.db.models.BigAutoField` |
| `LANGUAGE_CODE` | `es` |
| `USE_TZ` | `True` |
| `INSTALLED_APPS` | 5 apps propias + 6 apps de Django |
| Secretos | Leídos de `.env`; no se imprimieron ni se modificaron |

`INSTALLED_APPS` y las configuraciones verificadas:

| Entrada | AppConfig | Label | Modelos propios |
|---|---|---|---|
| `apps.cuentas` | `CuentasConfig` | `cuentas` | `cuentas.Usuario` |
| `apps.catalogo` | `CatalogoConfig` | `catalogo` | Ninguno |
| `apps.adquisicion` | `AdquisicionConfig` | `adquisicion` | Ninguno |
| `apps.analisis` | `AnalisisConfig` | `analisis` | Ninguno |
| `apps.interfaz` | `InterfazConfig` | `interfaz` | Ninguno |
| `django.contrib.admin` | `AdminConfig` | `admin` | `LogEntry` |
| `django.contrib.auth` | `AuthConfig` | `auth` | `Permission`, `Group`, `User` (sustituido) |
| `django.contrib.contenttypes` | `ContentTypesConfig` | `contenttypes` | `ContentType` |
| `django.contrib.sessions` | `SessionsConfig` | `sessions` | `Session` |
| `django.contrib.messages` | — | `messages` | Sin modelos |
| `django.contrib.staticfiles` | — | `staticfiles` | Sin modelos |

No hay etiquetas de app duplicadas. Solo `cuentas` tiene un modelo propio; los otros cuatro paquetes `apps.*` tienen `models.py` vacío y no generarán migraciones.

No se encontraron referencias a `get_user_model`, `AUTH_USER_MODEL` ni `settings.AUTH_USER_MODEL` en el código de las apps propias fuera de `config/settings.py`. No existen modelos propios adicionales que dependan del usuario.

---

## 2. Estado de `AUTH_USER_MODEL`

| Comprobación | Resultado |
|---|---|
| Valor configurado | `cuentas.Usuario` |
| `get_user_model()` | `apps.cuentas.models.Usuario` |
| `_meta.label` | `cuentas.Usuario` |
| `_meta.db_table` | `cuentas_usuario` |
| `_meta.abstract` / `swapped` / `proxy` | `False` / `None` / `False` |
| `USERNAME_FIELD` | `username` |
| `REQUIRED_FIELDS` | `['email']` |
| `auth.User._meta.swapped` | `cuentas.Usuario` |
| `admin.LogEntry.user` | FK a `cuentas.Usuario`, `on_delete=CASCADE` |

La etiqueta `cuentas` coincide con `CuentasConfig.name = "apps.cuentas"`. El modelo es concreto y está correctamente registrado antes de cualquier migración. `auth.User` queda sustituido, por lo que no se creará la tabla `auth_user`.

---

## 3. Inventario de migraciones existentes

### 3.1 Migraciones propias

```text
apps/catalogo/migrations/      __init__.py  (sin 0*.py)
apps/adquisicion/migrations/   __init__.py  (sin 0*.py)
apps/analisis/migrations/      __init__.py  (sin 0*.py)
apps/cuentas/migrations/       __init__.py  (sin 0*.py)
apps/interfaz/migrations/      __init__.py  (sin 0*.py)
```

**Total de migraciones propias: 0.**

### 3.2 Migraciones de Django incluidas en el entorno

| App | Migraciones |
|---|---|
| `admin` | `0001_initial`, `0002_logentry_remove_auto_add`, `0003_logentry_add_action_flag_choices` |
| `auth` | `0001_initial`, `0002_alter_permission_name_max_length`, `0003_alter_user_email_max_length`, `0004_alter_user_username_opts`, `0005_alter_user_last_login_null`, `0006_require_contenttypes_0002`, `0007_alter_validators_add_error_messages`, `0008_alter_user_username_max_length`, `0009_alter_user_last_name_max_length`, `0010_alter_group_name_max_length`, `0011_update_proxy_permissions`, `0012_alter_user_first_name_max_length` |
| `contenttypes` | `0001_initial`, `0002_remove_content_type_name` |
| `sessions` | `0001_initial` |

**Total para apps instaladas: 18.** `messages` y `staticfiles` no tienen migraciones.

La tabla `django_migrations` **no existe**: la base está vacía.

---

## 4. Dependencias entre aplicaciones

Dependencias confirmadas leyendo los archivos de migración y el grafo:

```text
contenttypes.0001_initial                              → (ninguna)
sessions.0001_initial                                  → (ninguna)
auth.0001_initial                                      → contenttypes.__first__
admin.0001_initial                                     → cuentas.__first__, contenttypes.__first__
cuentas.0001_initial (a generar)                       → auth (grupos y permisos)
```

Detalles:

- `admin.0001_initial` declara `migrations.swappable_dependency(settings.AUTH_USER_MODEL)`, que resuelve a `("cuentas", "__first__")`.
- `auth.0001_initial` declara `("contenttypes", "__first__")`.
- `auth.0001_initial` crea `User` con `options={"swappable": "AUTH_USER_MODEL"}`, por lo que esa operación se omite con el modelo personalizado.
- `Usuario.groups` y `Usuario.user_permissions` son M2M hacia `auth.Group` y `auth.Permission`, por lo que `cuentas.0001` depende de `auth`.
- No hay ciclo: `auth` no depende de `cuentas`; `admin` depende de `cuentas`; `cuentas` depende de `auth`; `auth` depende de `contenttypes`.

### 4.1 Estado actual del grafo

`python manage.py showmigrations --plan` **falla en este momento**:

```text
ValueError: Dependency on app with no migrations: cuentas
```

Causa: `admin.0001` depende de `cuentas.__first__`, pero `apps/cuentas/migrations/` solo contiene `__init__.py`. Mientras no exista `cuentas.0001`, el grafo no puede construirse y, por tanto, `migrate` tampoco podría ejecutarse correctamente.

La forma de evitar el error de la FK de `admin.LogEntry` **no es editar la migración de Django**, sino generar primero `cuentas.0001_initial`: así la dependencia swappable apunta a una migración real y el estado puede renderizar `admin.LogEntry.user` como FK a `cuentas.Usuario`.

---

## 5. Análisis de la migración inicial de `cuentas`

No se creó el archivo. La descripción siguiente procede de la introspección del modelo y de una sonda en memoria con `MigrationAutodetector`, sin escribir archivos.

### 5.1 Nombre y dependencias

- Nombre esperado: `cuentas/0001_initial.py`.
- Dependencia esperada: la hoja vigente de `auth` en el momento de generarla (actualmente `auth.0012_alter_user_first_name_max_length`), porque los campos M2M apuntan a `auth.Group` y `auth.Permission`.
- La sonda con estado vacío resolvió `("auth", "__first__")`; con el grafo real, Django resuelve la dependencia según sus reglas de grafo.
- La sonda con el estado completo también propuso cambios menores en `auth` y `contenttypes` (principalmente opciones de verbose name y campos automáticos). Por eso, el archivo generado debe revisarse antes de aplicarlo: si aparecen migraciones de otras apps, hay que detenerse y pedir instrucciones.

### 5.2 Operación principal

Se espera una operación `CreateModel` de `Usuario` con:

| Grupo | Campos |
|---|---|
| Herencia de `AbstractUser` | `id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined` |
| Campo propio | `rol` |
| Relaciones M2M | `groups`, `user_permissions` |

Detalles confirmados:

- `id`: `BigAutoField`, acorde con `DEFAULT_AUTO_FIELD`.
- `username`: `CharField(max_length=150, unique=True)`; se crea un índice único.
- `email`: `EmailField(max_length=254, blank=True)`, **no único** (decisión D08).
- `rol`: `CharField(max_length=20, choices=[('administrador','Administrador'), ('usuario','Usuario')], default='usuario')`.
- `groups`: M2M a `auth.Group`, tabla intermedia `cuentas_usuario_groups`.
- `user_permissions`: M2M a `auth.Permission`, tabla intermedia `cuentas_usuario_user_permissions`.
- Opciones: `verbose_name='usuario'`, `verbose_name_plural='usuarios'`.

### 5.3 Restricciones

Se esperan dos `CheckConstraint` dentro de las opciones del `CreateModel` (en Django 6.1 la sonda las ubicó en `options`, no como operaciones `AddField`/`AddConstraint` separadas):

| Nombre | Condición |
|---|---|
| `cuentas_usuario_rol_valido` | `rol IN ('administrador','usuario')` |
| `cuentas_usuario_superusuario_administrador` | `is_superuser = False OR rol = 'administrador'` |

Índices esperados: clave primaria sobre `id`, índice único sobre `username` y restricciones de unicidad en las dos tablas intermedias M2M.

### 5.4 Gestor

`Usuario.objects` es `UsuarioManager`. Se verificó que `UserManager.use_in_migrations = True`, por lo que la migración debe serializar el gestor:

```python
managers=[("objects", apps.cuentas.models.UsuarioManager())]
```

Esto no requiere código adicional: `UsuarioManager` es importable y no necesita argumentos de deconstrucción.

### 5.5 Compatibilidad con Django 6.1.3

- `CheckConstraint(condition=...)` es la firma correcta en Django 6.1.
- `BigAutoField` es el valor por defecto declarado.
- El modelo es concreto, no proxy y no está sustituido.
- La migración no debe contener operaciones sobre `auth.User`, porque está swappeado.

---

## 6. Orden recomendado de migración

Una vez autorizado:

1. `python manage.py check` (ya pasa).
2. `python manage.py makemigrations cuentas`.
3. **Revisar** `apps/cuentas/migrations/0001_initial.py` antes de cualquier aplicación.
4. `python manage.py sqlmigrate cuentas 0001`.
5. `python manage.py showmigrations --plan`.
6. `python manage.py migrate --plan`.
7. `python manage.py migrate`.
8. Verificar tablas y ausencia de `auth_user`.

Orden topológico aproximado que Django aplicará:

```text
contenttypes.0001
auth.0001            (User se omite por swappable)
cuentas.0001         (depende de auth)
auth.0002 … auth.0012
contenttypes.0002
admin.0001 … admin.0003
sessions.0001
```

El orden exacto lo decide el grafo de Django; lo relevante es que `cuentas.0001` exista antes de que se resuelva la dependencia de `admin.0001`.

---

## 7. Riesgos detectados

| ID | Riesgo | Estado |
|---|---|---|
| R01 | El grafo actual es inválido: `showmigrations --plan` falla por `cuentas` sin migraciones | **Sin resolver**; se resuelve generando `cuentas.0001` |
| R02 | La sonda del autodetector propuso cambios accesorios en `auth`/`contenttypes` | Revisar el archivo generado; no aplicar cambios no deseados |
| R03 | La dependencia exacta de `cuentas.0001` debe confirmarse en el archivo generado | Pendiente de revisión |
| R04 | Los `CheckConstraint` no están verificados en base | Requiere base migrada |
| R05 | `email` no es único y `rol` solo se valida por `choices` + constraints | Decisión aprobada; sin cambio |
| R06 | El gestor se serializa en la migración | Esperado y compatible |
| R07 | No hay datos en la base; no hay riesgo de pérdida al decidir ahora | Ventana segura |

No se detectaron defectos de código que obliguen a corregir modelos o configuración antes de generar la migración.

---

## 8. Comandos que se ejecutarían en una futura etapa (NO ejecutados)

```powershell
python manage.py check
python manage.py makemigrations cuentas
python manage.py sqlmigrate cuentas 0001
python manage.py showmigrations --plan
python manage.py migrate --plan
python manage.py migrate
```

Ninguno de estos comandos de generación o aplicación fue ejecutado en esta auditoría, salvo `check` y `showmigrations --plan`, que son de solo lectura.

---

## 9. Verificaciones realizadas y resultados

| Verificación | Resultado |
|---|---|
| `python manage.py check` | 0 incidencias |
| `python manage.py test apps.cuentas -v 1` | **52/52 OK** en 0.024 s |
| `python manage.py showmigrations --plan` | Falló: `ValueError: Dependency on app with no migrations: cuentas` |
| Migraciones propias | 0 archivos |
| Migraciones Django instaladas | 18 (`admin` 3, `auth` 12, `contenttypes` 2, `sessions` 1) |
| `AUTH_USER_MODEL` | `cuentas.Usuario`, resuelto a `apps.cuentas.models.Usuario` |
| `auth.User._meta.swapped` | `cuentas.Usuario` |
| `admin.LogEntry.user` | FK a `cuentas.Usuario`, `CASCADE` |
| Modelos en apps propias | Solo `cuentas.Usuario`; los otros cuatro paquetes están vacíos |
| Referencias al usuario en apps propias | Ninguna fuera de `settings.py` |
| Tablas en `public` | Ninguna |
| Bases `test_*` | Ninguna |
| `django_migrations` | No existe |
| Sonda `MigrationAutodetector` | Confirmó `CreateModel Usuario`, campos, M2M y dos `CheckConstraint` |

Todas las consultas a PostgreSQL fueron `SELECT` de solo lectura. No se ejecutó `GRANT` ni `REVOKE`.

---

## 10. Recomendación final

**No se declara que la preparación esté lista para migrar.** Existe una dependencia sin resolver en el grafo: `admin.0001` requiere `cuentas.__first__` y `cuentas` todavía no tiene migraciones. Mientras esa dependencia no se resuelva, `showmigrations --plan` y `migrate` no pueden completarse.

**No se requieren correcciones de código ni de configuración.** `AUTH_USER_MODEL`, el modelo `Usuario`, los `CheckConstraint`, el gestor y las dependencias son coherentes con Django 6.1.3.

La preparación es segura para avanzar **solo si el usuario autoriza expresamente**:

1. Generar `cuentas.0001_initial`.
2. Revisar el archivo generado, prestando atención a las dependencias y a posibles cambios accesorios en `auth`/`contenttypes`.
3. Solo después, previsualizar y aplicar migraciones.

Esta auditoría **no autoriza** generar ni aplicar migraciones. La Fase 0 continúa abierta.

---

Fin del informe.
