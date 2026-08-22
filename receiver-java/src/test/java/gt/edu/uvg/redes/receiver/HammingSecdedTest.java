package gt.edu.uvg.redes.receiver;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class HammingSecdedTest {
    @Test
    void recoversMessageWithoutNoise() {
        String data = AsciiCodec.encode("AB");
        HammingSecded.Result result = HammingSecded.decode(HammingSecded.encode(data), data.length());
        assertEquals("OK", result.status());
        assertEquals("AB", AsciiCodec.decode(result.dataBits()));
    }

    @Test
    void correctsOneChangedBit() {
        String data = AsciiCodec.encode("A");
        String frame = HammingSecded.encode(data);
        int changedIndex = 5;
        String damaged = flip(frame, changedIndex);
        HammingSecded.Result result = HammingSecded.decode(damaged, data.length());
        assertEquals("CORRECTED", result.status());
        assertEquals("A", AsciiCodec.decode(result.dataBits()));
    }

    @Test
    void detectsTwoChangedBits() {
        String data = AsciiCodec.encode("A");
        String frame = HammingSecded.encode(data);
        String damaged = flip(flip(frame, 2), 5);
        assertThrows(IllegalArgumentException.class, () -> HammingSecded.decode(damaged, data.length()));
    }

    private static String flip(String value, int index) {
        char[] bits = value.toCharArray();
        bits[index] = bits[index] == '0' ? '1' : '0';
        return new String(bits);
    }
}
