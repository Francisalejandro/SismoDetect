"""Gestor centralizado de modelos de IA.

Contendrá el registro (registro/descubrimiento) de modelos disponibles,
la selección del modelo activo y la carga perezosa de sus pesos. Está
pensado para incorporar la CNN V1 y, más adelante, arquitecturas como
Transformers sin modificar los modelos ya existentes.
"""
