import pytest

from base28 import Overflow, rev45

# From SPEC section 9, valid vector row 5.
KNOWN_VALUE = 2832504837759
KNOWN_COMPACT = "09FWWAHNMTK"
KNOWN_DISPLAY = "09F-WWAH-NMTK"


def test_profile_constants() -> None:
    assert rev45.BITS == 45
    assert rev45.PAYLOAD_SYMBOLS == 10
    assert rev45.TOTAL_SYMBOLS == 11


def test_encode_matches_known_vector() -> None:
    assert rev45.encode(KNOWN_VALUE) == KNOWN_DISPLAY
    assert rev45.encode_compact(KNOWN_VALUE) == KNOWN_COMPACT


def test_decode_accepts_grouped_compact_and_messy() -> None:
    assert rev45.decode(KNOWN_DISPLAY) == KNOWN_VALUE
    assert rev45.decode(KNOWN_COMPACT) == KNOWN_VALUE
    assert rev45.decode(f"  {KNOWN_DISPLAY.lower()}  ") == KNOWN_VALUE


def test_roundtrip_boundaries() -> None:
    for v in [0, 1, 27, 28, 2**44, 2**45 - 1]:
        assert rev45.decode(rev45.encode(v)) == v


def test_encode_rejects_out_of_range() -> None:
    with pytest.raises(Overflow):
        _ = rev45.encode(2**45)
    with pytest.raises(Overflow):
        _ = rev45.encode(-1)
