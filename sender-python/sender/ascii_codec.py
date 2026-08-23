import re

_BIT_PATTERN = re.compile(r"[01]*")


def encode(text: str) -> str:
    bits = []
    for character in text:
        code_point = ord(character)
        if code_point > 127:
            raise ValueError("El mensaje solo puede contener caracteres ASCII")
        bits.append(format(code_point, "08b"))
    return "".join(bits)


def decode(bits: str) -> str:
    if len(bits) % 8 != 0 or not _BIT_PATTERN.fullmatch(bits):
        raise ValueError("La cantidad de bits ASCII no es válida")
    characters = []
    for i in range(0, len(bits), 8):
        value = int(bits[i:i + 8], 2)
        if value > 127:
            raise ValueError("La trama contiene un carácter fuera de ASCII")
        characters.append(chr(value))
    return "".join(characters)
