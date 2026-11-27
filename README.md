# SismoDetect

Sistema web para la consulta, análisis y clasificación de señales sísmicas en
Cuba mediante inteligencia artificial.

> La explicabilidad se mantiene como funcionalidad complementaria del sistema.
> SismoDetect **no predice terremotos ni es un sistema de alerta temprana**.

**Estado:** Fase 0 — base técnica verificada y **cerrada oficialmente** el
2026-11-27. Primera publicación completada en GitHub (commit inicial
`e4c00a0`). No se ha iniciado la Fase 1.

---

## Entorno actual

| Elemento | Versión / valor |
|---|---|
| Python | 3.13.0 |
| Django | 6.1.3 |
| PostgreSQL | 18.7 |
| Base de datos | `sismodetect` |
| Usuario de conexión | `sismodetect_app` (sin `CREATEDB`, `CREATEROLE` ni superusuario) |
| Adaptador | `psycopg[binary]` 3.3.9 |
| TensorFlow / Keras / NumPy | 2.21.0 / 3.15.1 / 2.5.5 |

El entorno virtual `.venv` existe en este equipo y **no se incluye en el
repositorio**. Las credenciales se leen desde `.env`, que está ignorado por
Git; no se registran secretos en este archivo ni en la documentación.

---

## Estructura

| Ruta | Contenido actual |
|---|---|
| `config/` | Configuración Django (`settings`, `urls`, `wsgi`, `asgi`). |
| `apps/catalogo/` | Aplicación Django creada (esqueleto, sin modelos aún). |
| `apps/adquisicion/` | Aplicación Django creada (esqueleto, sin modelos aún). |
| `apps/analisis/` | Aplicación Django creada (esqueleto, sin modelos aún). |
| `apps/cuentas/` | Modelo de usuario, admin, migración y 52 pruebas. |
| `apps/interfaz/` | Aplicación Django creada (esqueleto, sin modelos aún). |
| `ia/pesos/cnn_v1/` | Artefactos congelados de la CNN V1. |
| `data/`, `logs/`, `static/`, `templates/` | Carpetas base con marcadores. |
| `documentacion/` | Informes y decisiones del proyecto. |
| `requirements/` | `base.txt`, `tensorflow.txt`, `dev.txt`, `dev-ia.txt`. |
| `tests/` | Espacio reservado para pruebas generales. |

El modelo de usuario activo es `cuentas.Usuario` (`AUTH_USER_MODEL`), basado en
`AbstractUser`, con campo `rol` (`administrador` / `usuario`) y dos
`CheckConstraint`. No existe `auth_user`.

---

## Implementado

- Proyecto Django 6.1.3 con configuración para PostgreSQL 18.7 y base
  `sismodetect`; conexión verificada con el rol `sismodetect_app`.
- Cinco aplicaciones Django registradas; `manage.py check` y
  `manage.py check --database default` sin incidencias.
- Modelo personalizado `cuentas.Usuario`, `UsuarioManager`, `es_administrador`
  y dos restricciones `CHECK` activas en PostgreSQL.
- Controles del panel de administración **implementados en código**:
  listas blancas de campos, filtrado de consulta, denegación de acceso a otros
  administradores, protección de contraseñas, bloqueo de borrado y protección
  frente a la auto-desactivación. Cubiertos por 52 pruebas unitarias.
- **19/19 migraciones aplicadas** el 2026-11-27: 10 tablas en `public`,
  `cuentas_usuario` presente y `auth_user` ausente. No hay usuarios ni grupos
  creados.
- Seis artefactos de la CNN V1 verificados por SHA-256, modelo cargable con
  entrada `(None, 3000, 3)`, umbral y estadísticas congelados.
- Dataset externo de 1555 segmentos, con partición canónica verificada.

---

## Pendiente

- Registro público de usuarios (no existe vista ni formulario).
- Creación del superusuario temporal, del grupo `Administradores` y del
  Administrador definitivo; verificación real de `/admin/` con usuarios,
  sesiones y peticiones HTTP.
- Comprobación real del rechazo de los `CHECK` con un `INSERT` inválido.
- Cliente FDSN (IRIS/EarthScope) y descarga de MiniSEED.
- Lector MiniSEED y validador de ventana.
- Carga de la CNN, preprocesamiento e inferencia integrada en Django.
- Vistas, formularios, plantillas, interfaz web e historial.
- XAI complementaria.
- Copias de seguridad y endurecimiento para producción.
- Pruebas funcionales de las apps distintas de `cuentas`.

**El sistema todavía no clasifica señales desde la web.**

---

## Dataset externo

El dataset usado para entrenar y evaluar la CNN V1 **no está dentro de este
repositorio**. La copia local verificada se encuentra en:

```text
D:\Escuela\Inteligencia Artificial\Dataset\dataset_sismico_cubano
```

La fuente canónica de la partición final es `colab/splits_alternativo.csv`
(columna `split_alternativo`), con resumen en
`colab/split_alternativo_resumen.json`: 1245 entrenamiento / 155 validación /
155 prueba. `metadata.csv` (1383 filas) y la columna antigua `split` son
referencias históricas, no la partición vigente. Ver
`documentacion/INFORME_IMPLEMENTACION.md`, sección 14.

---

## Comprobaciones habituales

```powershell
cd 'D:\Escuela\Inteligencia Artificial\SismoDetect'
.\.venv\Scripts\Activate.ps1

python manage.py check
python manage.py check --database default
python manage.py showmigrations
python manage.py makemigrations --check --dry-run
python manage.py test apps.cuentas -v 1
```

`manage.py makemigrations --check --dry-run` informa `No changes detected` con
la configuración actual. No se debe generar una migración cosmética sin revisar
antes su contenido y su SQL.

Para instalar dependencias en un equipo nuevo:

```powershell
python -m pip install -r requirements\base.txt        # Django sin IA
python -m pip install -r requirements\tensorflow.txt  # Django con CNN/IA
```

---

## Documentación

| Documento | Uso |
|---|---|
| `documentacion/INFORME_IMPLEMENTACION.md` | **Estado vigente** de la Fase 0. |
| `documentacion/FASE_01_MODELO_USUARIOS.md` | Decisiones D01–D09 y protocolo pendiente. |
| `documentacion/REVISION_MIGRACION_CUENTAS.md` | Generación, revisión y aplicación de `cuentas.0001`. |
| `documentacion/REVISION_ADMIN_CUENTAS.md` | Política de permisos del admin y sus límites de verificación. |
| `documentacion/INSPECCION_CNN_V1.md` | Inspección histórica del modelo. |
| `documentacion/AUDITORIA_FASE_0.md` | Auditoría histórica del estado inicial (2026-11-25). |
| `documentacion/INFORME_PREPARACION_GIT.md` | Preparación y publicación inicial en GitHub. |

Repositorio: https://github.com/Francisalejandro/SismoDetect

La Fase 0 está oficialmente cerrada. El inicio de la Fase 1 requiere decisión
expresa del usuario.
