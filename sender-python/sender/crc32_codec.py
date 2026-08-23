import zlib
from dataclasses import dataclass

_CRC_BITS = 32
_MINIMUM_DATA_BITS = 32


@dataclass(frozen=True)
class Result:
    data_bits: str
    status: str
    errors_detected: int
    errors_corrected: int


def protected_data_length(original_bit_length: int) -> int:
    if original_bit_length < 0 or original_bit_length % 8 != 0:
        raise ValueError("La longitud ASCII debe ser múltiplo de 8")
    return max(original_bit_length, _MINIMUM_DATA_BITS)


def checksum(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def encode(data_bits: str) -> str:
    if len(data_bits) % 8 != 0 or not set(data_bits) <= {"0", "1"}:
        raise ValueError("Los datos CRC deben ser bytes ASCII")
    protected_data_bits = _pad_data(data_bits)
    value = checksum(_bits_to_bytes(protected_data_bits))
    return protected_data_bits + format(value, "032b")


def decode(frame_bits: str, original_bit_length: int) -> Result:
    protected_length = protected_data_length(original_bit_length)
    if len(frame_bits) != protected_length + _CRC_BITS:
        raise ValueError("Longitud de CRC-32 inválida")
    protected_data_bits = frame_bits[:protected_length]
    expected = int(frame_bits[protected_length:], 2)
    actual = checksum(_bits_to_bytes(protected_data_bits))
    if actual != expected:
        raise ValueError("CRC-32 no coincide")
    return Result(protected_data_bits[:original_bit_length], "OK", 0, 0)


def _pad_data(data_bits: str) -> str:
    protected_length = protected_data_length(len(data_bits))
    return data_bits + "0" * (protected_length - len(data_bits))


def _bits_to_bytes(bits: str) -> bytes:
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
