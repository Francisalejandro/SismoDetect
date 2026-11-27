# Inspección técnica — CNN 1D V1

> **Documento histórico.** Esta inspección se realizó el **2026-11-19**, antes de la integración de la CNN con Django. Los artefactos del modelo y sus hashes siguen vigentes, pero el estado de integración descrito aquí (componentes de `ia/` pendientes y apps Django inexistentes) **no representa el estado actual**. El estado vigente está en `documentacion/INFORME_IMPLEMENTACION.md`. Para la fuente canónica de las particiones del dataset, véase la nota posterior de la sección 11.

**Proyecto:** SismoDetect
**Fecha de inspección:** 2026-11-19
**Fase:** inspección previa a la integración con Django
**Alcance:** solo lectura. No se entrenó, reevaluó ni modificó el modelo.
**Estado:** informe de inspección completado; integración aún no implementada.

---

## 1. Objetivo de la inspección

Verificar, antes de autorizar cualquier modificación, que los artefactos de la
CNN 1D V1 son los esperados, que están íntegros y que pueden utilizarse en el
entorno local del proyecto SismoDetect.

Objetivos específicos:

1. Revisar la estructura actual del proyecto.
2. Comprobar la presencia de los siete archivos esperados en `ia/pesos/cnn_v1/`.
3. Verificar las huellas SHA-256 contra el inventario proporcionado.
4. Identificar la arquitectura real y el preprocesamiento documentado.
5. Comprobar la compatibilidad del entorno virtual con el archivo `.keras`.
6. Determinar qué componentes faltan para integrar la CNN con Django.

Restricciones respetadas durante la inspección:

- No se modificó, creó, eliminó ni movió ningún archivo del modelo.
- No se entrenó ni se reevaluó el modelo.
- No se modificaron las estadísticas de normalización ni el umbral.
- No se instalaron ni actualizaron dependencias.
- No se implementó la integración.

---

## 2. Estructura y archivos encontrados

### 2.1 Estructura general del proyecto

```
SismoDetect/
├── apps/                  → solo __init__.py (sin apps funcionales)
├── config/                → settings.py, urls.py, asgi.py, wsgi.py
├── data/
│   ├── entrada/           → solo .gitkeep
│   └── temporal/          → solo .gitkeep
├── documentacion/         → documentación del proyecto
├── ia/
│   ├── modelos/           → solo __init__.py
│   ├── procesamiento/     → solo __init__.py
│   ├── inferencia/        → solo __init__.py
│   ├── gestor_modelos/    → solo __init__.py
│   └── pesos/cnn_v1/      → artefactos de la CNN V1
├── requirements/          → base.txt, tensorflow.txt, dev.txt, dev-ia.txt
├── tests/                 → solo __init__.py
├── manage.py
├── db.sqlite3
└── README.md
```

Observaciones:

- El proyecto es un esqueleto Django. No existe ninguna aplicación funcional
  en `apps/`.
- `config/settings.py` corresponde a la configuración estándar de Django
  6.1.3: `DEBUG = True`, `ALLOWED_HOSTS = []`, base de datos SQLite y sin
  aplicaciones propias registradas.
- `config/urls.py` solo expone la ruta `admin/`.
- Los paquetes `ia/modelos/`, `ia/procesamiento/`, `ia/inferencia/` y
  `ia/gestor_modelos/` contienen únicamente su `__init__.py` con docstrings
  orientativos; no tienen lógica implementada.
- `data/entrada/` y `data/temporal/` están vacías salvo por sus `.gitkeep`.
- La carpeta del proyecto no es un repositorio Git.
- El `.gitignore` excluye `*.keras`, `*.h5`, `*.tflite` y otros formatos de
  pesos, por lo que los artefactos del modelo no se versionarían en Git.

### 2.2 Archivos de la CNN V1

Carpeta inspeccionada: `ia/pesos/cnn_v1/`

| # | Archivo | Tamaño | Estado |
|---|---|---:|---|
| 1 | `mejor_modelo_cnn_v1.keras` | 602 838 B | Presente y legible |
| 2 | `estadisticas_normalizacion.npz` | 1 344 B | Presente y legible |
| 3 | `manifiesto_preprocesamiento.json` | 1 011 B | Presente y legible |
| 4 | `configuracion_entrenamiento.json` | 1 873 B | Presente y legible |
| 5 | `seleccion_umbral_v1.json` | 756 B | Presente y legible |
| 6 | `INFORME_FINAL_CNN_V1.md` | 6 301 B | Presente y legible |
| 7 | `inventario_sha256.json` | 919 B | Presente y legible |

