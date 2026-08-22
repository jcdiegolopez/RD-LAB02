package gt.edu.uvg.redes.receiver;

public final class FrameProcessor {
    public FrameResponse process(FrameRequest request) {
        try {
            return switch (request.algorithm()) {
                case "HAMMING" -> processHamming(request);
                case "CRC32", "CRC-32" -> processCrc(request);
                default -> FrameResponse.failure(request.messageId(), "Algoritmo no soportado: " + request.algorithm());
            };
        } catch (RuntimeException exception) {
            return FrameResponse.failure(request.messageId(), exception.getMessage());
        }
    }

    private FrameResponse processHamming(FrameRequest request) {
        HammingSecded.Result result = HammingSecded.decode(request.frameBits(), request.originalBitLength());
        String message = AsciiCodec.decode(result.dataBits());
        return FrameResponse.success(request.messageId(), result.status(), result.errorsDetected(), result.errorsCorrected(), message);
    }

    private FrameResponse processCrc(FrameRequest request) {
        Crc32Codec.Result result = Crc32Codec.decode(request.frameBits(), request.originalBitLength());
        String message = AsciiCodec.decode(result.dataBits());
        return FrameResponse.success(request.messageId(), result.status(), result.errorsDetected(), result.errorsCorrected(), message);
    }
}
