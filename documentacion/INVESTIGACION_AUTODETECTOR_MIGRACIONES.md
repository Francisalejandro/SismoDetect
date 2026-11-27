# Investigación del autodetector de migraciones — SismoDetect

**Proyecto:** SismoDetect — Sistema web para la consulta, análisis y clasificación de señales sísmicas en Cuba mediante inteligencia artificial

> La explicabilidad se mantiene como funcionalidad complementaria del sistema.

| Campo | Valor |
|---|---|
| Fecha | 2026-11-27 |
| Fase | Fase 0 — Base técnica (continúa abierta) |
| Alcance | Solo lectura, comparaciones en memoria y diagnóstico |
| Estado | Investigación completada; **no se generaron migraciones** |
| Nota | Documento restaurado el 2026-11-27 tras detectarse su ausencia en `documentacion/`; refleja la investigación previa a la generación de `cuentas.0001` |
| Aclaración posterior | Las simulaciones de este documento son anteriores a la generación y aplicación de `cuentas.0001`; con la configuración real actual, `makemigrations --check --dry-run` devuelve `No changes detected` |

> **Alcance de sus conclusiones (aclaración de 2026-11-27):** las alternativas y previsiones de este documento proceden de simulaciones en memoria realizadas **antes** de generar `cuentas.0001_initial`, con `LANGUAGE_CODE="es"` y sin migraciones aplicadas. Con la configuración real del proyecto y ya aplicada la migración, `python manage.py makemigrations --check --dry-run` devuelve `No changes detected`. Por tanto, la aparición de migraciones cosméticas adicionales no está confirmada en el estado actual; cualquier propuesta futura debe revisarse antes de generarla o aplicarla.

---

## 1. Causa exacta de las migraciones adicionales

La causa es la **traducción de los nombres legibles** (`verbose_name`, `verbose_name_plural`, `help_text` y mensajes de error) de los modelos incluidos en Django.

`config/settings.py` fija:

```python
LANGUAGE_CODE = "es"
```

Los modelos de `django.contrib.auth` y `django.contrib.contenttypes` definen esos textos con `gettext_lazy`. Al construir el estado actual de la aplicación (`ProjectState.from_apps(apps)`) con idioma español activo, Django obtiene cadenas en español. Las migraciones incluidas en Django, en cambio, guardan las cadenas originales en inglés.

`MigrationAutodetector` compara ambos estados y detecta diferencias en esos atributos, aunque **no haya cambiado la estructura de la base de datos**. Por eso propone `AlterModelOptions` y `AlterField`.

No se trata de una diferencia estructural: con un proceso nuevo inicializado con `LANGUAGE_CODE = "en"`, todas las diferencias de campos y opciones de `contenttypes`, `Group`, `Permission` y `User` desaparecen. La única diferencia restante es `abstract: False` en el estado actual de `auth.User`, que el autodetector **no** convierte en ninguna operación.

---

## 2. Diferencias concretas detectadas

### 2.1 Estado con español (configuración actual)

Comparación entre el estado histórico de las migraciones y el estado actual de los modelos:

#### `contenttypes.0003_alter_contenttype_options_alter_contenttype_model`

| Elemento | Histórico | Actual con `es` |
|---|---|---|
| `ContentType._meta.verbose_name` | `content type` | `tipo de contenido` |
| `ContentType._meta.verbose_name_plural` | `content types` | `tipos de contenido` |
| Campo `model`, `verbose_name` | `python model class name` | `nombre de la clase modelo de python` |

Operaciones propuestas:

```text
AlterModelOptions contenttype -> verbose_name='tipo de contenido',
                                 verbose_name_plural='tipos de contenido'
AlterField contenttype.model -> CharField (solo cambia verbose_name)
```

#### `auth.0013_alter_group_options_alter_permission_options_and_more`

