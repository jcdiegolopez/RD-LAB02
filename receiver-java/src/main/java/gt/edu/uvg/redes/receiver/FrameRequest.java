package gt.edu.uvg.redes.receiver;

public record FrameRequest(String messageId, String algorithm, int originalBitLength, String frameBits) {
    public FrameRequest {
        if (messageId == null || messageId.isBlank()) {
            throw new IllegalArgumentException("messageId inválido");
        }
        if (algorithm == null || algorithm.isBlank()) {
            throw new IllegalArgumentException("algorithm inválido");
        }
        if (originalBitLength < 0) {
            throw new IllegalArgumentException("originalBitLength inválido");
        }
        if (frameBits == null || !frameBits.matches("[01]*")) {
            throw new IllegalArgumentException("frameBits debe contener únicamente bits");
        }
    }
}