Además de los siete archivos esperados, la carpeta contiene un archivo
`.gitkeep`.

**Resultado:** los 7 archivos esperados están presentes. No falta ninguno.

---

## 3. Verificación de integridad SHA-256

El archivo `inventario_sha256.json` contiene las huellas y los tamaños de seis
artefactos. No incluye su propia huella, lo cual es esperado, ya que un archivo
no puede contener de forma autorreferente su propio SHA-256.

| Archivo | SHA-256 esperado | SHA-256 calculado | Bytes esperados | Bytes reales | Resultado |
|---|---|---|---:|---:|---|
| `mejor_modelo_cnn_v1.keras` | `cd9e8962d1cdc2977ef15854a416a89c87591d489d870d86f2b64a05e3f2a0d5` | `cd9e8962d1cdc2977ef15854a416a89c87591d489d870d86f2b64a05e3f2a0d5` | 602 838 | 602 838 | Coincide |
| `estadisticas_normalizacion.npz` | `dea35212ca9e992ef6895e465f331e3ba43ea1e87bee15507ccf83ad16d5b32d` | `dea35212ca9e992ef6895e465f331e3ba43ea1e87bee15507ccf83ad16d5b32d` | 1 344 | 1 344 | Coincide |
| `manifiesto_preprocesamiento.json` | `f61217fd1cad73c127993f589160067d7995dd5c81103f3439660f0cb6c6e8ed` | `f61217fd1cad73c127993f589160067d7995dd5c81103f3439660f0cb6c6e8ed` | 1 011 | 1 011 | Coincide |
| `seleccion_umbral_v1.json` | `78228b4433efb6cbe5907311003948e9af92e5952dfe6b7cf38e0c9c11680475` | `78228b4433efb6cbe5907311003948e9af92e5952dfe6b7cf38e0c9c11680475` | 756 | 756 | Coincide |
| `configuracion_entrenamiento.json` | `cb7ecf197538ed7e0d7bc4b8b4cc77a22e162324e978eaf480dd10d7f5f4cc45` | `cb7ecf197538ed7e0d7bc4b8b4cc77a22e162324e978eaf480dd10d7f5f4cc45` | 1 873 | 1 873 | Coincide |
| `INFORME_FINAL_CNN_V1.md` | `48cd811353c29a64aa3f9115274dac2c8c659c38280d70717246ac9f7527a772` | `48cd811353c29a64aa3f9115274dac2c8c659c38280d70717246ac9f7527a772` | 6 301 | 6 301 | Coincide |

**Resultado: 6/6 huellas coinciden; 0 discrepancias.**

La verificación se repitió al final de la inspección y las huellas seguían
intactas, por lo que la inspección no alteró los artefactos.

Dato adicional de trazabilidad, calculado durante la inspección pero **no
respaldado por el inventario**:

```
inventario_sha256.json
fffa00bc35c5ffcfad7104f9c523f1dc3eb24ca941b2d761a926fb0b774ac635
```

El hash del modelo coincide con el declarado en `seleccion_umbral_v1.json` y en
`INFORME_FINAL_CNN_V1.md`, por lo que la identificación del modelo es
consistente entre los tres documentos.

---

## 4. Características de la arquitectura CNN 1D V1

### 4.1 Formato del archivo

El archivo `mejor_modelo_cnn_v1.keras` es un archivo ZIP con la estructura de
Keras 3:

| Entrada interna | Tamaño |
|---|---:|
| `metadata.json` | 64 B |
| `config.json` | 12 508 B |
| `model.weights.h5` | 589 936 B |

Metadatos del guardado:

- Formato: Keras 3, clase `Sequential`.
- Versión de Keras que guardó el archivo: 3.13.2.
- Fecha de guardado: `2026-11-17@02:13:35`.
- Entrada declarada: `(None, 3000, 3)`.
- Salida declarada: `(None, 1)`.
- Configuración de compilación incluida: optimizador Adam,
  `binary_crossentropy`, métricas `BinaryAccuracy`, `Precision`, `Recall`,
  `ROC-AUC` y `PR-AUC`.
