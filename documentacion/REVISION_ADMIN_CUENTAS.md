# Revisión de seguridad del panel de administración de cuentas — SismoDetect

**Proyecto:** SismoDetect — Sistema web para la consulta, análisis y clasificación de señales sísmicas en Cuba mediante inteligencia artificial

> La explicabilidad se mantiene como funcionalidad complementaria del sistema.

| Campo | Valor |
|---|---|
| Fecha de la revisión original | 2026-11-26 |
| Fecha de reconstrucción documental | 2026-11-27 |
| Fase | Fase 0 — refuerzo del admin como continuación de la base técnica |
| Alcance | Revisión de código y de pruebas unitarias; **sin** usuarios reales, sesiones ni peticiones HTTP |
| Estado | **Implementado en código y cubierto por 52 pruebas unitarias**; verificación real pendiente |
| Documento vigente de la fase | `documentacion/INFORME_IMPLEMENTACION.md` |

> **Nota de reconstrucción.** Este documento se reconstruyó el 2026-11-27 a partir de información ya registrada en `documentacion/INFORME_IMPLEMENTACION.md` (sección 12), `documentacion/FASE_01_MODELO_USUARIOS.md` (sección 2.6) y la inspección del código real de `apps/cuentas/admin.py`, `apps/cuentas/models.py` y `apps/cuentas/tests.py`. **No se ejecutaron pruebas nuevas con usuarios, sesiones ni HTTP.** No se inventan resultados: lo que no estaba verificado se identifica expresamente como pendiente.

---

## 1. Alcance y fuentes

Esta revisión cubre la política de permisos del modelo `cuentas.Usuario` en `/admin/` y las barreras implementadas en `apps/cuentas/admin.py`.

Fuentes utilizadas:

| Fuente | Uso |
|---|---|
| `apps/cuentas/admin.py` | Comportamiento real del `UsuarioAdmin` |
| `apps/cuentas/models.py` | Rol, `es_administrador` y `CheckConstraint` |
| `apps/cuentas/tests.py` | 52 pruebas `SimpleTestCase` |
| `documentacion/INFORME_IMPLEMENTACION.md` §12 | Política, cambios y resultados documentados |
| `documentacion/FASE_01_MODELO_USUARIOS.md` §2.6 | Resumen de las medidas aplicadas |

Restricciones respetadas: no se crearon usuarios ni grupos, no se modificó PostgreSQL, no se ejecutaron migraciones ni `GRANT`/`REVOKE`, y no se realizaron peticiones HTTP reales.

---

## 2. Política de permisos

| Tipo de cuenta | Permisos efectivos en `/admin/` |
|---|---|
| Superusuario temporal | Gestiona todas las cuentas; crea y configura al Administrador definitivo; asigna `rol`, `is_staff`, `is_superuser`, grupos y permisos; gestiona otros superusuarios |
| Administrador normal | Accede al panel; crea, consulta, edita y gestiona **usuarios normales** y su propia cuenta; no ve ni modifica otros administradores; no cambia contraseñas, `is_active` ni datos de otros administradores; **no puede desactivar su propia cuenta**; no borra usuarios; no crea administradores ni superusuarios; no modifica campos reservados ni `last_login`/`date_joined`; no gestiona grupos ni permisos de Django; puede cambiar su propia contraseña |
| Usuario normal | Sin acceso al panel; no gestiona cuentas |

La distinción efectiva se apoya en dos condiciones: `is_superuser` para el acceso total y `rol="administrador"` para reconocer a un administrador funcional. Un administrador normal necesita además `is_staff=True` y los permisos `cuentas.add_usuario`, `cuentas.change_usuario` y `cuentas.view_usuario`, que en el diseño aprobado se asignan mediante el grupo `Administradores`.

---

## 3. Protecciones implementadas

### 3.1 Protección frente a otros administradores

