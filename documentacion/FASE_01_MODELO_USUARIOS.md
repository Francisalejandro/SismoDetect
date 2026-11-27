# FASE 1 — Modelo de usuarios y superusuario temporal

**Proyecto:** SismoDetect — Sistema web para la consulta, análisis y clasificación de señales sísmicas en Cuba mediante inteligencia artificial

> La explicabilidad se mantiene como funcionalidad complementaria del sistema.

| Campo | Valor |
|---|---|
| Fecha | 2026-11-26 (actualizado 2026-11-27) |
| Fase | Fase 1 — Corrección del modelo de usuarios |
| Estado | **IMPLEMENTADO Y VERIFICADO**; migraciones aplicadas en PostgreSQL |
| Código modificado | `apps/cuentas/models.py`, `apps/cuentas/admin.py`, `apps/cuentas/tests.py`, `apps/__init__.py` |
| Pruebas | **52/52 correctas** (`SimpleTestCase`, sin base de datos) |
| Migraciones | `cuentas.0001_initial` **generada y aplicada** (19/19 migraciones) |
| Base de datos | `sismodetect`, con 10 tablas; sin `auth_user` |
| Relación con Fase 0 | Continúa `documentacion/INFORME_IMPLEMENTACION.md` |

> **Estado real:** la corrección del código fue autorizada y aplicada. El 2026-11-27 se generó **solo** `apps/cuentas/migrations/0001_initial.py` y después se ejecutó `migrate` con autorización expresa: 19/19 migraciones aplicadas a las 01:40:51 (-05:00), sin errores. No se creó ningún usuario ni grupo. Las pruebas se ejecutaron con `SimpleTestCase`, que no crea ni usa base de datos.
>
> **Nota de fase:** el refuerzo del panel de administración descrito en la sección 2.6 se ejecutó como **continuación de la Fase 0**, no como inicio formal de la Fase 1. Ninguna fase se declara terminada.

---

## 1. Decisiones registradas

| ID | Decisión | Estado |
|---|---|---|
| D01 | Crear un superusuario **temporal** solo para la configuración inicial | **Aprobada** |
| D02 | El superusuario temporal se elimina tras verificar el Administrador definitivo | **Aprobada** |
| D03 | El Administrador definitivo debe tener `rol="administrador"`, `is_staff=True` y acceso a `/admin/` | **Aprobada** |
| D04 | Un superusuario de Django debe tener siempre `rol="administrador"` | **Aprobada e implementada** |
| D05 | `es_administrador` debe reconocer tanto el rol como `is_superuser` | **Aprobada e implementada** |
| D06 | `rol` se valida también en la base con `CheckConstraint` | **Aprobada e implementada** |
| D07 | `is_staff` se mantiene como permiso de acceso al panel, independiente del rol funcional | **Aprobada** |
| D08 | `email` sigue sin ser único en V1 | **Aprobada** |
| D09 | La cuenta definitiva será `is_superuser=False` y recibirá permisos por grupo | **Aprobada** |

### 1.1 Justificación de D01–D03

Django necesita una cuenta con acceso total para ejecutar la primera configuración: crear la cuenta real, el grupo de administradores y asignar permisos. Esa cuenta no debe quedar en el sistema. El Administrador definitivo no necesita ser superusuario si recibe los permisos necesarios.

### 1.2 Justificación de D04–D06

La revisión técnica de `documentacion/REVISION_MODELO_USUARIO.txt` demostró que:

```text
Usuario(username="prueba", is_superuser=True).rol → "usuario"
Usuario(...).es_administrador → False
```

`createsuperuser` no asigna `rol`. Sin corrección, el superusuario temporal no sería reconocido como Administrador por la aplicación. La corrección se aplica en tres capas:

1. `UsuarioManager.create_superuser()` asigna el rol.
2. `save()` fuerza la coherencia.
3. `CheckConstraint` impide violarla por SQL directo.

---

## 2. Cambios implementados

### 2.1 `apps/cuentas/models.py`

