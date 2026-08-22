package gt.edu.uvg.redes.receiver;

public record FrameResponse(String messageId, String status, int errorsDetected, int errorsCorrected,
                            String message, String error) {
    public static FrameResponse success(String id, String status, int detected, int corrected, String message) {
        return new FrameResponse(id, status, detected, corrected, message, null);
    }

    public static FrameResponse failure(String id, String error) {
        return new FrameResponse(id == null ? "unknown" : id, "ERROR_DETECTED", 1, 0, null, error);
    }
}