| Modelo / campo | Histórico | Actual con `es` |
|---|---|---|
| `Group.verbose_name` / plural | `group` / `groups` | `grupo` / `grupos` |
| `Group.name.verbose_name` | `name` | `nombre` |
| `Group.permissions.verbose_name` | `permissions` | `permisos` |
| `Permission.verbose_name` / plural | `permission` / `permissions` | `permiso` / `permisos` |
| `Permission.codename.verbose_name` | `codename` | `nombre en código` |
| `Permission.content_type.verbose_name` | `content type` | `tipo de contenido` |
| `Permission.name.verbose_name` | `name` | `nombre` |
| `User.verbose_name` / plural | `user` / `users` | `usuario` / `usuarios` |
| `User.username.verbose_name` | `username` | `nombre de usuario` |
| `User.username.help_text` | inglés | español |
| `User.username.error_messages['unique']` | inglés | español |
| `User.password.verbose_name` | `password` | `contraseña` |
| `User.last_login.verbose_name` | `last login` | `último inicio de sesión` |
| `User.first_name.verbose_name` | `first name` | `nombre` |
| `User.last_name.verbose_name` | `last name` | `apellidos` |
| `User.email.verbose_name` | `email address` | `dirección de correo electrónico` |
| `User.is_staff.verbose_name` / `help_text` | inglés | español |
| `User.is_superuser.verbose_name` / `help_text` | inglés | español |
| `User.is_active.verbose_name` / `help_text` | inglés | español |
| `User.date_joined.verbose_name` | `date joined` | `fecha de alta` |
| `User.groups.verbose_name` / `help_text` | inglés | español |
| `User.user_permissions.verbose_name` / `help_text` | inglés | español |

Operaciones propuestas:

```text
AlterModelOptions group
AlterModelOptions permission
AlterModelOptions user
AlterField group.name
AlterField group.permissions
AlterField permission.codename
AlterField permission.content_type
AlterField permission.name
AlterField user.date_joined
AlterField user.email
AlterField user.first_name
AlterField user.groups
AlterField user.is_active
AlterField user.is_staff
AlterField user.is_superuser
AlterField user.last_login
AlterField user.last_name
AlterField user.password
AlterField user.user_permissions
AlterField user.username
```

### 2.2 Demostración de que no son diferencias estructurales

Se repitió la comparación en un **proceso nuevo** con un módulo de ajustes temporal que importa `config.settings` y solo cambia:

```python
LANGUAGE_CODE = "en"
```

Resultado:

| Modelo | Opciones históricas vs. actuales con `en` | Diferencias de campos |
|---|---|---|
| `contenttypes.ContentType` | Iguales | Ninguna |
| `auth.Group` | Iguales | Ninguna |
| `auth.Permission` | Iguales | Ninguna |
| `auth.User` | Solo aparece `abstract: False` en el estado actual | Ninguna |

El autodetector no genera ninguna operación por `abstract: False` en un modelo existente. Por tanto, **todas las operaciones propuestas en `auth.0013` y `contenttypes.0003` son consecuencia del idioma**, no de cambios reales de esquema.

Nota: intentar `translation.override("en")` después de que Django ya cargó los modelos no es fiable, porque los nombres pueden haberse resuelto durante la construcción del registro de aplicaciones. La comparación concluyente se hizo con un proceso nuevo e idioma inglés desde el inicio.

---

## 3. Evaluación de alternativas

### Alternativa A — Generación temporal con idioma inglés, sin modificar `settings.py`

Consiste en crear un módulo de ajustes **fuera del proyecto** que importe la configuración real y cambie solo `LANGUAGE_CODE`:

```python
# archivo temporal fuera del proyecto
from config.settings import *

LANGUAGE_CODE = "en"
```

y ejecutar, con autorización, la generación apuntando a ese módulo:

```powershell
$env:PYTHONPATH = 'C:\Users\Francis\AppData\Local\Temp\opencode'
python manage.py makemigrations cuentas --settings=settings_en
```

Simulación en memoria con ese mismo módulo:

```text
APPS: ['cuentas']
MIGRACION: cuentas 0001_initial | deps: [('auth', '0012_alter_user_first_name_max_length')]
   OP: CreateModel Usuario
```

