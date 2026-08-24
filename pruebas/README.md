# Pruebas de envío/recepción

Harness automatizado para el requisito de "Pruebas" del laboratorio: envía
tramas reales contra el receptor Java (Hamming SECDED y CRC-32) variando
tamaño del mensaje, probabilidad de error y algoritmo, y genera las
gráficas de respaldo para el reporte.

Reutiliza directamente los módulos del emisor Python (`ascii_codec`,
`hamming_secded`, `crc32_codec`, `noise`, `protocol`, `client`) en vez de
reimplementar los algoritmos; solo evita la UI interactiva para poder
correr miles de pruebas sin intervención manual.

## Requisitos

- Java 21 + Maven (para levantar el receptor real)
- Python 3.11+
- `pip install -r requirements.txt` (matplotlib)

## Uso

```bash
python3 run_experiments.py     # ejecuta las pruebas y escribe resultados/raw_results.csv
python3 generar_graficas.py    # lee el CSV y genera resultados/graficas/*.png
```

`run_experiments.py` levanta su propia instancia del receptor Java en el
puerto 5099 (para no chocar con una instancia manual en 5000), corre todas
las pruebas y la cierra al terminar.

## Diseño de las pruebas

Semilla fija (`SEED = 20260823`) para reproducibilidad.

- **Experimento A (overhead)**: tamaños 1–128 caracteres, sin ruido, 1
  corrida por combinación algoritmo×tamaño. Mide el overhead determinístico
  de cada algoritmo.
- **Experimento B (vs. probabilidad)**: mensaje fijo de 32 caracteres,
  probabilidad de error de 0 a 0.2, 200 pruebas por punto y algoritmo.
- **Experimento C (vs. tamaño)**: probabilidad fija de 0.01, tamaños
  1–128 caracteres, 150 pruebas por punto y algoritmo.

Total: 6416 pruebas.

## Columnas del CSV

`experiment, algorithm, size_chars, size_bits, probability, flipped_bits,
frame_bits_len, overhead_bits, overhead_pct, status, errors_detected,
errors_corrected, message_correct, silent_corruption, malformed_json`

- `message_correct`: el mensaje decodificado coincide exactamente con el original.
- `silent_corruption`: el receptor reportó `OK`/`CORRECTED` pero el mensaje
  decodificado es incorrecto (falla silenciosa — la más grave).
- `malformed_json`: la respuesta del receptor no era JSON válido (ver
  limitación conocida abajo). Se recupera vía un parser tolerante para no
  perder la prueba.

## Limitaciones conocidas encontradas durante las pruebas

1. **Tamaño máximo de trama (~2000 bits)**: el parser JSON del receptor
   (`JsonProtocol.FIELD`, una regex con backtracking) lanza
   `StackOverflowError` con tramas muy largas y tumba el proceso completo,
   porque `ReceiverServer.handle` solo captura `RuntimeException`, no
   `Error`. Por eso el barrido de tamaños se limita a 128 caracteres.
2. **Respuestas JSON mal formadas por ruido (~1–4% de las pruebas con
   probabilidad de error moderada)**: `JsonProtocol.escape` en el receptor
   solo escapa `\n`, `\r` y `\t`. Si el ruido corrompe un byte de datos y el
   carácter ASCII decodificado es otro carácter de control, el JSON de
   respuesta queda inválido. El emisor Python real (`sender/protocol.py`,
   `parse_response`) usa `json.loads` sin manejar
   `json.JSONDecodeError`, así que **el emisor real puede crashear** al
   recibir una de estas respuestas. El harness usa un parser tolerante para
   seguir midiendo, pero esto vale la pena mencionarlo (o corregirlo) antes
   de la entrega/demo.
