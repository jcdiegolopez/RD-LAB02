import random

import pytest

from sender import noise


def test_parse_fraction_format():
    assert noise.parse_noise_probability("1/100") == pytest.approx(0.01)
    assert noise.parse_noise_probability(" 1 / 4 ") == pytest.approx(0.25)


def test_parse_decimal_format():
    assert noise.parse_noise_probability("0.5") == pytest.approx(0.5)


def test_parse_rejects_invalid_values():
    with pytest.raises(ValueError):
        noise.parse_noise_probability("1/0")
    with pytest.raises(ValueError):
        noise.parse_noise_probability("abc")
    with pytest.raises(ValueError):
        noise.parse_noise_probability("2")


def test_apply_noise_zero_probability_leaves_frame_untouched():
    frame = "0101010101"
    result, flipped = noise.apply_noise(frame, 0.0, rng=random.Random(42))
    assert result == frame
    assert flipped == 0


def test_apply_noise_full_probability_flips_every_bit():
    frame = "0101010101"
    result, flipped = noise.apply_noise(frame, 1.0, rng=random.Random(42))
    assert flipped == len(frame)
    assert result == "1010101010"
