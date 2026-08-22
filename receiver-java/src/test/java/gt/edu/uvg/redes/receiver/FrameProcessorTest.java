package gt.edu.uvg.redes.receiver;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class FrameProcessorTest {
    @Test
    void returnsDetailedErrorForInvalidCrc() {
        String data = AsciiCodec.encode("A");
        String frame = Crc32Codec.encode(data);
        char[] damaged = frame.toCharArray();
        damaged[0] = damaged[0] == '0' ? '1' : '0';
        FrameRequest request = new FrameRequest("id", "CRC32", data.length(), new String(damaged));
        FrameResponse response = new FrameProcessor().process(request);
        assertEquals("ERROR_DETECTED", response.status());
        assertEquals(null, response.message());
    }
}