| Aspecto | Resultado |
|---|---|
| Archivos que produciría | Solo `apps/cuentas/migrations/0001_initial.py` |
| Dependencia | `('auth', '0012_alter_user_first_name_max_length')` |
| Dos `CheckConstraint` | Sí, se conservan: el modelo no se modifica |
| Gestor `UsuarioManager` | Sí, se serializa porque `use_in_migrations=True` |
| Grafo resultante | Válido: `admin.0001` resuelve `cuentas.__first__` a `cuentas.0001` |
| Riesgos | El módulo temporal debe crearse fuera del proyecto y eliminarse después; no debe quedar en el repositorio. Durante la generación el idioma activo es inglés, pero no se escriben datos ni cambios de idioma en la base |

**Valoración:** alternativa preferida si se autoriza generar exclusivamente `cuentas.0001_initial`.

### Alternativa B — `makemigrations cuentas` con la configuración actual (`es`)

Simulación ya realizada:

```text
APPS: ['auth', 'contenttypes', 'cuentas']

contenttypes.0003_alter_contenttype_options_alter_contenttype_model
  deps: [('contenttypes', '0002_remove_content_type_name')]

auth.0013_alter_group_options_alter_permission_options_and_more
  deps: [('contenttypes', '0003...'), ('auth', '0012_alter_user_first_name_max_length')]

cuentas.0001_initial
  deps: [('auth', '0013_alter_group_options_alter_permission_options_and_more')]
```

| Aspecto | Resultado |
|---|---|
| Archivos que produciría | Tres: `contenttypes.0003`, `auth.0013`, `cuentas.0001` |
| Dependencia | `auth.0013` |
| Restricciones y gestor | Se conservan, pero el alcance se amplía |
| Grafo resultante | Sería válido solo si se generan los tres archivos |
| Riesgos | Incluye migraciones de apps de Django que no aportan cambios de esquema; si se generara solo `cuentas.0001` con esta dependencia, el grafo quedaría roto porque `auth.0013` no existiría |

**Valoración:** no cumple la condición de generar exclusivamente `cuentas.0001_initial`.

La documentación oficial de Django indica que limitar las migraciones a una app es una promesa de «mejor esfuerzo», no una garantía: Django generará también las migraciones de otras apps que necesite para mantener las dependencias correctas. Esto explica por qué `cuentas` arrastra a `auth`, aunque en este caso el motivo inmediato sea la diferencia de idioma.

### Alternativa C — Otras opciones

| Opción | Evaluación |
|---|---|
| `makemigrations --dry-run` | Solo previsualiza; no genera el archivo. Útil como verificación adicional, no como solución |
| `--noinput`, `--name` | No cambian el idioma ni las dependencias |
| Cambiar `LANGUAGE_CODE` a `en` en `config/settings.py` | Modificaría el comportamiento permanentemente; no autorizado |
| `USE_I18N = False` | También es un cambio permanente de configuración; no autorizado |
| `MIGRATION_MODULES` para desactivar `auth`/`contenttypes` | No recomendable: `cuentas` tiene M2M hacia modelos de `auth`; Django desaconseja relaciones con apps sin migraciones |
| Crear `cuentas.0001` manualmente | Se aparta del comando autorizado y puede divergir de lo que Django generaría; requiere autorización explícita |
| `migrate --run-syncdb` | No crea restricciones ni el historial de migraciones; además está prohibido |

No existe una opción oficial de `makemigrations` que, con `LANGUAGE_CODE="es"`, garantice que solo se escriba `cuentas.0001` sin arrastrar los cambios de traducción de Django.

---

## 4. Dependencia correcta para `cuentas.0001`

La dependencia correcta es:

```python
dependencies = [
    ("auth", "0012_alter_user_first_name_max_length"),
]
```

Justificación:

1. `Usuario.groups` es una relación M2M hacia `auth.Group`.
2. `Usuario.user_permissions` es una relación M2M hacia `auth.Permission`.
3. Esos modelos se crean en `auth.0001_initial`, pero Django no genera una dependencia directa contra esa migración: cuando la app relacionada ya tiene migraciones y no se generan nuevas para ella, `MigrationAutodetector` resuelve la dependencia contra la **hoja** del grafo de esa app.
4. La hoja actual de `auth` es `auth.0012_alter_user_first_name_max_length`.
5. Esa migración incluye transitivamente `auth.0001`, por lo que garantiza que `auth_group` y `auth_permission` existen antes de crear las tablas intermedias de `cuentas`.

