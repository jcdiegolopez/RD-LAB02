package gt.edu.uvg.redes.receiver;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class AsciiCodecTest {
    @Test
    void encodesAndDecodesAscii() {
        String message = "Redes 2!";
        assertEquals(message, AsciiCodec.decode(AsciiCodec.encode(message)));
    }

    @Test
    void rejectsNonAscii() {
        assertThrows(IllegalArgumentException.class, () -> AsciiCodec.encode("café"));
    }
}
