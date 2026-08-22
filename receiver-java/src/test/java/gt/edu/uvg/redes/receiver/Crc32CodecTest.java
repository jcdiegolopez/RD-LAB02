package gt.edu.uvg.redes.receiver;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class Crc32CodecTest {
    @Test
    void matchesStandardVector() {
        String data = AsciiCodec.encode("123456789");
        String frame = Crc32Codec.encode(data);
        assertEquals("cbf43926", Long.toHexString(Long.parseUnsignedLong(frame.substring(data.length()), 2)));
        assertEquals("OK", Crc32Codec.decode(frame, data.length()).status());
    }

    @Test
    void detectsChangedBit() {
        String data = AsciiCodec.encode("A");
        String frame = Crc32Codec.encode(data);
        assertEquals(64, frame.length());
        char[] bits = frame.toCharArray();
        bits[0] = bits[0] == '0' ? '1' : '0';
        assertThrows(IllegalArgumentException.class, () -> Crc32Codec.decode(new String(bits), data.length()));
    }

    @Test
    void removesPaddingAfterVerification() {
        String data = AsciiCodec.encode("A");
        String frame = Crc32Codec.encode(data);
        Crc32Codec.Result result = Crc32Codec.decode(frame, data.length());
        assertEquals(data, result.dataBits());
    }
}
