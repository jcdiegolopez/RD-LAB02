import random
import re

_FRACTION_PATTERN = re.compile(r"1\s*/\s*(\d+)")


def parse_noise_probability(text: str) -> float:
    text = text.strip()
    match = _FRACTION_PATTERN.fullmatch(text)
    if match:
        n = int(match.group(1))
        if n <= 0:
            raise ValueError("N debe ser mayor que cero en 1/N")
        return 1.0 / n

    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError("Formato inválido, use 1/N o un decimal entre 0 y 1") from exc
    if not (0.0 <= value <= 1.0):
        raise ValueError("La probabilidad debe estar entre 0 y 1")
    return value


def apply_noise(frame_bits: str, probability: float, rng: random.Random | None = None) -> tuple[str, int]:
    if not (0.0 <= probability <= 1.0):
        raise ValueError("La probabilidad debe estar entre 0 y 1")
    rng = rng or random.Random()
    bits = list(frame_bits)
    flipped = 0
    for i, bit in enumerate(bits):
        if rng.random() < probability:
            bits[i] = "1" if bit == "0" else "0"
            flipped += 1
    return "".join(bits), flipped