- `get_queryset()` devuelve, para un no superusuario, solo su propia cuenta y los usuarios con `is_superuser=False` y `rol != "administrador"`.
- `has_view_permission()` y `has_change_permission()` deniegan cualquier administrador distinto del propio usuario.
- `user_change_password()` comprueba el objetivo antes de delegar en Django: si es otro administrador, lanza `PermissionDenied`; si es la propia cuenta o un usuario normal, lo permite.
- `save_model()` lanza `PermissionDenied` si un no superusuario intenta editar a otro administrador, incluso con un POST manipulado.
- Un administrador normal **no puede convertir** a un usuario normal en administrador ni asignarle `is_staff`, `is_superuser`, grupos o permisos.

### 3.2 Protección de grupos, permisos y campos reservados

Los campos `rol`, `is_staff`, `is_superuser`, `groups`, `user_permissions`, `last_login` y `date_joined` quedan fuera de los formularios de un administrador normal mediante listas blancas en `get_fieldsets()` y `get_form()`:

- **Alta:** solo `username`, `usable_password`, `password1` y `password2`.
- **Edición:** solo `username`, `password`, `first_name`, `last_name`, `email` e `is_active`.
- `last_login` y `date_joined` son de solo lectura para no superusuarios.
- `save_model()` fuerza en el alta `rol="usuario"`, `is_staff=False` e `is_superuser=False`; en la edición de un usuario normal mantiene esos valores.
- `save_related()` limpia `groups` y `user_permissions` al crear un usuario desde una cuenta no superusuario.

### 3.3 Protección frente a la auto-desactivación

Un administrador normal **no puede desactivar su propia cuenta**. La protección tiene dos capas:

1. **Formulario:** `get_readonly_fields()` añade `is_active` a los campos de solo lectura cuando el objeto editado es la propia cuenta y quien edita no es superusuario. `get_form()` excluye ese campo, por lo que un valor enviado en un POST manipulado es ignorado.
2. **Servidor:** `save_model()` comprueba, antes de guardar, si el objeto es la propia cuenta y llega con `is_active=False`; en ese caso lanza `PermissionDenied`, aunque el valor provenga de una petición manipulada o de un formulario simulado.

La comprobación usa `_es_propia_cuenta()`, que compara la clave primaria del usuario autenticado con la del objeto y exige `is_authenticated=True`. Solo se aplica a no superusuarios: el superusuario conserva la posibilidad de desactivarse si lo decide.

El cambio de contraseña propia sigue funcionando porque transcurre por `user_change_password()`, no por `save_model()`. Los administradores normales pueden seguir desactivando **usuarios normales**; la restricción afecta únicamente a su propia cuenta.

### 3.4 Gestión de usuarios normales y de la cuenta propia

Un administrador normal puede:

- crear usuarios normales (que quedan como `rol="usuario"`, sin staff, sin superusuario y sin grupos ni permisos);
- consultar y editar datos básicos de usuarios normales;
- cambiar la contraseña de un usuario normal;
- cambiar su propia contraseña;
- editar su propia cuenta, salvo dejarla inactiva.

No puede borrar usuarios: `has_delete_permission()` devuelve siempre `False` para no superusuarios y `get_actions()` retira `delete_selected`.

### 3.5 Protección del superusuario

- El superusuario no sufre el filtrado de `get_queryset()`.
- Conserva los campos reservados en alta y edición.
- Conserva los permisos de cambio y borrado.
- `user_change_password()` delega directamente en Django.
- Puede gestionar otros administradores y superusuarios.
- Conserva la posibilidad de desactivar su propia cuenta.

---

## 4. Implementación en `apps/cuentas/admin.py`

| Medida | Implementación |
|---|---|
| Listas blancas por rol | `CAMPOS_PERMITIDOS_ALTA_ADMIN_NORMAL`, `CAMPOS_PERMITIDOS_EDICION_ADMIN_NORMAL`, `CAMPOS_SOLO_LECTURA_ADMIN_NORMAL` |
| Consulta filtrada | `get_queryset()` |
| Formularios restringidos | `get_fieldsets()`, `get_form()`, `_solo_campos_permitidos()` |
| Campos de solo lectura | `get_readonly_fields()` |
| Sin borrado | `has_delete_permission()`, `get_actions()` |
| Denegación de otros administradores | `has_view_permission()`, `has_change_permission()`, `save_model()` |
| Contraseñas protegidas | `user_change_password()` |
| Política aplicada en servidor | `save_model()` |
| Grupos y permisos limpios en alta | `save_related()` |

