# Receptor Java

## Requisitos

- Java 21
- Maven 3.9 o superior

## Ejecutar pruebas

Desde esta carpeta:

```powershell
mvn test
```

## Iniciar el receptor

```powershell
mvn exec:java
```

Por defecto escucha en `127.0.0.1:5000` y acepta conexiones continuamente.

Para cambiar el host o puerto:

```powershell
mvn exec:java "-Dexec.args=--host 127.0.0.1 --port 5000"
```

Para procesar una sola conexión:

```powershell
mvn exec:java "-Dexec.args=--once"
```

El emisor Python debe enviar una línea JSON por conexión y leer una línea JSON de respuesta. La trama debe usar `algorithm` igual a `HAMMING` o `CRC32`, `originalBitLength` con la longitud de los bits ASCII originales y `frameBits` con la trama afectada por ruido.

## Convenciones de bits

- Cada carácter ASCII ocupa 8 bits, del bit más significativo al menos significativo.
- En Hamming, las posiciones se numeran desde 1; los bits de paridad ocupan `1, 2, 4, 8...`, los datos se colocan en las demás posiciones y la paridad global se agrega al final.
- En CRC-32, el mensaje se rellena con ceros hasta alcanzar 32 bits cuando sea menor. El CRC se calcula sobre el mensaje rellenado y se agrega como 32 bits binarios al final.
- Para CRC-32, `frameBits` mide `max(originalBitLength, 32) + 32` bits.
- Python debe usar el CRC-32 estándar compatible con `java.util.zip.CRC32` y transmitir el valor en orden binario de mayor a menor peso.