- Learning rate almacenado en el optimizador:
  `0.0002500000118743628`, coherente con la reducción aplicada durante el
  entrenamiento (el valor inicial era 0.001).

### 4.2 Capas verificadas cargando el modelo real

| # | Capa | Tipo | Detalle |
|---:|---|---|---|
| 0 | `conv1d_3` | Conv1D | 32 filtros, kernel 7, padding `same`, activación lineal |
| 1 | `batch_normalization_3` | BatchNormalization | — |
| 2 | `re_lu_3` | ReLU | — |
| 3 | `max_pooling1d_3` | MaxPooling1D | — |
| 4 | `conv1d_4` | Conv1D | 64 filtros, kernel 5, padding `same` |
| 5 | `batch_normalization_4` | BatchNormalization | — |
| 6 | `re_lu_4` | ReLU | — |
| 7 | `max_pooling1d_4` | MaxPooling1D | — |
| 8 | `conv1d_5` | Conv1D | 128 filtros, kernel 3, padding `same` |
| 9 | `batch_normalization_5` | BatchNormalization | — |
| 10 | `re_lu_5` | ReLU | — |
| 11 | `max_pooling1d_5` | MaxPooling1D | — |
| 12 | `global_average_pooling1d_1` | GlobalAveragePooling1D | — |
| 13 | `dense_1` | Dense | 64 neuronas, ReLU |
| 14 | `dropout_1` | Dropout | tasa 0.3 |
| 15 | `puntuacion_sismo` | Dense | 1 neurona, sigmoid |

**Parámetros totales: 44 705.** Este valor coincide con el declarado en
`configuracion_entrenamiento.json` y en `INFORME_FINAL_CNN_V1.md`.

### 4.3 Contrato de entrada

| Aspecto | Valor respaldado por los archivos |
|---|---|
| Forma | `(3000, 3)` por segmento |
| Canales | `Z`, `N`, `E` (orden ZNE) |
| Frecuencia de muestreo | 100 Hz |
| Duración | 30 segundos |
| Tipo de dato | `float32` |
| Etiquetas | `0 = ruido`, `1 = sismo` |
| Salida | 1 valor sigmoide, no calibrado como probabilidad |

### 4.4 Entrenamiento y evaluación declarados

- Dataset total: 1 555 segmentos (827 sismo, 728 ruido).
- División: 1 245 entrenamiento / 155 validación / 155 test.
- Semilla: 2026.
- Optimizador Adam, learning rate inicial 0.001, batch size 32, máximo 100
  épocas.
- Entrenamiento en CPU; 39 épocas ejecutadas, mejor época 29, mejor
  `val_loss` 0.264483.
- Evaluación final en test: accuracy 0.9548, Macro F1 0.9545, ROC-AUC 0.9873;
  148 de 155 clasificaciones correctas.
- El informe advierte sobre el tamaño reducido del dataset, etiquetas con
  distinto nivel de validación y falta de calibración de la probabilidad.
- El conjunto de test se utilizó una sola vez y no debe reutilizarse para
  ajustar el modelo ni el umbral.

---

## 5. Configuración del preprocesamiento y normalización

Según `manifiesto_preprocesamiento.json`, el procedimiento es:

1. Restar la media temporal por segmento y por canal.
2. Estandarizar globalmente por canal usando exclusivamente las estadísticas
   de entrenamiento.
3. Aplicar esas mismas estadísticas a validación, test e inferencia. Nunca
   recalcularlas.

No se aplicó normalización independiente por segmento, SMOTE ni aumento
artificial de datos.

### 5.1 Estadísticas congeladas

Contenido verificado dentro de `estadisticas_normalizacion.npz`:

| Clave | dtype | Forma | Valor |
|---|---|---|---|
| `media_train` | float32 | (3,) | `[0.0006783410790376365, 0.0007371546817012131, 3.24415486829821e-05]` |
| `desviacion_train` | float32 | (3,) | `[14287.1103515625, 15959.3994140625, 13554.525390625]` |
| `canales` | `<U1` | (3,) | `['Z', 'N', 'E']` |
| `frecuencia_hz` | int64 | escalar | `100` |
| `muestras` | int64 | escalar | `3000` |

