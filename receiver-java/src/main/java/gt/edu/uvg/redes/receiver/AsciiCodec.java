package gt.edu.uvg.redes.receiver;

public final class AsciiCodec {
    private AsciiCodec() {
    }

    public static String encode(String text) {
        StringBuilder bits = new StringBuilder(text.length() * 8);
        for (char character : text.toCharArray()) {
            if (character > 127) {
                throw new IllegalArgumentException("El mensaje solo puede contener caracteres ASCII");
            }
            bits.append(String.format("%8s", Integer.toBinaryString(character)).replace(' ', '0'));
        }
        return bits.toString();
    }

    public static String decode(String bits) {
        if (bits.length() % 8 != 0 || !bits.matches("[01]*")) {
            throw new IllegalArgumentException("La cantidad de bits ASCII no es válida");
        }
        StringBuilder text = new StringBuilder(bits.length() / 8);
        for (int i = 0; i < bits.length(); i += 8) {
            int value = Integer.parseInt(bits.substring(i, i + 8), 2);
            if (value > 127) {
                throw new IllegalArgumentException("La trama contiene un carácter fuera de ASCII");
            }
            text.append((char) value);
        }
        return text.toString();
    }
}
