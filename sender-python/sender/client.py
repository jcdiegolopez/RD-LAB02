import socket


def send_frame(host: str, port: int, request_json: str, timeout: float = 5.0) -> str:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock_file = sock.makefile("rw", encoding="utf-8", newline="\n")
        sock_file.write(request_json + "\n")
        sock_file.flush()
        response_line = sock_file.readline()
        if not response_line:
            raise ConnectionError("El receptor cerró la conexión sin responder")
        return response_line.strip()
