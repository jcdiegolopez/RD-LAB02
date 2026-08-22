package gt.edu.uvg.redes.receiver;

import org.fusesource.jansi.AnsiConsole;

public final class App {
    private App() {
    }

    public static void main(String[] args) {
        ReceiverConfig config = ReceiverConfig.fromArgs(args);
        AnsiConsole.systemInstall();
        try {
            new ReceiverServer(config).run();
        } finally {
            AnsiConsole.systemUninstall();
        }
    }
}
