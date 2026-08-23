import uuid

from sender import ascii_codec, client, config, crc32_codec, hamming_secded, noise, protocol, ui


def _encode_frame(algorithm: str, original_bits: str) -> str:
    if algorithm == "HAMMING":
        return hamming_secded.encode(original_bits)
    if algorithm == "CRC32":
        return crc32_codec.encode(original_bits)
    raise ValueError(f"Algoritmo no soportado: {algorithm}")


def main(argv: list[str] | None = None) -> int:
    sender_config = config.parse_args(argv)
    ui.banner(sender_config.host, sender_config.port)

    message = ui.ask_message()
    algorithm = ui.ask_algorithm()
    probability = ui.ask_noise_probability()

    original_bits = ascii_codec.encode(message)
    frame_bits = _encode_frame(algorithm, original_bits)
    noisy_frame_bits, flipped = noise.apply_noise(frame_bits, probability)

    ui.show_frame_summary(algorithm, original_bits, frame_bits, noisy_frame_bits, flipped)

    request_json = protocol.build_request_json(
        message_id=str(uuid.uuid4()),
        algorithm=algorithm,
        original_bit_length=len(original_bits),
        frame_bits=noisy_frame_bits,
    )

    try:
        response_line = client.send_frame(sender_config.host, sender_config.port, request_json)
    except OSError as exc:
        ui.show_connection_error(str(exc))
        return 1

    response = protocol.parse_response(response_line)
    ui.show_response(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
