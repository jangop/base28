"""The ``rev45`` profile: a 45-bit value as an ``XXX-XXXX-XXXX`` code.

This is the intended everyday surface. ``encode`` takes an integer in
``[0, 2**45)`` and returns the grouped display form; ``decode`` accepts either
the grouped or the ungrouped form (and tolerates case, whitespace, and the
I/L/O aliases) and returns the integer.
"""

from base28 import _core

BITS = 45
PAYLOAD_SYMBOLS = _core.symbol_count(BITS)  # 10
TOTAL_SYMBOLS = PAYLOAD_SYMBOLS + 1  # 11, including the check symbol


def encode(value: int) -> str:
    """Encode a 45-bit value as a grouped ``XXX-XXXX-XXXX`` code."""
    return _core.format_rev45(_core.encode(value, BITS))


def encode_compact(value: int) -> str:
    """Encode a 45-bit value as 11 symbols with no group separators."""
    return _core.encode(value, BITS)


def decode(text: str) -> int:
    """Decode a rev45 code (grouped or compact) back to its 45-bit value."""
    return _core.decode(text, BITS)
