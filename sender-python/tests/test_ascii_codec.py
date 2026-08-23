import pytest

from sender import ascii_codec


def test_round_trip():
    text = "Hola Redes"
    bits = ascii_codec.encode(text)
    assert len(bits) == len(text) * 8
    assert ascii_codec.decode(bits) == text


def test_encode_rejects_non_ascii():
    with pytest.raises(ValueError):
        ascii_codec.encode("ñ")


def test_decode_rejects_invalid_length():
    with pytest.raises(ValueError):
        ascii_codec.decode("0101")


def test_decode_rejects_non_binary_characters():
    with pytest.raises(ValueError):
        ascii_codec.decode("0000000A")
