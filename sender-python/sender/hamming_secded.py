from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    data_bits: str
    status: str
    errors_detected: int
    errors_corrected: int


def parity_bits_for(data_length: int) -> int:
    parity_bits = 0
    while data_length + parity_bits + 1 > (1 << parity_bits):
        parity_bits += 1
    return parity_bits


def _is_power_of_two(value: int) -> bool:
    return (value & (value - 1)) == 0


def encode(data_bits: str) -> str:
    parity_bits = parity_bits_for(len(data_bits))
    code_length = len(data_bits) + parity_bits
    code = [""] * code_length

    data_index = 0
    for position in range(1, code_length + 1):
        if _is_power_of_two(position):
            code[position - 1] = "0"
        else:
            code[position - 1] = data_bits[data_index]
            data_index += 1

    parity_position = 1
    while parity_position <= code_length:
        parity = 0
        for position in range(1, code_length + 1):
            if (position & parity_position) != 0 and code[position - 1] == "1":
                parity ^= 1
        code[parity_position - 1] = str(parity)
        parity_position <<= 1

    global_parity = 0
    for bit in code:
        if bit == "1":
            global_parity ^= 1

    return "".join(code) + str(global_parity)


def decode(frame_bits: str, original_bit_length: int) -> Result:
    if original_bit_length < 0 or original_bit_length > len(frame_bits):
        raise ValueError("Longitud original inválida")

    parity_bits = parity_bits_for(original_bit_length)
    code_length = original_bit_length + parity_bits
    expected_length = code_length + 1
    if len(frame_bits) != expected_length:
        raise ValueError("Longitud de Hamming inválida")

    code = list(frame_bits[:code_length])
    syndrome = 0
    parity_position = 1
    while parity_position <= code_length:
        parity = 0
        for position in range(1, code_length + 1):
            if (position & parity_position) != 0 and code[position - 1] == "1":
                parity ^= 1
        if parity == 1:
            syndrome |= parity_position
        parity_position <<= 1

    global_parity = 0
    for character in frame_bits:
        if character == "1":
            global_parity ^= 1

    status = "OK"
    detected = 0
    corrected = 0
    if syndrome != 0 and global_parity == 1:
        if syndrome > code_length:
            raise ValueError("Error Hamming fuera de rango")
        index = syndrome - 1
        code[index] = "1" if code[index] == "0" else "0"
        status = "CORRECTED"
        detected = 1
        corrected = 1
    elif syndrome == 0 and global_parity == 1:
        status = "CORRECTED"
        detected = 1
        corrected = 1
    elif syndrome != 0:
        raise ValueError("Hamming detectó múltiples errores")

    data = []
    for position in range(1, code_length + 1):
        if not _is_power_of_two(position):
            data.append(code[position - 1])

    data_bits = "".join(data)[:original_bit_length]
    return Result(data_bits, status, detected, corrected)
