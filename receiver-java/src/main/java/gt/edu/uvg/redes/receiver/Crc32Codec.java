package gt.edu.uvg.redes.receiver;

public final class Crc32Codec {
    private static final int CRC_BITS = 32;
    private static final int MINIMUM_DATA_BITS = 32;
    private static final long INITIAL_VALUE = 0xFFFFFFFFL;
    private static final long POLYNOMIAL = 0xEDB88320L;

    private Crc32Codec() {
    }

    public record Result(String dataBits, String status, int errorsDetected, int errorsCorrected) {
    }

    public static Result decode(String frameBits, int originalBitLength) {
        if (originalBitLength < 0 || originalBitLength % 8 != 0) {
            throw new IllegalArgumentException("La longitud ASCII debe ser múltiplo de 8");
        }
        int protectedDataLength = protectedDataLength(originalBitLength);
        if (frameBits.length() != protectedDataLength + CRC_BITS) {
            throw new IllegalArgumentException("Longitud de CRC-32 inválida");
        }
        String protectedDataBits = frameBits.substring(0, protectedDataLength);
        long expected = Long.parseUnsignedLong(frameBits.substring(protectedDataLength), 2);
        long actual = checksum(bitsToBytes(protectedDataBits));
        if (actual != expected) {
            throw new IllegalArgumentException("CRC-32 no coincide");
        }
        return new Result(protectedDataBits.substring(0, originalBitLength), "OK", 0, 0);
    }

    public static String encode(String dataBits) {
        if (dataBits.length() % 8 != 0 || !dataBits.matches("[01]*")) {
            throw new IllegalArgumentException("Los datos CRC deben ser bytes ASCII");
        }
        String protectedDataBits = padData(dataBits);
        long value = checksum(bitsToBytes(protectedDataBits));
        return protectedDataBits + String.format("%32s", Long.toBinaryString(value)).replace(' ', '0');
    }

    public static long checksum(byte[] bytes) {
        long crc = INITIAL_VALUE;
        for (byte value : bytes) {
            crc ^= value & 0xFFL;
            for (int bit = 0; bit < 8; bit++) {
                if ((crc & 1L) != 0) {
                    crc = (crc >>> 1) ^ POLYNOMIAL;
                } else {
                    crc >>>= 1;
                }
            }
        }
        return (crc ^ INITIAL_VALUE) & 0xFFFFFFFFL;
    }

    public static int protectedDataLength(int originalBitLength) {
        if (originalBitLength < 0 || originalBitLength % 8 != 0) {
            throw new IllegalArgumentException("La longitud ASCII debe ser múltiplo de 8");
        }
        return Math.max(originalBitLength, MINIMUM_DATA_BITS);
    }

    private static String padData(String dataBits) {
        int protectedLength = protectedDataLength(dataBits.length());
        return dataBits + "0".repeat(protectedLength - dataBits.length());
    }

    private static byte[] bitsToBytes(String bits) {
        byte[] bytes = new byte[bits.length() / 8];
        for (int i = 0; i < bytes.length; i++) {
            bytes[i] = (byte) Integer.parseInt(bits.substring(i * 8, i * 8 + 8), 2);
        }
        return bytes;
    }
}
