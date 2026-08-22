package gt.edu.uvg.redes.receiver;

public final class HammingSecded {
    private HammingSecded() {
    }

    public record Result(String dataBits, String status, int errorsDetected, int errorsCorrected) {
    }

    public static Result decode(String frameBits, int originalBitLength) {
        if (originalBitLength < 0 || originalBitLength > frameBits.length()) {
            throw new IllegalArgumentException("Longitud original inválida");
        }
        int parityBits = parityBitsFor(originalBitLength);
        int codeLength = originalBitLength + parityBits;
        int expectedLength = codeLength + 1;
        if (frameBits.length() != expectedLength) {
            throw new IllegalArgumentException("Longitud de Hamming inválida");
        }

        char[] code = frameBits.substring(0, codeLength).toCharArray();
        int syndrome = 0;
        for (int parityPosition = 1; parityPosition <= codeLength; parityPosition <<= 1) {
            int parity = 0;
            for (int position = 1; position <= codeLength; position++) {
                if ((position & parityPosition) != 0 && code[position - 1] == '1') {
                    parity ^= 1;
                }
            }
            if (parity == 1) {
                syndrome |= parityPosition;
            }
        }

        int globalParity = 0;
        for (int i = 0; i < frameBits.length(); i++) {
            if (frameBits.charAt(i) == '1') {
                globalParity ^= 1;
            }
        }

        String status = "OK";
        int detected = 0;
        int corrected = 0;
        if (syndrome != 0 && globalParity == 1) {
            if (syndrome > codeLength) {
                throw new IllegalArgumentException("Error Hamming fuera de rango");
            }
            code[syndrome - 1] = flip(code[syndrome - 1]);
            status = "CORRECTED";
            detected = 1;
            corrected = 1;
        } else if (syndrome == 0 && globalParity == 1) {
            status = "CORRECTED";
            detected = 1;
            corrected = 1;
        } else if (syndrome != 0) {
            throw new IllegalArgumentException("Hamming detectó múltiples errores");
        }

        StringBuilder data = new StringBuilder(originalBitLength);
        for (int position = 1; position <= codeLength; position++) {
            if (!isPowerOfTwo(position)) {
                data.append(code[position - 1]);
            }
        }
        return new Result(data.substring(0, originalBitLength), status, detected, corrected);
    }

    public static String encode(String dataBits) {
        int parityBits = parityBitsFor(dataBits.length());
        int codeLength = dataBits.length() + parityBits;
        char[] code = new char[codeLength];
        int dataIndex = 0;
        for (int position = 1; position <= codeLength; position++) {
            if (isPowerOfTwo(position)) {
                code[position - 1] = '0';
            } else {
                code[position - 1] = dataBits.charAt(dataIndex++);
            }
        }
        for (int parityPosition = 1; parityPosition <= codeLength; parityPosition <<= 1) {
            int parity = 0;
            for (int position = 1; position <= codeLength; position++) {
                if ((position & parityPosition) != 0 && code[position - 1] == '1') {
                    parity ^= 1;
                }
            }
            code[parityPosition - 1] = (char) ('0' + parity);
        }
        int global = 0;
        for (char bit : code) {
            if (bit == '1') {
                global ^= 1;
            }
        }
        return new String(code) + global;
    }

    public static int parityBitsFor(int dataLength) {
        int parityBits = 0;
        while (dataLength + parityBits + 1 > (1 << parityBits)) {
            parityBits++;
        }
        return parityBits;
    }

    private static boolean isPowerOfTwo(int value) {
        return (value & (value - 1)) == 0;
    }

    private static char flip(char bit) {
        return bit == '0' ? '1' : '0';
    }
}