```python
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q


class UsuarioManager(UserManager):
    """Manager que mantiene coherente el rol de los superusuarios."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("rol", self.model.Rol.ADMINISTRADOR)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    """Usuario local de SismoDetect.

    Se extiende ``AbstractUser`` para conservar la autenticación estándar de
    Django y añadir el rol funcional que utilizará la interfaz.
    """

    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        USUARIO = "usuario", "Usuario"

    rol = models.CharField(
        "rol",
        max_length=20,
        choices=Rol.choices,
        default=Rol.USUARIO,
        help_text="Rol funcional dentro de SismoDetect.",
    )

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = (
            models.CheckConstraint(
                condition=Q(rol__in=["administrador", "usuario"]),
                name="cuentas_usuario_rol_valido",
            ),
            models.CheckConstraint(
                condition=Q(is_superuser=False) | Q(rol="administrador"),
                name="cuentas_usuario_superusuario_administrador",
            ),
        )

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = self.Rol.ADMINISTRADOR
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"rol"}
        super().save(*args, **kwargs)

    @property
    def es_administrador(self) -> bool:
        return self.is_superuser or self.rol == self.Rol.ADMINISTRADOR
```

### 2.2 `apps/__init__.py`

**Aplicado.** El docstring ya describe `catalogo`, `adquisicion`, `analisis`, `cuentas` e `interfaz`, y no menciona `apps.catalogacion` ni `apps.api`.

### 2.3 `apps/cuentas/admin.py` (necesario para la decisión 7)

**Aplicado.** Un administrador que no sea superusuario no puede crear superusuarios ni elevar privilegios:

| Medida | Implementación |
|---|---|
| Campos reservados fuera de sus formularios | `rol`, `is_staff`, `is_superuser`, `groups`, `user_permissions` |
| No ve superusuarios en el listado | `get_queryset()` filtra `is_superuser=False` |
| No puede editar un superusuario | `has_change_permission()` devuelve `False` |
| No puede borrar un superusuario | `has_delete_permission()` devuelve `False` |
| Alta de usuarios | Solo `username`, `password1`, `password2`; el rol queda en `usuario` por defecto |

Consecuencia: un administrador normal gestiona usuarios normales (datos, estado y contraseña), pero **no puede crear otros administradores, conceder permisos ni dar acceso al panel**. Para crear otro administrador haría falta un superusuario temporal por consola, igual que en el arranque.

Los nombres de permiso del modelo son los del modelo `Usuario`:

```text
cuentas.add_usuario
cuentas.change_usuario
cuentas.view_usuario
cuentas.delete_usuario
```

### 2.4 Pruebas añadidas

**Aplicado.** `apps/cuentas/tests.py` contiene **52 pruebas** `SimpleTestCase`:

| Grupo | Pruebas |
|---|---|
| Modelo | rol por defecto, choices, `es_administrador` por rol y por `is_superuser`, manager, restricciones, `__str__` |
| `save()` | fuerza el rol del superusuario, respeta el rol normal, añade `rol` a `update_fields` |
| Manager | `create_superuser()` asigna `rol="administrador"` |
| Admin inicial | campos reservados ocultos, rol oculto al crear, cambio/borrado de superusuarios denegado |
| Admin reforzado | consulta filtrada, ver/editar/borrar, contraseñas, listas blancas de formulario, fechas de solo lectura, `save_model`, `save_related`, acciones y acceso al panel |

No usan base de datos: `SimpleTestCase` declara `databases = set()` y Django informa «Skipping setup of unused database(s): default».

### 2.5 Sin cambios

- `AUTH_USER_MODEL = "cuentas.Usuario"` se mantiene.
- `INSTALLED_APPS` se mantiene.
- `db.sqlite3` no se toca.
- `ia/pesos/cnn_v1/` no se toca.
- `email` sigue sin ser único (D08 aprobada).

### 2.6 Refuerzo del panel de administración (continuación de Fase 0)

**Aplicado.** Según la política aprobada, `apps/cuentas/admin.py` incorpora:

