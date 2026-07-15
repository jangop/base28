"""Reference implementation of the base28 encoding.

Normative document: SPEC.md. This module exists to generate and verify the
frozen artifacts (Damm table, test vectors); it is not a published library.
"""

import json
from pathlib import Path
from typing import cast

ALPHABET = "01346789ABCDEFGHJKMNPQRTVWXY"

MIN_BITS = 1
MAX_BITS = 128

_TABLE_PATH = Path(__file__).resolve().parent.parent / "damm_table.json"
_TABLE_DATA = cast(dict[str, object], json.loads(_TABLE_PATH.read_text()))
DAMM_TABLE = cast(list[list[int]], _TABLE_DATA["table"])

ALIASES = {"I": "1", "L": "1", "O": "0"}
EXCLUDED = set("25SZU")


class Base28Error(Exception):
    """Base class for all base28 errors."""


class Overflow(Base28Error):
    """Value out of range for the declared bit width."""

    def __init__(self, value: int, bits: int) -> None:
        self.value: int = value
        self.bits: int = bits
        super().__init__(f"value {value} out of range for {bits}-bit width")


class InvalidCharacter(Base28Error):
    def __init__(self, char: str, position: int, message: str | None = None) -> None:
        self.char: str = char
        self.position: int = position
        if message is None:
            message = f"invalid character {char!r} at position {position}"
        super().__init__(message)


class ExcludedConfusable(InvalidCharacter):
    def __init__(self, char: str, position: int) -> None:
        super().__init__(
            char,
            position,
            f"character {char!r} at position {position} is never part of a "
            + "base28 code (excluded as confusable); re-read the source",
        )


class WrongLength(Base28Error):
    def __init__(self, got: int, expected: int) -> None:
        self.got: int = got
        self.expected: int = expected
        super().__init__(f"expected {expected} symbols, got {got}")


class CheckMismatch(Base28Error):
    """Check symbol does not match payload."""


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


def damm_fold(values: list[int]) -> int:
    interim = 0
    for v in values:
        interim = DAMM_TABLE[interim][v]
    return interim


def check_symbol(payload: str) -> str:
    interim = damm_fold([ALPHABET.index(c) for c in payload])
    row = DAMM_TABLE[interim]
    return ALPHABET[row.index(0)]


def encode(v: int, n: int) -> str:
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
    if len(s) != 11:
        raise WrongLength(len(s), 11)
    return f"{s[0:3]}-{s[3:7]}-{s[7:11]}"
