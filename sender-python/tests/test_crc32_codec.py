import pytest

from sender import ascii_codec, crc32_codec


def test_matches_standard_vector():
    data = ascii_codec.encode("123456789")
    frame = crc32_codec.encode(data)
    crc_bits = frame[len(data):]
    assert format(int(crc_bits, 2), "08x") == "cbf43926"
    assert crc32_codec.decode(frame, len(data)).status == "OK"


def test_detects_changed_bit():
    data = ascii_codec.encode("A")
    frame = crc32_codec.encode(data)
    assert len(frame) == 64
    bits = list(frame)
    bits[0] = "1" if bits[0] == "0" else "0"
    with pytest.raises(ValueError):
        crc32_codec.decode("".join(bits), len(data))


def test_removes_padding_after_verification():
    data = ascii_codec.encode("A")
    frame = crc32_codec.encode(data)
    result = crc32_codec.decode(frame, len(data))
    assert result.data_bits == data