Los valores del `.npz` coinciden con los del manifiesto JSON.

Las desviaciones estándar son del orden de 13 500 a 16 000, lo que sugiere que
los datos de entrenamiento estaban en unidades crudas (tipo *counts*) y no en
unidades físicas normalizadas. Esto es relevante para la integración: las
señales de entrada deben estar en las mismas unidades y escala que los datos
de entrenamiento.

### 5.2 Cantidades del dataset

| División | Segmentos |
|---|---:|
| Entrenamiento | 1 245 |
| Validación | 155 |
| Test | 155 |

### 5.3 Orden de los pasos

El orden documentado es: primero eliminación de la componente DC por segmento
y canal, después estandarización global con estadísticas de entrenamiento. La
integración debe respetar este orden exacto y no sustituirlo por un
preprocesamiento genérico.

---

## 6. Umbral de clasificación

Contenido de `seleccion_umbral_v1.json`:

| Aspecto | Valor |
|---|---|
| Versión | CNN_V1 |
| Modelo | `mejor_modelo_cnn_v1.keras` |
| SHA-256 del modelo | `cd9e8962d1cdc2977ef15854a416a89c87591d489d870d86f2b64a05e3f2a0d5` |
| Conjunto de selección | Validación |
| Método | Maximizar Macro F1; desempate por cercanía a 0.5 |
| Umbral congelado | `0.2927532196044922` |
| Test utilizado para el umbral | No |

Métricas de validación declaradas:

| Métrica | Valor |
|---|---:|
| Macro F1 | 0.9093718676912796 |
| F1 ruido | 0.9041095890410958 |
| F1 sismo | 0.9146341463414634 |
| Precisión sismo | 0.9259259259259259 |
| Recall sismo | 0.9036144578313253 |
| Balanced accuracy | 0.910140562248996 |

Matriz de confusión en validación:

```
[[66,  6],
 [ 8, 75]]
```

El umbral congelado es `0.2927532196`, no 0.5. Cualquier integración debe
aplicar explícitamente este valor.

---

## 7. Compatibilidad de TensorFlow y Keras con el modelo

### 7.1 Entorno virtual

| Componente | Versión instalada |
|---|---|
| Python | 3.13.0 |
| Django | 6.1.3 |
| TensorFlow | 2.21.0 |
| Keras | 3.15.1 |
| NumPy | 2.5.5 |
| h5py | 3.14.0 |
| protobuf | 7.36.2 |
| ml_dtypes | 0.7.0 |
| absl-py | 2.5.1 |

Ejecutable del entorno:

```
D:\Escuela\Inteligencia Artificial\SismoDetect\.venv\Scripts\python.exe
```

### 7.2 Pruebas de carga realizadas

| Prueba | Resultado |
|---|---|
| `keras.models.load_model(..., compile=False)` | Carga correcta |
| `keras.models.load_model(..., compile=True)` | Carga correcta |

Con `compile=True` se verificó además:

- Optimizador: Adam.
- Learning rate cargado: `0.0002500000118743628`.
- Función de pérdida: `binary_crossentropy`.
- Métricas reconocidas: `loss` y `compile_metrics`.

### 7.3 Prueba de inferencia con datos ficticios

Se ejecutó una predicción con un tensor de ceros de forma `(1, 3000, 3)`:

- Salida obtenida: `[[0.11681133]]`
- dtype: `float32`
- Forma: `(1, 1)`

Esta prueba confirma únicamente que el modelo carga y ejecuta. No se utilizó
ningún dato real ni se evaluó el rendimiento.

### 7.4 Diferencias respecto al entorno de entrenamiento

| Aspecto | Entrenamiento | Entorno local | Impacto observado |
|---|---|---|---|
| TensorFlow | 2.21.0 | 2.21.0 | Sin diferencia |
| NumPy | 2.4.6 | 2.5.5 | Carga e inferencia correctas |
| Keras | 3.13.2 (guardado) | 3.15.1 | Carga correcta |
| Sistema operativo | Linux x86_64 | Windows | Carga correcta |
| Hardware | CPU | CPU | Sin GPU disponible |
| Python | No declarado | 3.13.0 | Sin problema observado |

TensorFlow en Windows nativo no utiliza GPU para versiones iguales o
superiores a 2.11. La inferencia se realizará en CPU, lo cual es suficiente
para un modelo de 44 705 parámetros.

