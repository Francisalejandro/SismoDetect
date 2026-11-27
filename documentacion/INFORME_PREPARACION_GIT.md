# Informe de preparación para Git — SismoDetect

**Proyecto:** SismoDetect — Sistema web para la consulta, análisis y clasificación de señales sísmicas en Cuba mediante inteligencia artificial

| Campo | Valor |
|---|---|
| Fecha | 2026-11-27 |
| Fase | Fase 0 — primera publicación oficial completada |
| Alcance | `.gitignore`, `.gitattributes`, revisión de `.env.example`, inicialización y publicación |
| Repositorio local | Inicializado en `main`; remoto `origin` configurado |
| Repositorio remoto | `https://github.com/Francisalejandro/SismoDetect.git`; `origin/main` sincronizada |
| Primer commit | `e4c00a0c7bbff45ab6cbb0134106ea33ce8d29ca` |
| Resultado | **Publicación completada** el 2026-11-27; ver sección 11 |

> Durante la fase de preparación no se ejecutaron operaciones Git de escritura. La publicación posterior sí ejecutó, con autorización expresa, `git init`, `git remote add`, `git add`, `git commit` y `git push -u origin main`. No se imprimieron valores de `.env` ni se copiaron credenciales reales.

---

## 1. Cambios realizados

| Archivo | Acción |
|---|---|
| `.gitignore` | Actualizado: se conservaron todas las reglas existentes, se ajustó la regla `*.keras` y se añadieron reglas preventivas. |
| `.gitattributes` | **Creado**: normalización de finales de línea para texto y preservación de bytes en artefactos binarios y congelados. |
| `.env.example` | Solo lectura: se verificó que no contiene credenciales reales. No se modificó. |
| `documentacion/INFORME_PREPARACION_GIT.md` | **Creado**: este informe. |

No se modificaron archivos Python, configuración Django, dependencias, migraciones, modelos, base de datos ni artefactos de la CNN.

---

## 2. Reglas de `.gitignore`

### 2.1 Conservadas sin cambios

```
.venv/
.idea/
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
build/
dist/
db.sqlite3
*.log
media/
staticfiles/
data/entrada/*  con !data/entrada/.gitkeep
data/temporal/* con !data/temporal/.gitkeep
data/registros/* con !data/registros/.gitkeep
logs/*          con !logs/.gitkeep
.pytest_cache/
.coverage
htmlcov/
.ruff_cache/
Thumbs.db
.DS_Store
.env
```

### 2.2 Ajustadas

- **`*.keras`**: se mantuvo la exclusión por defecto para modelos futuros y se añadió una excepción explícita:

  ```gitignore
  *.keras
  !ia/pesos/cnn_v1/mejor_modelo_cnn_v1.keras
  ```

  El modelo de CNN V1 pasa a ser candidato a publicación; cualquier otro `.keras` sigue excluido.

- **Variables de entorno**: la regla final `.env` se amplió para cubrir variantes, conservando la plantilla:

  ```gitignore
  .env
  .env.*
  !.env.example
  ```

### 2.3 Añadidas

| Bloque | Reglas | Motivo |
|---|---|---|
| IDE | `.vscode/`, `*.iml` | Configuración personal adicional. |
| Python | `.mypy_cache/`, `.tox/`, `.nox/` | Cachés de herramientas. |
| Django/BD | `*.sqlite3`, `*.db` | Otras bases de datos locales. |
| Señales y datos | `*.mseed`, `*.miniseed`, `*.npy`, `*.csv` | Evitar copias locales del dataset. |
| Claves | `*.pem`, `*.key`, `*.p12`, `*.pfx` | Claves privadas y certificados. |
| Comprimidos/temporales | `*.zip`, `*.tar`, `*.tar.gz`, `*.tgz`, `*.gz`, `*.7z`, `*.rar`, `*.tmp`, `*.temp`, `*.bak`, `*.old`, `*.swp`, `*.swo` | Archivos generados o temporales. |

**Nota sobre CSV:** antes de añadir `*.csv` se revisó el árbol completo de archivos. **No existe ningún `.csv` en el proyecto**, por lo que no se excluyó ningún recurso legítimo. Si en el futuro se añade un CSV que forme parte del código, la documentación o la configuración, deberá permitirse de forma explícita con una regla `!ruta/al/archivo.csv`.

---

## 3. Contenido de `.gitattributes`

