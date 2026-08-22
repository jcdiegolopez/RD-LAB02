package gt.edu.uvg.redes.receiver;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class JsonProtocolTest {
    @Test
    void parsesRequestAndSerializesResponse() {
        String requestJson = "{\"messageId\":\"abc\",\"algorithm\":\"CRC32\",\"originalBitLength\":8,\"frameBits\":\"01000001\"}";
        FrameRequest request = JsonProtocol.parseRequest(requestJson);
        assertEquals("abc", request.messageId());
        assertEquals("CRC32", request.algorithm());
        assertEquals(8, request.originalBitLength());
        assertEquals("01000001", request.frameBits());

        String responseJson = JsonProtocol.serialize(FrameResponse.success("abc", "OK", 0, 0, "A"));
        assertEquals(true, responseJson.contains("\"status\":\"OK\""));
        assertEquals(true, responseJson.contains("\"message\":\"A\""));
    }
}