**Compatibilidad verificada:** el archivo `.keras` carga y ejecuta
correctamente con TensorFlow 2.21.0 y Keras 3.15.1 en el entorno local.

**Comprobación no realizada:** no se verificó la paridad numérica exacta
contra el entorno original de entrenamiento, porque no se dispone de los datos
originales ni del código de entrenamiento en este proyecto. Queda pendiente.

---

## 8. Estado de las dependencias

### 8.1 Archivos de requisitos

| Archivo | Contenido |
|---|---|
| `requirements/base.txt` | `Django==6.1.3` |
| `requirements/tensorflow.txt` | `-r base.txt` + `tensorflow==2.21.0` |
| `requirements/dev.txt` | `-r base.txt` + `pytest`, `pytest-django`, `pytest-cov`, `ruff` (sin fijar) |
| `requirements/dev-ia.txt` | `-r tensorflow.txt` + `-r dev.txt` |

### 8.2 Dependencias instaladas en el entorno virtual

Instaladas y verificadas:

- `tensorflow==2.21.0`
- `keras==3.15.1`
- `numpy==2.5.5`
- `h5py==3.14.0`
- `Django==6.1.3`
- `protobuf==7.36.2`
- `ml_dtypes==0.7.0`
- `absl-py==2.5.1`

No instaladas:

- `pytest`
- `pytest-django`
- `pytest-cov`
- `ruff`
- `scikit-learn`

No se instaló ni actualizó ninguna dependencia durante la inspección.

### 8.3 Observaciones sobre las dependencias

- `requirements/tensorflow.txt` fija TensorFlow pero no fija Keras ni NumPy de
  forma explícita. Una reinstalación futura podría resolver versiones
  distintas si TensorFlow cambia sus dependencias.
- `scikit-learn` no está instalado. No es necesario para aplicar el umbral,
  pero sí lo sería para recalcular métricas como Macro F1. No se instalará en
  esta fase.
- Las herramientas de desarrollo (`pytest`, `ruff`, etc.) figuran en
  `requirements/dev.txt` sin versión fijada y no están instaladas.

---

## 9. Componentes que faltan para integrar la CNN con Django

### 9.1 `ia/gestor_modelos/`

Actualmente solo contiene un docstring. Falta:

- Registro y descubrimiento de modelos.
- Definición del modelo activo (`cnn_v1`).
- Carga perezosa y cacheada del modelo y sus metadatos.
- Lectura de `manifiesto_preprocesamiento.json`,
  `configuracion_entrenamiento.json`, `seleccion_umbral_v1.json` e
  `inventario_sha256.json`.
- Verificación de integridad SHA-256 al cargar.
- Manejo de errores por archivos ausentes, hashes incorrectos o versiones
  incompatibles.
- Sincronización de la carga para evitar cargas duplicadas en concurrencia.

### 9.2 `ia/modelos/`

Falta:

- Una interfaz común de modelo (clase base o protocolo) con operaciones tipo
  `cargar()` y `predecir()`.
- El adaptador o wrapper de la CNN V1.
- Exposición de metadatos: forma de entrada, canales, frecuencia, versión y
  umbral.

El archivo `.keras` ya contiene arquitectura y pesos, por lo que puede
cargarse directamente con `keras.models.load_model`. Si se decide reconstruir
la red en código, debe coincidir exactamente con la arquitectura verificada.

### 9.3 `ia/procesamiento/`

Falta:

- Carga de las estadísticas desde el `.npz` o desde el manifiesto, sin
  recalcularlas.
- Función pura para restar la media temporal por segmento y canal.
- Función pura para estandarizar con `media_train` y `desviacion_train`.
- Validación estricta de forma `(3000, 3)`, orden ZNE, dtype `float32` y
  ausencia de valores inválidos.
- Lector de señales de entrada.

**Pendiente de definición:** los archivos no especifican el formato de archivo
de entrada (MiniSEED, SAC, CSV, SDS u otro), las unidades de las señales, ni
cómo se seleccionan los 30 segundos y los tres canales. Esta información no
puede inferirse de los artefactos inspeccionados.

### 9.4 `ia/inferencia/`

Falta:

- Orquestación: señal cruda → preprocesamiento → modelo → puntuación.
- Aplicación del umbral congelado `0.2927532196`, no el 0.5 por defecto de
  Keras.