```gitattributes
# Normalización de finales de línea para archivos de texto.
* text=auto

*.py         text eol=lf
*.md         text eol=lf
*.txt        text eol=lf
*.json       text eol=lf
*.yml        text eol=lf
*.yaml       text eol=lf
*.ini        text eol=lf
*.cfg        text eol=lf
*.gitignore  text eol=lf
*.gitattributes text eol=lf
*.gitkeep    text eol=lf
*.example    text eol=lf

# Archivos binarios: sin conversión de finales de línea.
*.keras   binary
*.npz     binary
*.npy     binary
*.pyc     binary
*.sqlite3 binary
*.db      binary
*.png     binary
*.jpg     binary
*.jpeg    binary
*.gif     binary
*.ico     binary
*.pdf     binary

# Artefactos congelados de la CNN V1: conservar los bytes exactos,
# porque sus hashes SHA-256 están registrados en inventario_sha256.json.
ia/pesos/cnn_v1/** -text
```

La regla final `ia/pesos/cnn_v1/** -text` evita que `INFORME_FINAL_CNN_V1.md` y los JSON del inventario sufran conversión de saltos de línea, de modo que sus hashes SHA-256 se mantengan.

---

## 4. CNN V1 y verificación SHA-256

Los seis artefactos están presentes y sus hashes **coinciden 6/6** con `ia/pesos/cnn_v1/inventario_sha256.json`:

| Artefacto | SHA-256 | Estado |
|---|---|---|
| `mejor_modelo_cnn_v1.keras` | `cd9e8962d1cd…` | Correcto |
| `estadisticas_normalizacion.npz` | `dea35212ca9e…` | Correcto |
| `manifiesto_preprocesamiento.json` | `f61217fd1cad…` | Correcto |
| `seleccion_umbral_v1.json` | `78228b4433ef…` | Correcto |
| `configuracion_entrenamiento.json` | `cb7ecf197538…` | Correcto |
| `INFORME_FINAL_CNN_V1.md` | `48cd811353c2…` | Correcto |

El modelo `.keras` tiene 602 838 bytes (aprox. 589 KiB) y es candidato a publicación gracias a la excepción añadida. El inventario `inventario_sha256.json` también se publica. No se modificó, regeneró ni entrenó ningún artefacto.

---

## 5. Verificación de `.env.example`

- Existe `.env.example` con 9 asignaciones.
- Los dos campos sensibles (`DJANGO_SECRET_KEY` y `DB_PASSWORD`) contienen **marcadores de posición**, no valores reales.
- Los valores reales presentes en `.env` **no aparecen en ningún otro archivo** del proyecto (0 coincidencias).
- No se imprimió el contenido de `.env`.

---

## 6. Archivos excluidos y motivos

| Archivo / patrón | Motivo |
|---|---|
| `.env` | Contiene clave secreta de Django y contraseña de base de datos. |
| `.venv/` | Entorno virtual local; 27 384 archivos, ~1.63 GiB. |
| `.idea/`, `.vscode/`, `*.iml` | Configuración personal del IDE. |
| `__pycache__/`, `*.pyc` | Cachés de Python. |
| `db.sqlite3`, `*.sqlite3`, `*.db` | Bases de datos locales. |
| `logs/*.log`, `*.log` | Registros locales. |
| `data/entrada/*`, `data/temporal/*`, `data/registros/*` | Datos locales; se conservan solo los `.gitkeep`. |
| `*.mseed`, `*.miniseed`, `*.npy`, `*.csv` | Señales y datos locales; ninguno existe hoy en el proyecto. |
| `*.pem`, `*.key`, `*.p12`, `*.pfx` | Claves privadas y certificados. |
| `*.zip`, `*.tar*`, `*.gz`, `*.7z`, `*.rar`, `*.tmp`, `*.temp`, `*.bak`, `*.old`, `*.swp`, `*.swo` | Comprimidos y temporales. |
| Cachés de pruebas y herramientas | Generadas localmente. |
| Dataset sísmico externo | Está fuera del proyecto, en `D:\Escuela\Inteligencia Artificial\Dataset\dataset_sismico_cubano`; no se copió ni se publicará. |

No se utilizó `git add -f` ni se forzó ningún archivo ignorado.

---

## 7. Archivos candidatos a publicación

Verificación realizada con un comparador de patrones compatible con la ausencia de repositorio Git (no se inicializó Git para usar `git check-ignore`).

