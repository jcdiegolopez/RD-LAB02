# Emisor Python

## Requisitos

- Python 3.11 o superior

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

(`requirements-dev.txt` incluye `requirements.txt` más `pytest` para las pruebas.)

## Ejecutar pruebas

```bash
pytest
```

## Iniciar el emisor

El receptor Java debe estar escuchando antes de ejecutar el emisor.

```bash
python main.py
```

Por defecto se conecta a `127.0.0.1:5000`. Para cambiar host o puerto:

```bash
python main.py --host 127.0.0.1 --port 5000
```

El programa solicita interactivamente el mensaje (ASCII), el algoritmo
(`HAMMING` o `CRC32`) y la probabilidad de error por bit en formato `1/N`
(por ejemplo `1/100`), la convierte a `1 ÷ N` y aplica el ruido a cada bit
de la trama, incluida la redundancia.

## Convenciones de bits (deben coincidir con el receptor Java)

- Cada carácter ASCII ocupa 8 bits, del bit más significativo al menos
  significativo.
- Hamming SECDED: posiciones numeradas desde 1; los bits de paridad ocupan
  `1, 2, 4, 8...`, los datos ocupan el resto de posiciones y se agrega un
  bit de paridad global al final. `parity_bits_for` calcula `r` dinámico
  tal que `m + r + 1 <= 2^r`.
- CRC-32: el mensaje se rellena con ceros hasta 32 bits cuando es menor.
  El CRC se calcula con una implementación propia bit a bit usando el
  polinomio reflejado `0xEDB88320` y se agregan 32 bits al final. `frameBits`
  mide `max(originalBitLength, 32) + 32` bits.
- El padding se retira en el receptor usando `originalBitLength`.

## Protocolo

Se envía una línea JSON por conexión y se lee una línea JSON de respuesta:

```json
{"messageId": "...", "algorithm": "HAMMING", "originalBitLength": 40, "frameBits": "0101..."}
```

```json
{"messageId": "...", "status": "OK|CORRECTED|ERROR_DETECTED", "errorsDetected": 0, "errorsCorrected": 0, "message": "..."}
```