- Listas blancas de campos para alta y edición de administradores normales.
- `get_queryset()` que excluye otros administradores y superusuarios, manteniendo visible la propia cuenta.
- `has_view_permission()` y `has_change_permission()` que deniegan otros administradores.
- `has_delete_permission()` siempre `False` para no superusuarios y eliminación de `delete_selected`.
- `user_change_password()` protegido: permite la propia contraseña y la de usuarios normales, pero no la de otro administrador.
- `last_login` y `date_joined` de solo lectura para no superusuarios.
- `save_model()` y `save_related()` que imponen la política en el servidor: los usuarios nuevos creados por un administrador normal quedan como `rol="usuario"`, `is_staff=False`, `is_superuser=False`, sin grupos ni permisos.
- Protección contra auto-desactivación: `is_active` es de solo lectura en la propia cuenta y `save_model()` lanza `PermissionDenied` si un administrador normal intenta guardarla con `is_active=False`, incluso con un POST manipulado.
- El superusuario temporal conserva todas sus capacidades.

El detalle completo está en `documentacion/REVISION_ADMIN_CUENTAS.md` (secciones 2–4) y en `documentacion/INFORME_IMPLEMENTACION.md` (sección 12).

---

## 3. Impacto en las migraciones

| Elemento | ¿Genera operación de migración? |
|---|---|
| `UsuarioManager` | **Sí**: se serializa porque `use_in_migrations=True`, heredado de `django.contrib.auth.models.UserManager` |
| `save()` | **No** |
| `es_administrador` | **No** |
| `CheckConstraint` de rol | **Sí**, dentro de `0001_initial` |
| `CheckConstraint` superusuario/rol | **Sí**, dentro de `0001_initial` |

La migración inicial generada es una sola y contiene una única operación:

```text
cuentas.0001_initial
    CreateModel(Usuario)   # incluye los 14 campos, las M2M y los dos CheckConstraint
```

> **Corrección (2026-11-27):** la versión anterior de esta sección afirmaba que el gestor no generaría operación porque `use_in_migrations=False` por defecto. Es incorrecto: `UserManager` define `use_in_migrations = True` y `UsuarioManager` lo hereda. El archivo generado incluye `managers=[("objects", UsuarioManager())]`.

Las M2M `groups` y `user_permissions` y los dos `CheckConstraint` no aparecen como operaciones separadas: Django los integra dentro del `CreateModel`. El detalle real está en `documentacion/REVISION_MIGRACION_CUENTAS.md`.

Dependencias reales:

```text
cuentas.0001 → auth.0012_alter_user_first_name_max_length
admin.0001   → cuentas.0001 + contenttypes.0001
auth.0001    → contenttypes.0001  (auth.User se omite por estar sustituido)
```

No hay dependencia circular.

### 3.1 Advertencia sobre el orden

`apps/cuentas/migrations/` ya contiene `0001_initial.py` (generado el 2026-11-27). Antes de generarlo, `migrate` habría fallado al resolver la FK de `admin.LogEntry`:

```text
ValueError: The field admin.LogEntry.user was declared with a lazy reference
to 'cuentas.usuario', but app 'cuentas' isn't installed.
```

Con la migración presente, `showmigrations --plan` y `migrate --plan` funcionan correctamente. El orden aplicado fue: `makemigrations` → revisar → `migrate`. `migrate` **ya se ejecutó con autorización expresa el 2026-11-27** (19/19 OK); no queda pendiente de autorización.

---

## 4. Protocolo del superusuario temporal

> **Requisito:** este protocolo se ejecuta **después** de aplicar las migraciones. Las migraciones ya están aplicadas (19/19 el 2026-11-27); la creación de usuarios y grupos descrita aquí **no forma parte de los pasos autorizados todavía**.

### 4.1 Crear el superusuario temporal

```powershell
cd 'D:\Escuela\Inteligencia Artificial\SismoDetect'
.\.venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

Datos sugeridos:

| Campo | Valor |
|---|---|
| Username | `bootstrap_temp` |
| Email | correo del responsable técnico |
| Password | clave aleatoria forte, guardada solo en un gestor de contraseñas |

Con la corrección aplicada, `create_superuser()` asignará automáticamente:

```text
rol = "administrador"
is_staff = True
is_superuser = True
es_administrador = True
```

Verificación en `manage.py shell`:

```python
from django.contrib.auth import get_user_model