| Grupo | Archivos |
|---|---|
| `apps/` | 37 (5 apps, modelos, admin, pruebas, vistas, `migrations/0001_initial.py` y `__init__.py`) |
| `ia/` | 14 (paquetes y los 6 artefactos de CNN V1 + inventario + `.gitkeep`) |
| `documentacion/` | 9 documentos vigentes e históricos |
| `config/` | 5 (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`, `__init__.py`) |
| `requirements/` | 4 (`base.txt`, `tensorflow.txt`, `dev.txt`, `dev-ia.txt`) |
| `data/` | 3 marcadores `.gitkeep` |
| `tests/`, `static/`, `templates/`, `logs/` | 1 marcador cada uno |
| Raíz | `manage.py`, `README.md`, `.gitignore`, `.gitattributes`, `.env.example` |

**Total:** 82 archivos candidatos (incluido este informe).

Comprobaciones puntuales del comparador:

| Ruta | Resultado |
|---|---|
| `.env` | Excluido |
| `.env.example` | Incluido |
| `.venv/Scripts/python.exe` | Excluido |
| `.idea/workspace.xml` | Excluido |
| `apps/cuentas/__pycache__/tests.cpython-313.pyc` | Excluido |
| `db.sqlite3` | Excluido |
| `logs/sismodetect.log` | Excluido |
| `logs/.gitkeep`, `data/entrada/.gitkeep` | Incluidos |
| `ia/pesos/cnn_v1/mejor_modelo_cnn_v1.keras` | **Incluido** |
| `ia/pesos/cnn_v1/mejor_modelo_cnn_v2.keras` (hipotético) | Excluido |
| `dataset.csv`, `data/senales.mseed`, `clave.pem` (hipotéticos) | Excluidos |

Revisión de nombres y rutas: **0 rutas con caracteres no ASCII, espacios problemáticos o longitud excesiva**. No hay enlaces simbólicos. El archivo más grande es `mejor_modelo_cnn_v1.keras` (589 KiB); ninguno supera 1 MiB. No hay duplicados problemáticos: los grupos existentes son archivos vacíos y esqueletos idénticos de apps sin implementar.

---

## 8. Tamaño aproximado de la primera publicación

| Concepto | Valor |
|---|---|
| Archivos candidatos | 82 (incluido este informe) |
| Bytes estimados | ~917 000 |
| Tamaño | **~0.88 MiB** |
| Sin el `.keras` (escenario anterior) | ~0.30 MiB, 81 archivos |

---

## 9. Riesgos y pendientes

| ID | Severidad | Hallazgo |
|---|---|---|
| R01 | ALTO | `.env` contiene secretos reales. La única barrera es `.gitignore`; debe comprobarse de nuevo justo antes del primer `git add`. |
| R02 | MEDIO | La regla global `*.csv` protege contra datos locales, pero impedirá versionar CSV legítimos futuros salvo excepción explícita. |
| R03 | RESUELTO | La simulación de patrones se repitió con `git check-ignore` tras `git init`; los resultados coincidieron y se comprobó el área de preparación antes del commit. |
| R04 | BAJO | El repositorio es público y el primer push creó el historial. No debe usarse `--force` en pushes posteriores. |
| R05 | BAJO | `DEBUG=True`, backend de correo de consola y ausencia de HSTS/SSL siguen siendo configuraciones de desarrollo, no de producción. |

No se detectaron credenciales en `.env.example`, claves privadas, tokens ni copias del dataset dentro del proyecto.

---

## 10. Confirmación de la fase de preparación

- Durante la preparación no se ejecutaron operaciones Git de escritura ni publicación; la publicación se ejecutó después con autorización (sección 11).
- No se modificaron código, migraciones, dependencias, configuración Django ni base de datos.
- No se modificaron los artefactos de la CNN V1; sus 6 hashes siguen siendo correctos.
- La Fase 0 está oficialmente cerrada.

---

## 11. Publicación completada (2026-11-27)

| Paso | Resultado |
|---|---|
| `git init -b main` | Repositorio local inicializado en `main`. |
| `git remote add origin https://github.com/Francisalejandro/SismoDetect.git` | Remoto configurado; no existía `origin` previo. |
| `git add -A` | 82 archivos preparados; sin `.env`, `.venv/`, `.idea/`, cachés, logs, bases locales ni datos sísmicos. |
| `git diff --cached --check` | Solo avisos de whitespace en un documento histórico y en `INFORME_FINAL_CNN_V1.md`; este último es un artefacto con hash congelado y no se modificó. |
| Primer commit | `e4c00a0c7bbff45ab6cbb0134106ea33ce8d29ca` — `chore: initial publication of SismoDetect`; 82 archivos, 7044 inserciones. |
| `git push -u origin main` | Correcto; rama `main` configurada para seguir `origin/main`. No se usó `--force`. |
| Verificación remota | API de GitHub confirma el commit y los 8 entradas de `ia/pesos/cnn_v1/` (6 artefactos + inventario + `.gitkeep`). |
| Sincronización | `main` y `origin/main` apuntan al mismo commit; árbol de trabajo limpio. |

Enlace: https://github.com/Francisalejandro/SismoDetect

**Estado: publicación completada. No se inicia la Fase 1.**
