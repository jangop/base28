import pytest

from tools.base28ref import (
    ALPHABET,
    CheckMismatch,
    ExcludedConfusable,
    InvalidCharacter,
    Overflow,
    WrongLength,
    check_symbol,
    decode,
    encode,
    encode_payload,
    format_rev45,
    symbol_count,
)


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


def test_encode_appends_valid_check() -> None:
    s = encode(0, 45)
    assert len(s) == 11
    assert s[:10] == "0" * 10
    assert decode(s, 45) == 0


def test_roundtrip_many() -> None:
    for v in [0, 1, 27, 28, 2**44, 2**45 - 1, 0x1234_5678_ABC]:
        assert decode(encode(v, 45), 45) == v


def test_decode_normalizes_case_hyphens_whitespace() -> None:
    s = encode(2**45 - 1, 45)
    grouped = format_rev45(s)
    assert decode(grouped.lower(), 45) == 2**45 - 1
    assert decode(" " + s + " ", 45) == 2**45 - 1


def test_decode_rejects_internal_newline() -> None:
    s = encode(0, 45)
    with pytest.raises(InvalidCharacter) as exc:
        _ = decode(s[:5] + "\n" + s[5:], 45)
    assert exc.value.char == "\n"
    assert not isinstance(exc.value, ExcludedConfusable)


def test_decode_aliases_i_l_o() -> None:
    s = encode(1, 45)  # payload ends in "1"
    assert s[9] == "1"
    assert decode(s[:9] + "I" + s[10:], 45) == 1
    assert decode(s[:9] + "L" + s[10:], 45) == 1
    z = encode(0, 45)
    assert decode("O" + z[1:], 45) == 0


def test_decode_rejects_excluded_confusables_with_position() -> None:
    s = encode(0, 45)
    for bad in "25SZU":
        with pytest.raises(ExcludedConfusable) as exc:
            _ = decode(bad + s[1:], 45)
        assert exc.value.char == bad
        assert exc.value.position == 0


def test_decode_rejects_other_invalid_characters() -> None:
    s = encode(0, 45)
    with pytest.raises(InvalidCharacter) as exc:
        _ = decode(s[:5] + "*" + s[6:], 45)
    assert exc.value.position == 5
    assert not isinstance(exc.value, ExcludedConfusable)


def test_decode_rejects_excluded_confusable_position_counts_hyphens() -> None:
    # "4B4-S8NK-DG9R" is the hyphenated rev45 display form for value
    # 35184372088831 with the payload's fifth symbol ("K", ALPHABET index 4)
    # swapped for the excluded confusable "S". Raw indices: 0='4', 1='B',
    # 2='4', 3='-', 4='S'. The reported position must count the hyphen at
    # index 3, landing on 4, not 3 (the offset it would have in the
    # hyphen-stripped payload).
    s = encode(35184372088831, 45)
    assert s[:5] == "4B4K8"
    grouped = format_rev45(s)
    bad = grouped.replace("K8", "S8", 1)
    assert bad == "4B4-S8NK-DG9R"
    with pytest.raises(ExcludedConfusable) as exc:
        _ = decode(bad, 45)
    assert exc.value.char == "S"
    assert exc.value.position == 4


def test_decode_wrong_length_too_few() -> None:
    with pytest.raises(WrongLength) as exc:
        _ = decode("0000", 45)
    assert exc.value.got == 4
    assert exc.value.expected == 11


def test_decode_wrong_length_too_many() -> None:
    s = encode(0, 45)  # 11 valid symbols
    with pytest.raises(WrongLength) as exc:
        _ = decode(s + "0", 45)
    assert exc.value.got == 12
    assert exc.value.expected == 11


def test_single_symbol_error_always_caught() -> None:
    s = encode(0x1234_5678_ABC, 45)
    for pos in range(11):
        for c in ALPHABET:
            if c == s[pos]:
                continue
            corrupted = s[:pos] + c + s[pos + 1 :]
            with pytest.raises(CheckMismatch):
                _ = decode(corrupted, 45)


def test_adjacent_transposition_always_caught() -> None:
    s = encode(0x1234_5678_ABC, 45)
    for pos in range(10):
        if s[pos] == s[pos + 1]:
            continue
        swapped = s[:pos] + s[pos + 1] + s[pos] + s[pos + 2 :]
        with pytest.raises(CheckMismatch):
            _ = decode(swapped, 45)


def test_decode_overflow_rejected() -> None:
    # Payload "Y" * 10 is 28**10 - 1 >= 2**45; append its valid check
    # symbol so only the value check can fail.
    payload = "Y" * 10
    with pytest.raises(Overflow):
        _ = decode(payload + check_symbol(payload), 45)


def test_overflow_carries_value_and_bits() -> None:
    with pytest.raises(Overflow) as exc:
        _ = encode_payload(2**45, 45)
    assert exc.value.value == 2**45
    assert exc.value.bits == 45


def test_format_rev45() -> None:
    s = encode(2**45 - 1, 45)
    g = format_rev45(s)
    assert len(g) == 13
    assert g[3] == "-" and g[8] == "-"
    assert g.replace("-", "") == s


def test_format_rev45_rejects_wrong_length() -> None:
    with pytest.raises(WrongLength) as exc:
        _ = format_rev45("000")
    assert exc.value.got == 3
    assert exc.value.expected == 11
