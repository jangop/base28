"""Reference implementation of the base28 encoding.

Normative document: SPEC.md. This module exists to generate and verify the
frozen artifacts (Damm table, test vectors); it is not a published library.
"""

ALPHABET = "01346789ABCDEFGHJKMNPQRTVWXY"

MIN_BITS = 1
MAX_BITS = 128


class Base28Error(Exception):
    """Base class for all base28 errors."""


class Overflow(Base28Error):
    """Value out of range for the declared bit width."""


def symbol_count(n: int) -> int:
    """Smallest k with 28**k >= 2**n, for MIN_BITS <= n <= MAX_BITS."""
    if not MIN_BITS <= n <= MAX_BITS:
        raise ValueError(f"bit width must be in [{MIN_BITS}, {MAX_BITS}], got {n}")
    k = 1
    while 28**k < 2**n:
        k += 1
    return k


def encode_payload(v: int, n: int) -> str:
    """Encode v as exactly symbol_count(n) base28 symbols, big-endian."""
    k = symbol_count(n)
    if not 0 <= v < 2**n:
        raise Overflow(f"value must be in [0, 2**{n}), got {v}")
    out: list[str] = []
    rest = v
    for _ in range(k):
        rest, digit = divmod(rest, 28)
        out.append(ALPHABET[digit])
    return "".join(reversed(out))