- Normalización del resultado: clase (`ruido`/`sismo`), puntuación, umbral
  aplicado, versión del modelo y metadatos.
- Manejo de lote y de una sola muestra.
- Mensajes y estados de error claros.
- Advertencia de que la puntuación sigmoide no es una probabilidad calibrada.

### 9.5 Django (`apps/` y `config/`)

Falta:

- Crear al menos una app en `apps/` (por ejemplo `apps.inferencia` o
  `apps.api`). Actualmente `apps/` solo contiene `__init__.py`.
- Registrar la app en `INSTALLED_APPS`.
- Añadir rutas en `config/urls.py`.
- Capa fina de servicios que llame a `ia/` sin importar TensorFlow
  directamente, respetando la decisión arquitectónica documentada.
- Vista o endpoint de subida de señal y vista o endpoint de resultado.
- Formulario o API para recibir archivos.
- Configuración de almacenamiento en `data/entrada/` y limpieza de
  `data/temporal/`.
- Validación de tamaño, extensión y contenido del archivo subido.
- Opcional: modelo de base de datos y migraciones para guardar inferencias y
  trazabilidad.
- Plantillas o serializadores, según se opte por HTML o API.
- Manejo de errores y mensajes para el usuario.
- Configuración de `ALLOWED_HOSTS`, `DEBUG`, secretos y límites de subida para
  un entorno real.

### 9.6 Pruebas (`tests/`)

Falta:

- Prueba de integridad SHA-256 de los artefactos.
- Prueba de carga del modelo.
- Prueba del preprocesamiento con vectores conocidos.
- Prueba de que el umbral aplicado es el congelado y no 0.5.
- Prueba de rechazo de formas, canales o tipos incorrectos.
- Prueba de extremo a extremo con una señal sintética.
- Prueba de que la inferencia no modifica los archivos originales.

---

## 10. Problemas, riesgos y recomendaciones

### 10.1 Riesgos altos

1. **Contrato de entrada no definido.**
   No está especificado el formato de archivo de la señal del usuario, ni sus
   unidades, ni cómo se obtienen los 30 segundos y los tres canales. Sin esta
   definición no se puede implementar un lector correcto sin inventar
   información.

2. **Unidades y escala de la señal.**
   Las desviaciones de entrenamiento son del orden de 14 000. Si la
   integración recibe señales en unidades físicas distintas o ya normalizadas,
   la estandarización con estadísticas de entrenamiento producirá una
   distribución diferente y las predicciones no serán válidas.

3. **Uso incorrecto del umbral.**
   El modelo fue seleccionado con umbral `0.2927532196`, no con 0.5. Un uso
   ingenuo de `predicción > 0.5` cambiaría el comportamiento respecto al
   informe. La integración debe aplicar explícitamente el umbral congelado.

4. **Longitud y frecuencia rígidas.**
   El modelo exige exactamente `(3000, 3)` a 100 Hz. No hay especificación de
   remuestreo, ventaneo ni rechazo para señales de otra duración o frecuencia.
   Cualquier decisión al respecto debe acordarse y documentarse.

### 10.2 Riesgos medios

5. **Dependencia de artefactos no versionados.**
   El `.gitignore` excluye `*.keras` y el proyecto no es un repositorio Git.
   Si los pesos se pierden o se copian mal, no hay respaldo automático. El
   inventario SHA-256 detecta corrupción, pero no sustituye un respaldo.

6. **Deriva de versiones.**
   El modelo se guardó con Keras 3.13.2 y se carga con Keras 3.15.1; NumPy
   pasó de 2.4.6 a 2.5.5. Hoy funciona, pero no se ha verificado paridad
   numérica contra el entorno original. Además, `requirements/tensorflow.txt`
   no fija Keras ni NumPy.

7. **Carga de TensorFlow en el arranque de Django.**
   Importar TensorFlow es lento y consume memoria. Si se carga al iniciar
   Django o en cada petición, afectará el rendimiento. Conviene carga perezosa
   y única, con sincronización.

8. **Concurrencia.**
   La carga del modelo debe protegerse para que dos peticiones simultáneas no
   lo carguen dos veces. La inferencia concurrente debe probarse o
   serializarse.

