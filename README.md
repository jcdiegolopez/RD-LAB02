# RD-LAB02 — Detección y corrección de errores

Laboratorio 2 de Redes (CC3067, UVG). Simula el envío de un mensaje por un
canal con ruido, siguiendo la arquitectura de capas pedida: aplicación,
presentación, enlace, ruido y transmisión.

El emisor está en Python y el receptor en Java (van en lenguajes distintos
porque así lo pide el enunciado), comunicados por sockets TCP con una línea
de JSON por mensaje. Los algoritmos de integridad son Hamming SECDED
(corrección) y CRC-32 (detección), implementados en ambos lados.

## Estructura

- `sender-python/` — emisor (Python + Rich)
- `receiver-java/` — receptor (Java + Maven)
- `pruebas/` — script para correr las pruebas de envío/recepción y generar
  las gráficas del reporte

Cada carpeta tiene su propio README con el detalle de instalación y del
protocolo entre emisor y receptor.

## Cómo correrlo

Levantar primero el receptor:

```bash
cd receiver-java
mvn exec:java
```

Y en otra terminal, el emisor:

```bash
cd sender-python
python3 main.py
```

Por defecto ambos usan `127.0.0.1:5000`. El emisor va a pedir el mensaje,
el algoritmo (`HAMMING` o `CRC32`) y la probabilidad de error por bit
(formato `1/N`, por ejemplo `1/100`).

## Pruebas

`pruebas/run_experiments.py` manda miles de mensajes contra el receptor
variando tamaño, probabilidad de error y algoritmo, y
`pruebas/generar_graficas.py` genera las gráficas que van en la sección de
Resultados del reporte. Detalle en `pruebas/README.md`.
