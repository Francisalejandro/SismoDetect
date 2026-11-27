
# INFORME FINAL — CNN V1
## Clasificación de señales sísmicas y ruido

**Proyecto:** Sistema de análisis de señales sísmicas en Cuba  
**Versión:** CNN V1  
**Fecha de cierre:** 2026-11-16  
**Estado:** Entrenamiento y evaluación final completados

---

## 1. Objetivo

Desarrollar una red neuronal convolucional 1D capaz de
clasificar segmentos de señales sísmicas en dos categorías:

- Ruido (0).
- Sismo (1).

El sistema realiza clasificación de señales registradas.
No predice terremotos ni determina cuándo ocurrirá un evento.

## 2. Dataset

Dataset principal: 1555 segmentos.

| Clase | Cantidad |
|---|---:|
| Sismo | 827 |
| Ruido | 728 |
| Total | 1555 |

Se utilizó una división alternativa por unidades de agrupación,
con separación entre entrenamiento, validación y prueba.

| División | Segmentos |
|---|---:|
| Entrenamiento | 1245 |
| Validación | 155 |
| Test | 155 |

Distribución de TEST:

- Ruido: 72.
- Sismo: 83.

Se mantuvo separado el dataset auxiliar extranjero de 520
segmentos, que no se incorporó al entrenamiento principal.

### Limitaciones del dataset

Las etiquetas tienen diferentes niveles de validación.
Hay señales sísmicas verificadas y candidatas, así como ruido
validado técnicamente y candidato.

La validación técnica o automática no equivale a una revisión
experta sismológica completa.

También existen estaciones y combinaciones de clase que no
están representadas en todas las divisiones.

## 3. Preprocesamiento

Cada segmento tiene:

- 3000 muestras.
- Tres componentes: Z, N y E.
- Frecuencia de muestreo: 100 Hz.
- Duración: 30 segundos.
- Tipo de dato: float32.

Procedimiento:

1. Eliminación de componente DC mediante la resta de la media
   temporal de cada segmento y canal.
2. Cálculo de media y desviación estándar global por canal
   utilizando exclusivamente entrenamiento.
3. Normalización de entrenamiento, validación y test mediante
   las estadísticas obtenidas en entrenamiento.

No se aplicó normalización independiente por segmento,
SMOTE ni aumento artificial de datos.

## 4. Arquitectura CNN V1

Entrada: (3000, 3).

Arquitectura:

- Conv1D: 32 filtros, kernel 7.
- Batch Normalization y ReLU.
- MaxPooling1D.
- Conv1D: 64 filtros, kernel 5.
- Batch Normalization y ReLU.
- MaxPooling1D.
- Conv1D: 128 filtros, kernel 3.
- Batch Normalization y ReLU.
- MaxPooling1D.
- Global Average Pooling.
- Dense: 64 neuronas, ReLU.
- Dropout: 0.3.
- Dense: 1 neurona, sigmoid.

**Parámetros entrenables y no entrenables:**
44 705.

## 5. Entrenamiento

Configuración:

- Optimizador: Adam.
- Learning rate inicial: 0.001.
- Función de pérdida: binary crossentropy.
- Batch size: 32.
- Máximo: 100 épocas.
- EarlyStopping: paciencia 10.
- ReduceLROnPlateau: factor 0.5, paciencia 5.
- ModelCheckpoint: mejor val_loss.
- Semilla: 2026.
- Entrenamiento realizado en CPU.

Épocas ejecutadas: 39.

Mejor época: 29.

Mejor val_loss: 0.264483.

La selección del checkpoint se realizó utilizando únicamente
validación.

Se observó deterioro de la pérdida de validación después
de la mejor época, compatible con sobreajuste.

## 6. Selección del umbral

El umbral se seleccionó utilizando exclusivamente validación.

Criterio: maximizar Macro F1. En caso de empate, elegir el
valor más cercano a 0.5.

**Umbral congelado:**
0.2927532196

Resultados de validación:

- Macro F1: 0.9094.
- F1 ruido: 0.9041.
- F1 sismo: 0.9146.
- Precisión sismo: 0.9259.
- Recall sismo: 0.9036.
- Balanced accuracy: 0.9101.

El umbral no se modificó después de evaluar TEST.

## 7. Evaluación final con TEST

La evaluación se realizó una sola vez utilizando el checkpoint
seleccionado y el umbral congelado.

### Matriz de confusión

| Real / Predicción | Ruido | Sismo |
|---|---:|---:|
| Ruido | 67 | 5 |
| Sismo | 2 | 81 |

### Métricas

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.9548 |
| Precisión sismo | 0.9419 |
| Recall sismo | 0.9759 |
| Especificidad ruido | 0.9306 |
| F1 sismo | 0.9586 |
| F1 ruido | 0.9504 |
| Macro F1 | 0.9545 |
| Balanced accuracy | 0.9532 |
| ROC-AUC | 0.9873 |
| PR-AUC | 0.9920 |

Total de segmentos de prueba: 155.

Clasificaciones correctas: 148.

Clasificaciones incorrectas: 7.

## 8. Análisis de errores

Se identificaron:

- 5 falsos positivos: ruido clasificado como sismo.
- 2 falsos negativos: sismo clasificado como ruido.

Los falsos positivos corresponden a estaciones MARV y CAMR.
Los dos falsos negativos corresponden a MARV y tienen estado
de validación candidata.

Dos falsos positivos de MARV presentan puntuaciones muy
cercanas al umbral. Los demás errores se encuentran más
alejados de él.

Se calcularon características descriptivas de las señales
normalizadas: media, desviación estándar, amplitud máxima
absoluta y RMS para Z, N y E.

Los archivos originales de los siete segmentos no estaban
disponibles en la carpeta de trabajo, por lo que no se realizó
una inspección física de sus formas de onda originales.

No se modificó el modelo ni el umbral a partir del análisis
de errores.

## 9. Limitaciones

1. El conjunto de datos es relativamente pequeño.
2. No existe revisión experta completa de todas las etiquetas.
3. Algunas estaciones y clases no están representadas en
   todas las divisiones.
4. La evaluación corresponde al conjunto de prueba disponible
   y no garantiza el mismo rendimiento en otras estaciones,
   regiones o condiciones.
5. La puntuación sigmoid no debe interpretarse como una
   probabilidad calibrada.
6. El sistema no es un mecanismo de alerta temprana ni un
   predictor de terremotos.

## 10. Identificación del modelo

Archivo: mejor_modelo_cnn_v1.keras

SHA256:

`cd9e8962d1cdc2977ef15854a416a89c87591d489d870d86f2b64a05e3f2a0d5`

Umbral:

`0.2927532196`

Preprocesamiento: V1.

Entrada esperada: (3000, 3).

Orden de componentes: ZNE.

Frecuencia: 100 Hz.

Duración: 30 segundos.

## 11. Estado final

La fase de entrenamiento y evaluación de CNN V1 está cerrada.

No se deben modificar el checkpoint, las estadísticas de
normalización ni el umbral congelado.

La siguiente fase consiste en preparar la inferencia local
y su integración con Django, respetando exactamente el
preprocesamiento y los parámetros registrados.

---

**Fin del informe — CNN V1**