9. **Probabilidad no calibrada.**
   El propio informe advierte que la salida sigmoide no debe interpretarse
   como probabilidad calibrada. La interfaz no debería presentarla como
   probabilidad de sismo sin matices.

10. **Generalización limitada.**
    El dataset es pequeño (1 555 segmentos), con etiquetas de distinto nivel de
    validación y estaciones no representadas en todas las divisiones. Los
    resultados de test no garantizan el mismo rendimiento en otras estaciones
    o condiciones.

### 10.3 Riesgos bajos

11. `ALLOWED_HOSTS` vacío, `DEBUG = True` y `SECRET_KEY` fija en
    `settings.py`. No afecta a la IA, pero debe corregirse antes de exponer la
    aplicación.

12. `scikit-learn` no está instalado. No es necesario para inferencia si solo
    se aplica el umbral, pero sí para recalcular métricas como Macro F1.

13. La ruta del proyecto contiene espacios
    (`D:\Escuela\Inteligencia Artificial\SismoDetect`). La carga funcionó
    correctamente, pero conviene usar `pathlib` y rutas absolutas construidas
    desde `BASE_DIR`.

14. El inventario no cubre su propio hash. Es esperable, pero significa que su
    integridad no está protegida por sí misma.

### 10.4 Recomendaciones

1. Definir y documentar el contrato de entrada antes de implementar el lector:
   formato, unidades, canales, frecuencia, duración y comportamiento ante
   señales inválidas.
2. Mantener el umbral congelado `0.2927532196` y centralizarlo en un único
   lugar de configuración.
3. Verificar el SHA-256 del modelo al cargarlo y fallar de forma explícita si
   no coincide.
4. Implementar carga perezosa y única del modelo, con sincronización.
5. No recalcular las estadísticas de normalización en ningún punto.
6. Mantener el preprocesamiento como funciones puras y probadas con vectores
   conocidos.
7. Añadir pruebas de integridad, preprocesamiento, umbral y extremo a extremo.
8. Fijar también Keras y NumPy en los requisitos o documentar la combinación
   exacta verificada.
9. Respaldar los artefactos fuera del repositorio, ya que los pesos están
   excluidos por `.gitignore`.
10. No reevaluar el conjunto de test para ajustar el modelo ni el umbral.

---

## Comprobaciones realizadas y pendientes

### Realizadas

- Presencia y legibilidad de los siete archivos.
- Verificación SHA-256 de los seis artefactos incluidos en el inventario.
- Lectura de los tres JSON, del informe final y del manifiesto.
- Lectura del contenido del `.npz`.
- Carga del modelo `.keras` con `compile=False` y `compile=True`.
- Inspección de la arquitectura y del número de parámetros.
- Predicción con un tensor ficticio de ceros.
- Revisión del entorno virtual y de las dependencias instaladas.
- Revisión de la estructura Django y de los paquetes de IA.

### Pendientes

- Verificación de paridad numérica contra el entorno original de entrenamiento.
- Carga y prueba con una señal real de entrada.
- Definición del formato, unidades y procedencia de las señales de usuario.
- Definición del comportamiento ante señales de longitud o frecuencia distintas
  de 3000 muestras a 100 Hz.
- Implementación de la integración con Django.
- Pruebas automatizadas del pipeline de inferencia.
- Reevaluación del modelo: **no se realizó y no debe realizarse** salvo
  autorización expresa, ya que el conjunto de test se reservó para una única
  evaluación final.

---

## 11. Nota posterior (2026-11-27) — fuente canónica de las particiones

Esta nota se añade después de la inspección original y no modifica sus resultados históricos.

- La fuente canónica de la partición final utilizada por la CNN V1 es `colab/splits_alternativo.csv`, dentro del dataset externo.
- Su resumen está en `colab/split_alternativo_resumen.json`: 1245 segmentos de entrenamiento, 155 de validación y 155 de prueba.
- `metadata.csv` del dataset externo contiene 1383 filas y **no cubre** los 1555 identificadores del split final.
- El CSV conserva una columna antigua `split` (1292/123/140) que **no debe confundirse** con `split_alternativo`, la columna vigente usada por la CNN.

El detalle y la verificación de esta fuente están en `documentacion/INFORME_IMPLEMENTACION.md`, sección 14.

---

**Fin del informe de inspección — CNN V1**