Funciones auxiliares: `_es_administrador()`, `_es_otro_administrador()` y `_es_propia_cuenta()`.

---

## 5. Pruebas existentes y resultados

`apps/cuentas/tests.py` contiene **52 pruebas `SimpleTestCase`**, sin base de datos (`Skipping setup of unused database(s): default`).

Cobertura por grupo:

| Grupo | Qué comprueba |
|---|---|
| Modelo | rol por defecto, `choices`, `es_administrador` por rol y por `is_superuser`, manager, restricciones, `__str__` |
| `save()` | fuerza el rol del superusuario, respeta el rol normal y añade `rol` a `update_fields` |
| Manager | `create_superuser()` asigna `rol="administrador"` |
| Admin inicial | campos reservados ocultos, rol oculto al crear, cambio/borrado de superusuarios denegado |
| Admin reforzado | consulta filtrada, ver/editar/borrar, contraseñas, listas blancas, fechas de solo lectura, `save_model`, `save_related`, acciones y acceso al panel |
| Auto-desactivación | bloqueo en formulario y en `save_model`, incluso con formulario simulado; el superusuario conserva la capacidad |

Resultados documentados:

| Comprobación | Resultado |
|---|---|
| `manage.py check` | 0 incidencias |
| `manage.py check --tag models` | 0 incidencias |
| `manage.py check --tag admin` | 0 incidencias |
| `manage.py check --database default` | 0 incidencias |
| `manage.py test apps.cuentas -v 1` | **52/52 OK** (documentado el 2026-11-26 en 0.079 s; la auditoría del 2026-11-27 las repitió con 52/52 OK) |

---

## 6. Limitaciones y comprobaciones pendientes

- Las pruebas son `SimpleTestCase` con mocks: verifican lógica, rutas y barreras de servidor, **no persistencia real**, formularios HTML reales ni sesiones.
- **No se ejecutó HTTP real** contra `/admin/`; no hay usuarios creados.
- No se verificó en base el grupo `Administradores` ni su conjunto exacto de permisos (`add_usuario`, `change_usuario`, `view_usuario`; sin `delete_usuario` ni permisos `auth.*`).
- Los dos `CheckConstraint` existen en PostgreSQL, pero **no se probó el rechazo real** con un `INSERT` inválido (requiere escritura no autorizada).
- No se ha ejecutado el protocolo del superusuario temporal ni el alta del Administrador definitivo.
- Sigue vigente el riesgo operativo: tras eliminar al superusuario temporal no habrá superusuarios; crear uno exigirá consola/`createsuperuser`.

---

## 7. Qué está verificado y qué falta

| Elemento | Estado |
|---|---|
| Política de permisos en código | **Verificada por inspección** |
| Listas blancas de campos | **Verificadas por inspección y pruebas unitarias** |
| Denegación de otros administradores | **Verificada por pruebas unitarias** |
| Protección de contraseñas | **Verificada por pruebas unitarias** |
| Bloqueo de borrado | **Verificado por pruebas unitarias** |
| Protección contra auto-desactivación | **Verificada en formulario y `save_model` con pruebas unitarias** |
| Persistencia real de las reglas | **Pendiente** (requiere usuarios y base real) |
| Inicio de sesión y `/admin/` con cuentas reales | **Pendiente** |
| Grupo `Administradores` y permisos efectivos | **Pendiente de creación y verificación** |
| Rechazo de `CHECK` con `INSERT` inválido | **Pendiente de autorización** |

---

## 8. Conclusión

El refuerzo del panel está **implementado en código** y cubierto por 52 pruebas unitarias que pasan. El diseño aplica la política en el servidor y no solo en la interfaz. Sin embargo, la verificación de extremo a extremo con usuarios reales, sesiones, peticiones HTTP, grupo `Administradores` y restricciones ejercitadas sigue pendiente y pertenece al arranque controlado de la Fase 1.

Este documento no inicia la Fase 1; la Fase 0 fue cerrada oficialmente el 2026-11-27.
