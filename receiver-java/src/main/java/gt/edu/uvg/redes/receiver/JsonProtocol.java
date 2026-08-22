package gt.edu.uvg.redes.receiver;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class JsonProtocol {
    private static final Pattern FIELD = Pattern.compile("\\\"([A-Za-z][A-Za-z0-9]*)\\\"\\s*:\\s*(?:\\\"((?:\\\\.|[^\\\"\\\\])*)\\\"|(-?\\d+)|null)");

    private JsonProtocol() {
    }

    public static FrameRequest parseRequest(String json) {
        Map<String, String> fields = parseFields(json);
        return new FrameRequest(
                required(fields, "messageId"),
                required(fields, "algorithm").toUpperCase(),
                Integer.parseInt(required(fields, "originalBitLength")),
                required(fields, "frameBits"));
    }

    public static String serialize(FrameResponse response) {
        StringBuilder json = new StringBuilder();
        json.append("{\"messageId\":\"").append(escape(response.messageId())).append("\"");
        json.append(",\"status\":\"").append(escape(response.status())).append("\"");
        json.append(",\"errorsDetected\":").append(response.errorsDetected());
        json.append(",\"errorsCorrected\":").append(response.errorsCorrected());
        json.append(",\"message\":");
        if (response.message() == null) {
            json.append("null");
        } else {
            json.append("\"").append(escape(response.message())).append("\"");
        }
        if (response.error() != null) {
            json.append(",\"error\":\"").append(escape(response.error())).append("\"");
        }
        return json.append('}').toString();
    }

    private static Map<String, String> parseFields(String json) {
        Map<String, String> fields = new HashMap<>();
        Matcher matcher = FIELD.matcher(json);
        while (matcher.find()) {
            String value = matcher.group(2) != null ? unescape(matcher.group(2)) : matcher.group(3);
            fields.put(matcher.group(1), value);
        }
        if (fields.isEmpty() || !json.trim().startsWith("{") || !json.trim().endsWith("}")) {
            throw new IllegalArgumentException("JSON inválido");
        }
        return fields;
    }

    private static String required(Map<String, String> fields, String name) {
        String value = fields.get(name);
        if (value == null) {
            throw new IllegalArgumentException("Falta el campo " + name);
        }
        return value;
    }

    private static String escape(String value) {
        return value.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    private static String unescape(String value) {
        StringBuilder result = new StringBuilder();
        boolean escaped = false;
        for (int i = 0; i < value.length(); i++) {
            char character = value.charAt(i);
            if (!escaped && character == '\\') {
                escaped = true;
                continue;
            }
            if (!escaped) {
                result.append(character);
                continue;
            }
            switch (character) {
                case 'n' -> result.append('\n');
                case 'r' -> result.append('\r');
                case 't' -> result.append('\t');
                case 'b' -> result.append('\b');
                case 'f' -> result.append('\f');
                case '"', '\\', '/' -> result.append(character);
                case 'u' -> {
                    if (i + 4 >= value.length()) {
                        throw new IllegalArgumentException("Escape Unicode inválido");
                    }
                    result.append((char) Integer.parseInt(value.substring(i + 1, i + 5), 16));
                    i += 4;
                }
                default -> throw new IllegalArgumentException("Escape JSON inválido");
            }
            escaped = false;
        }
        if (escaped) {
            throw new IllegalArgumentException("Escape JSON incompleto");
        }
        return result.toString();
    }
}