No elegir `auth.0013`: no existe en el entorno y solo aparece porque `makemigrations` propuso crearlo. No elegir `auth.0001` manualmente: aunque crearía las tablas necesarias, no es la dependencia que Django genera de forma estándar y no incluiría el resto del historial de `auth`.

---

## 5. Estrategia recomendada

Con autorización expresa, el procedimiento más seguro es:

1. Crear un módulo de ajustes temporal **fuera del proyecto** que importe `config.settings` y fije `LANGUAGE_CODE = "en"`.
2. Ejecutar la generación apuntando a ese módulo, limitada a `cuentas`:

   ```powershell
   $env:PYTHONPATH = 'C:\Users\Francis\AppData\Local\Temp\opencode'
   python manage.py makemigrations cuentas --settings=settings_en
   ```

3. Verificar que se creó **solo** `apps/cuentas/migrations/0001_initial.py`.
4. Revisar el archivo generado:
   - dependencia `('auth', '0012_alter_user_first_name_max_length')`;
   - `CreateModel Usuario`;
   - dos `CheckConstraint`;
   - `managers=[("objects", UsuarioManager())]`;
   - ninguna operación sobre `auth.User`.
5. Eliminar el módulo de ajustes temporal.
6. Ejecutar solo verificaciones de lectura: `check`, `test`, `sqlmigrate`, `showmigrations --plan`, `migrate --plan`.
7. **No ejecutar `migrate`** sin una autorización posterior.

Esta estrategia no modifica `config/settings.py`, no cambia el idioma de la aplicación en funcionamiento y mantiene el grafo válido.

---

## 6. Riesgos y limitaciones

| Riesgo / limitación | Detalle |
|---|---|
| No se ejecutó `makemigrations` | Todas las conclusiones sobre salida de archivos proceden de simulaciones en memoria con el mismo autodetector y questioner del comando |
| Dependencia confirmada por simulación | `auth.0012` se confirmó con el módulo temporal; debe validarse de nuevo en el archivo real si se autoriza la generación |
| Idioma durante la generación | Con `es` aparecen cambios cosméticos en modelos de Django; con `en` desaparecen |
| Cambios de opciones no estructurales | No alteran tablas, pero sí ensucian el historial de migraciones si se generan |
| Módulo temporal | Debe estar fuera del proyecto y eliminarse después; no se agrega al repositorio |
| Base de datos | Sigue vacía; los `CheckConstraint` no están verificados en base |
| Fase | La Fase 0 continúa abierta; esta investigación no autoriza generar ni aplicar migraciones |

---

## 7. Verificaciones ejecutadas

| Verificación | Resultado |
|---|---|
| Comparación estado histórico vs. actual, idioma `es` | Diferencias solo en textos traducidos y opciones legibles |
| Comparación estado histórico vs. actual, idioma `en` | Sin diferencias de campos; solo `abstract: False` en `auth.User`, sin operación generada |
| Autodetector con `es` | Propone `contenttypes.0003`, `auth.0013`, `cuentas.0001`; dependencia `auth.0013` |
| Autodetector con módulo temporal `en` | Propone solo `cuentas.0001`; dependencia `auth.0012` |
| Revisión de la documentación oficial de Django | Confirma que limitar `makemigrations` a una app es «mejor esfuerzo» y puede arrastrar dependencias |
| Comprobación de archivos de migración | Sigue habiendo 0 migraciones propias |
| Consultas a PostgreSQL | Solo lectura; sin tablas de aplicación |

No se ejecutaron `makemigrations`, `migrate`, `GRANT`, `REVOKE` ni comandos de escritura.

---

## 8. Confirmación final

**No se generaron archivos de migración. No se modificó PostgreSQL. No se modificaron modelos, configuración, `.env`, usuarios ni permisos. No se realizaron commits ni push.**

La opción recomendada es la **alternativa A**, pero requiere autorización expresa antes de ejecutarse. Hasta entonces, la Fase 0 continúa abierta y no se autoriza generar ni aplicar migraciones.

---

Fin del informe.