U = get_user_model()
u = U.objects.get(username="bootstrap_temp")
print(u.rol, u.is_staff, u.is_superuser, u.es_administrador)
```

Resultado esperado:

```text
administrador True True True
```

### 4.2 Crear el grupo de administradores

Con la sesión del superusuario temporal en `/admin/`:

1. Ir a **Autenticación y autorización → Grupos → Añadir**.
2. Nombre: `Administradores`.
3. Permisos mínimos:
   - `cuentas | usuario | Can add usuario`
   - `cuentas | usuario | Can change usuario`
   - `cuentas | usuario | Can view usuario`
4. Guardar.

> **Nota:** no se concede `delete usuario`; para retirar una cuenta se recomienda desmarcar `is_active`. Los codenames reales son `add_usuario`, `change_usuario` y `view_usuario`, no `*_user`.

> **Advertencia:** el permiso `change_usuario` permite modificar cuentas y restablecer contraseñas. Aunque el admin oculta los campos reservados, la pertenencia al grupo `Administradores` debe limitarse al personal de confianza.

### 4.3 Crear el Administrador definitivo

En `/admin/` con el superusuario temporal:

| Campo | Valor |
|---|---|
| Username | el definitivo (por ejemplo, `admin_francis`) |
| Email | correo institucional |
| Password | clave fuerte del responsable |
| `rol` | `Administrador` |
| `is_active` | marcado |
| `is_staff` | **marcado** (necesario para `/admin/`) |
| `is_superuser` | **desmarcado** (recomendado, D09) |
| Grupos | `Administradores` |

> **Aclaración operativa:** el formulario de alta solo contiene `username`, contraseña y `rol`; `is_staff`, `is_superuser` y `groups` **no están en el alta** (ni siquiera para el superusuario). Tras guardar, Django abre el formulario de edición del usuario: allí se marca `is_staff`, se añade al grupo `Administradores` y se confirma que `is_superuser` queda desmarcado. `is_active` ya viene marcado por defecto.

### 4.4 Verificar el Administrador definitivo

1. Cerrar sesión del superusuario temporal.
2. Iniciar sesión con la cuenta definitiva.
3. Comprobar:
   - `/admin/` carga sin error 403.
   - Aparece la sección **Cuentas → Usuarios**.
   - La lista de usuarios es visible.
   - El detalle del propio usuario muestra `rol = Administrador`, `is_staff = True`, `is_superuser = False`.
   - Puede abrir el formulario de edición de un usuario.

Comprobación adicional en `manage.py shell`:

```python
from django.contrib.auth import get_user_model

U = get_user_model()
u = U.objects.get(username="admin_francis")
print(u.rol, u.is_staff, u.is_superuser, u.es_administrador)
print(u.has_perm("cuentas.change_usuario"), u.has_perm("cuentas.add_usuario"))
```

Resultado esperado:

```text
administrador True False True
True True
```

### 4.5 Eliminar el superusuario temporal

Solo después de que todas las comprobaciones anteriores pasen.

**Antes de borrar**, conservar evidencia de las acciones del temporal:

```python
from django.contrib.admin.models import LogEntry

for e in LogEntry.objects.filter(user__username="bootstrap_temp"):
    print(e.action_time, e.get_action_flag_display(), e.object_repr)
```

Anotar el resultado en este informe. Después:

```python
from django.contrib.auth import get_user_model

