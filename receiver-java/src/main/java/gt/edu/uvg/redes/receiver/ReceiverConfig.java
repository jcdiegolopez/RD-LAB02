package gt.edu.uvg.redes.receiver;

public record ReceiverConfig(String host, int port, boolean once) {
    public ReceiverConfig {
        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("El puerto debe estar entre 1 y 65535");
        }
    }

    public static ReceiverConfig fromArgs(String[] args) {
        String host = "127.0.0.1";
        int port = 5000;
        boolean once = false;

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--host" -> host = value(args, ++i, "--host");
                case "--port" -> port = Integer.parseInt(value(args, ++i, "--port"));
                case "--once" -> once = true;
                case "--help", "-h" -> {
                    printHelp();
                    System.exit(0);
                }
                default -> throw new IllegalArgumentException("Argumento desconocido: " + args[i]);
            }
        }
        return new ReceiverConfig(host, port, once);
    }

    private static String value(String[] args, int index, String option) {
        if (index >= args.length) {
            throw new IllegalArgumentException("Falta el valor de " + option);
        }
        return args[index];
    }

    private static void printHelp() {
        System.out.println("Uso: mvn exec:java [-Dexec.args=\"--host 127.0.0.1 --port 5000 --once\"]");
    }
}
