import pytest

from sender import ascii_codec, hamming_secded


def _flip(value: str, index: int) -> str:
    bits = list(value)
    bits[index] = "1" if bits[index] == "0" else "0"
    return "".join(bits)


def test_recovers_message_without_noise():
    data = ascii_codec.encode("AB")
    frame = hamming_secded.encode(data)
    result = hamming_secded.decode(frame, len(data))
    assert result.status == "OK"
    assert ascii_codec.decode(result.data_bits) == "AB"


def test_corrects_one_changed_bit():
    data = ascii_codec.encode("A")
    frame = hamming_secded.encode(data)
    damaged = _flip(frame, 5)
    result = hamming_secded.decode(damaged, len(data))
    assert result.status == "CORRECTED"
    assert result.errors_corrected == 1
    assert ascii_codec.decode(result.data_bits) == "A"


def test_corrects_global_parity_bit_flip():
    data = ascii_codec.encode("A")
    frame = hamming_secded.encode(data)
    damaged = _flip(frame, len(frame) - 1)
    result = hamming_secded.decode(damaged, len(data))
    assert result.status == "CORRECTED"
    assert ascii_codec.decode(result.data_bits) == "A"


def test_detects_two_changed_bits():
    data = ascii_codec.encode("A")
    frame = hamming_secded.encode(data)
    damaged = _flip(_flip(frame, 2), 5)
    with pytest.raises(ValueError):
        hamming_secded.decode(damaged, len(data))


def test_parity_bits_for_matches_hamming_rule():
    # m + r + 1 <= 2^r
    assert hamming_secded.parity_bits_for(4) == 3
    assert hamming_secded.parity_bits_for(8) == 4
    assert hamming_secded.parity_bits_for(11) == 4