U = get_user_model()
print(U.objects.filter(username="bootstrap_temp").delete())
```

Resultado esperado: `(N, {...})` con `N >= 1`.

Verificar:

```python
print(U.objects.filter(username="bootstrap_temp").exists())
print(U.objects.filter(rol="administrador", is_active=True).count())
```

Resultado esperado: `False` y un conteo `>= 1`.

### 4.6 Comprobación final

1. Cerrar sesión y volver a entrar con la cuenta definitiva.
2. Confirmar que `/admin/` sigue funcionando.
3. Confirmar que la cuenta temporal ya no existe.
4. Confirmar que no queda ninguna otra cuenta con `is_superuser=True` no prevista.

### 4.7 Nota sobre el historial

`admin.LogEntry.user` usa `on_delete=CASCADE`. Al eliminar `bootstrap_temp`, **se eliminan también sus entradas del historial del admin**. Por eso la exportación del paso 4.5 debe hacerse antes del borrado y registrarse en este informe.

---

## 5. Verificación ejecutada (antes y después de aplicar migraciones)

**Fechas:** 2026-11-26 (código), 2026-11-27 (migración generada) y 2026-11-27 01:40:51 (-05:00) (`migrate` aplicado).

| Comprobación | Comando / método | Resultado real |
|---|---|---|
| Sintaxis y checks | `python manage.py check` | 0 incidencias |
| Checks de modelos | `python manage.py check --tag models` | 0 incidencias |
| Checks de admin | `python manage.py check --tag admin` | 0 incidencias |
| Checks de base | `python manage.py check --database default` | 0 incidencias |
| Pruebas del modelo y roles | `python manage.py test apps.cuentas -v 1` | **52/52 OK** (0.034 s tras migrar; inicialmente 19/19) |
| Base de datos en las pruebas | salida del comando anterior | `Skipping setup of unused database(s): default` |
| Modelo resuelto | introspección | `apps.cuentas.models.Usuario` |
| Tabla | `_meta.db_table` | `cuentas_usuario` |
| Manager | `type(Usuario.objects)` | `UsuarioManager` (`use_in_migrations=True`) |
| Restricciones | `_meta.constraints` | `cuentas_usuario_rol_valido`, `cuentas_usuario_superusuario_administrador` |
| Superusuario en memoria | instancia con `is_superuser=True` | `es_administrador = True` |
| Usuario normal en memoria | instancia con `rol="usuario"` | `es_administrador = False` |
| Migraciones propias | `apps/**/0*.py` | **1 archivo**: `cuentas/0001_initial.py` |
| Dependencia de la migración | `MigrationLoader` | `('auth', '0012_alter_user_first_name_max_length')` |
| `CheckConstraint` en la migración | inspección del archivo | Los dos, con nombres exactos |
| SQL de la migración | `manage.py sqlmigrate cuentas 0001` | `cuentas_usuario` + 2 tablas M2M; sin `auth_user` |
| Grafo de migraciones | `manage.py showmigrations --plan` | 19 pendientes antes de aplicar; válido |
| Plan de aplicación | `manage.py migrate --plan` | 19 migraciones, orden correcto |
| Aplicación | `python manage.py migrate` | **19/19 OK**, salida 0, 1.39 s |
| Tablas en `public` | consulta a `information_schema` | **10** (antes: 0) |
| `django_migrations` | consulta directa | 19 filas |
| `auth_user` | `to_regclass` | **`NULL`** (no existe) |
| `auth_group` / `cuentas_usuario` | conteo | 0 / 0 (no se crearon cuentas ni grupos) |
| Bases de prueba creadas | `pg_database` con prefijo `test_` | **ninguna** |

### 5.1 Comprobaciones pendientes (requieren autorización)

| Comprobación | Estado |
|---|---|
| Generar `cuentas.0001_initial` | **Cumplido** (2026-11-27) |
| Verificar los dos `CheckConstraint` dentro de la migración | **Cumplido** (2026-11-27) |
| Previsualizar SQL y plan | **Cumplido** |
| Aplicar migraciones | **Cumplido** (2026-11-27 01:40:51; 19/19 OK) |
| Crear usuarios | Pendiente (no autorizado todavía) |
| Verificar rechazo en base de un superusuario con rol `usuario` | Pendiente: las restricciones ya existen, pero no se probó con un `INSERT` porque no estaba autorizado |
| Crear el grupo `Administradores` | Pendiente (no autorizado todavía) |

Generación ejecutada (solo `cuentas`):

```powershell
$env:PYTHONPATH = 'C:\Users\Francis\AppData\Local\Temp\opencode'
python manage.py makemigrations cuentas --settings=settings_en
```

Se usó un módulo temporal **fuera del proyecto** con `LANGUAGE_CODE = "en"` para evitar que el autodetector propusiera migraciones accesorias de `auth` y `contenttypes`. El módulo se eliminó al terminar. `config/settings.py` no se modificó.

Aplicación ejecutada:

```powershell
python manage.py migrate
```

Resultado: 19/19 migraciones aplicadas, código de salida 0, sin errores ni advertencias. El detalle está en `documentacion/REVISION_MIGRACION_CUENTAS.md` (sección 6).

---

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El superusuario temporal queda olvidado | Checklist 4.5–4.6 y verificación final de `is_superuser` |
| Pérdida de historial al borrar el temporal | Exportar `LogEntry` antes del borrado |
| La cuenta definitiva no puede gestionar usuarios | Grupo `Administradores` con permisos `add/change/view usuario` |
| Un administrador normal no puede crear otro administrador | Por diseño (decisión 7); se requiere un superusuario temporal por consola |
| `change_usuario` permite restablecer contraseñas | Limitar el grupo a personal de confianza; revisar membresías |
| Se ejecuta `migrate` antes de `makemigrations` | Orden documentado en 3.1 y checklist previa |
| Cambios de roles futuros | Actualizar `choices`, `CheckConstraint` y migración en el mismo cambio |
| `email` duplicado | D08 aprobada: no será único en V1; vigilar duplicados antes de usar correo para notificaciones |

---

## 7. Criterios de aceptación de la Fase 1

| # | Criterio | Estado |
|---|---|---|
| 1 | `manage.py check` sin incidencias tras aplicar los cambios | **Cumplido** (2026-11-26) |
| 2 | La migración `cuentas.0001` incluye los dos `CheckConstraint` | **Cumplido** (2026-11-27) |
| 3 | `auth_user` no existe en la base | **Cumplido** (2026-11-27): `to_regclass('public.auth_user')` devuelve `NULL` |
| 4 | `createsuperuser` genera una cuenta con `rol="administrador"` | Pendiente (no se crean usuarios todavía) |
| 5 | Un intento de dejar `is_superuser=True` con `rol="usuario"` es rechazado por la base | Parcial: las dos restricciones `CHECK` existen en PostgreSQL; el rechazo con `INSERT` no se probó porque no estaba autorizado |
| 6 | El Administrador definitivo inicia sesión, accede a `/admin/` y tiene `rol="administrador"`, `is_staff=True` | Pendiente (requiere crear usuarios) |
| 7 | El superusuario temporal se elimina y ya no existe | Pendiente |
| 8 | El Administrador definitivo sigue funcionando después del borrado | Pendiente |
| 9 | Este informe se actualiza con los resultados reales | **En curso**; se completará al cerrar la fase |

---

## 8. Estado

| Elemento | Estado |
|---|---|
| Decisiones D01–D09 | Aprobadas |
| Código del modelo | **Modificado y verificado** |
| Manager personalizado | **Implementado y probado** |
| Restricciones `CheckConstraint` | **Definidas en el modelo, incluidas en `cuentas.0001` y presentes en PostgreSQL** (verificadas por nombre y definición) |
| Restricciones del admin | **Implementadas, probadas y reforzadas** (sección 2.6) |
| Refuerzo de seguridad del panel | **Implementado como continuación de Fase 0** |
| Pruebas | **52/52 correctas**, sin base de datos |
| `manage.py check` | **0 incidencias** (general, models y admin) |
| `makemigrations` | **Ejecutado el 2026-11-27**, solo para `cuentas` |
| Migración generada | `apps/cuentas/migrations/0001_initial.py` (revisada) |
| `migrate` | **Ejecutado el 2026-11-27 01:40:51 (-05:00)**: 19/19 OK |
| Superusuario temporal | **No creado** |
| Administrador definitivo | **No creado** |
| Grupo `Administradores` | **No creado** |
| Base de datos | 10 tablas; sin `auth_user`; sin bases `test_*` |
| Autorización para crear usuarios | **Pendiente** |

**Siguiente paso:** autorización expresa para crear el superusuario temporal y el grupo `Administradores`. No se inicia la Fase 1. La Fase 0 fue cerrada oficialmente el 2026-11-27.
