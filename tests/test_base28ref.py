import pytest

from tools.base28ref import ALPHABET, Overflow, encode_payload, symbol_count


def test_alphabet_exact() -> None:
    assert ALPHABET == "01346789ABCDEFGHJKMNPQRTVWXY"
    assert len(ALPHABET) == 28
    assert len(set(ALPHABET)) == 28
    for banned in "25SZILOU":
        assert banned not in ALPHABET


def test_symbol_count_is_minimal() -> None:
    # k is the smallest integer with 28**k >= 2**n
    for n in range(1, 129):
        k = symbol_count(n)
        assert 28**k >= 2**n
        assert 28 ** (k - 1) < 2**n


def test_symbol_count_rev45() -> None:
    assert symbol_count(45) == 10


def test_encode_zero_pads_to_width() -> None:
    assert encode_payload(0, 45) == "0" * 10


def test_encode_max_45() -> None:
    s = encode_payload(2**45 - 1, 45)
    assert len(s) == 10
    assert all(c in ALPHABET for c in s)


def test_encode_roundtrip_via_int() -> None:
    v = 123456789
    s = encode_payload(v, 45)
    back = 0
    for c in s:
        back = back * 28 + ALPHABET.index(c)
    assert back == v


def test_encode_overflow_raises() -> None:
    with pytest.raises(Overflow):
        _ = encode_payload(2**45, 45)
    with pytest.raises(Overflow):
        _ = encode_payload(-1, 45)


def test_symbol_count_bounds() -> None:
    with pytest.raises(ValueError):
        _ = symbol_count(0)
    with pytest.raises(ValueError):
        _ = symbol_count(129)
