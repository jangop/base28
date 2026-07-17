"""Generic base28 encode/decode over an explicit bit width (SPEC sections 3-6).

``encode``/``decode`` work for any width in ``[MIN_BITS, MAX_BITS]``. The
:mod:`base28.rev45` module builds the named 45-bit profile on top of these.
"""

from base28._alphabet import ALIASES, ALPHABET, EXCLUDED
from base28._damm import check_symbol, damm_fold
from base28.errors import (
    CheckMismatch,
    ExcludedConfusable,
    InvalidCharacter,
    Overflow,
    WrongLength,
)

MIN_BITS = 1
MAX_BITS = 128


def symbol_count(n: int) -> int:
    """Smallest k with 28**k >= 2**n, for MIN_BITS <= n <= MAX_BITS."""
    if not MIN_BITS <= n <= MAX_BITS:
        raise ValueError(f"bit width must be in [{MIN_BITS}, {MAX_BITS}], got {n}")
    target = 1 << n  # 2**n, but typed int (2**n widens to Any under negative exponents)
    k = 1
    power = 28
    while power < target:
        power *= 28
        k += 1
    return k


def encode_payload(v: int, n: int) -> str:
    """Encode v as exactly symbol_count(n) base28 symbols, big-endian."""
    k = symbol_count(n)
    if not 0 <= v < 2**n:
        raise Overflow(v, n)
    out: list[str] = []
    rest = v
    for _ in range(k):
        rest, digit = divmod(rest, 28)
        out.append(ALPHABET[digit])
    return "".join(reversed(out))


def encode(v: int, n: int) -> str:
    """Encode v as a base28 payload of symbol_count(n) symbols plus a check."""
    payload = encode_payload(v, n)
    return payload + check_symbol(payload)


def _normalize(s: str, expected: int) -> str:
    cleaned: list[str] = []
    for pos, raw in enumerate(s.strip()):
        c = raw.upper()
        if c in "- \t":
            continue
        c = ALIASES.get(c, c)
        if c in EXCLUDED:
            raise ExcludedConfusable(raw, pos)
        if c not in ALPHABET:
            raise InvalidCharacter(raw, pos)
        cleaned.append(c)
    if len(cleaned) != expected:
        raise WrongLength(len(cleaned), expected)
    return "".join(cleaned)


def decode(s: str, n: int) -> int:
    """Decode a base28 string (with check symbol) back to its integer value."""
    k = symbol_count(n)
    cleaned = _normalize(s, k + 1)
    values = [ALPHABET.index(c) for c in cleaned]
    if damm_fold(values) != 0:
        raise CheckMismatch("check symbol mismatch; at least one symbol is wrong")
    v = 0
    for value in values[:k]:
        v = v * 28 + value
    if v >= 2**n:
        raise Overflow(v, n)
    return v


def format_rev45(s: str) -> str:
    """Group an 11-symbol rev45 code as ``XXX-XXXX-XXXX`` for display."""
    if len(s) != 11:
        raise WrongLength(len(s), 11)
    return f"{s[0:3]}-{s[3:7]}-{s[7:11]}"
