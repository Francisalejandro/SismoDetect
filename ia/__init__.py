"""Componentes independientes de inteligencia artificial de SismoDetect.

Este paquete está desacoplado de Django: contiene la carga, el
procesamiento y la inferencia de los modelos de clasificación de señales
sísmicas. La integración con Django se hace a través de una capa fina de
servicios, de modo que la IA pueda probarse y evolucionar sin depender
del framework web.
"""
