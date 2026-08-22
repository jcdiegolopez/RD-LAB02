package gt.edu.uvg.redes.receiver;

import org.fusesource.jansi.Ansi;

public final class AnsiUi {
    private AnsiUi() {
    }

    public static void banner(ReceiverConfig config) {
        System.out.println(Ansi.ansi().fg(Ansi.Color.CYAN).bold().a("Receptor de Redes").reset());
        System.out.println(Ansi.ansi().fg(Ansi.Color.WHITE).a("Escuchando en ").fg(Ansi.Color.GREEN)
                .a(config.host()).a(":").a(config.port()).reset());
    }

    public static void connected(String remote) {
        System.out.println(Ansi.ansi().fg(Ansi.Color.BLUE).a("Conexión recibida: ").fg(Ansi.Color.WHITE).a(remote).reset());
    }

    public static void received(FrameRequest request) {
        System.out.println(Ansi.ansi().fg(Ansi.Color.YELLOW).a("Trama recibida: ")
                .fg(Ansi.Color.WHITE).a(request.algorithm()).a(" | ")
                .a(request.frameBits().length()).a(" bits").reset());
    }

    public static void result(FrameResponse response) {
        Ansi.Color color = switch (response.status()) {
            case "OK" -> Ansi.Color.GREEN;
            case "CORRECTED" -> Ansi.Color.YELLOW;
            default -> Ansi.Color.RED;
        };
        System.out.println(Ansi.ansi().fg(color).a(response.status()).reset()
                .a(" | detectados: ").a(response.errorsDetected())
                .a(" | corregidos: ").a(response.errorsCorrected()));
        if (response.message() != null) {
            System.out.println(Ansi.ansi().fg(Ansi.Color.WHITE).a("Mensaje: ").a(response.message()).reset());
        }
        if (response.error() != null) {
            System.out.println(Ansi.ansi().fg(Ansi.Color.RED).a("Detalle: ").a(response.error()).reset());
        }
    }

    public static void failure(String message) {
        System.out.println(Ansi.ansi().fg(Ansi.Color.RED).a("Error: ").a(message).reset());
    }
}
