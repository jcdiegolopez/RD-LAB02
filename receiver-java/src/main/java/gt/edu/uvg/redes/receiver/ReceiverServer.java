package gt.edu.uvg.redes.receiver;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public final class ReceiverServer {
    private final ReceiverConfig config;
    private final FrameProcessor processor = new FrameProcessor();

    public ReceiverServer(ReceiverConfig config) {
        this.config = config;
    }

    public void run() {
        AnsiUi.banner(config);
        try (ServerSocket server = new ServerSocket()) {
            server.bind(new InetSocketAddress(config.host(), config.port()));
            while (true) {
                try (Socket socket = server.accept()) {
                    handle(socket);
                } catch (IOException exception) {
                    AnsiUi.failure(exception.getMessage());
                }
                if (config.once()) {
                    return;
                }
            }
        } catch (IOException exception) {
            throw new IllegalStateException("No se pudo abrir el puerto " + config.port() + ": " + exception.getMessage(), exception);
        }
    }

    private void handle(Socket socket) throws IOException {
        AnsiUi.connected(socket.getRemoteSocketAddress().toString());
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
             PrintWriter writer = new PrintWriter(socket.getOutputStream(), true, StandardCharsets.UTF_8)) {
            String line = reader.readLine();
            if (line == null || line.isBlank()) {
                return;
            }
            FrameResponse response;
            FrameRequest request = null;
            try {
                request = JsonProtocol.parseRequest(line);
                AnsiUi.received(request);
                response = processor.process(request);
            } catch (RuntimeException exception) {
                response = FrameResponse.failure(request == null ? null : request.messageId(), exception.getMessage());
            }
            writer.println(JsonProtocol.serialize(response));
            AnsiUi.result(response);
        }
    }
}
