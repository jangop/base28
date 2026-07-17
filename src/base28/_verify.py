"""Independent re-verification of the frozen test vectors (SPEC section 9).

Deliberately self-contained: the alphabet, base-28 conversion, and the Damm
fold are reimplemented here from the spec text, against the frozen
``damm_table.json``, and NOT imported from :mod:`base28._core`. A bug in the
core that also corrupted the vectors would still be caught, because the two
implementations would have to be wrong in the same way.
"""

import json
from dataclasses import dataclass, field
from importlib.resources import files
from typing import cast

_ALPHABET = "01346789ABCDEFGHJKMNPQRTVWXY"
_ALIASES = {"I": "1", "L": "1", "O": "0"}
_EXCLUDED = frozenset("25SZU")


@dataclass
class VerifyResult:
    """Outcome of :func:`verify`: per-class counts and any failure messages."""

    valid_checked: int = 0
    invalid_checked: int = 0
    failures: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


def _classify_invalid(inp: str, table: list[list[int]]) -> str:
    """Return the error class SPEC section 6's decode pipeline raises first."""
    symbols: list[str] = []
    for raw in inp.strip():
        c = raw.upper()
        if c in "- \t":
            continue
        c = _ALIASES.get(c, c)
        if c in _EXCLUDED:
            return "ExcludedConfusable"
        if c not in _ALPHABET:
            return "InvalidCharacter"
        symbols.append(c)
    if len(symbols) != 11:
        return "WrongLength"
    interim = 0
    for c in symbols:
        interim = table[interim][_ALPHABET.index(c)]
    if interim != 0:
        return "CheckMismatch"
    value = 0
    for c in symbols[:10]:
        value = value * 28 + _ALPHABET.index(c)
    if value >= 2**45:
        return "Overflow"
    return "VALID"


def _load(name: str) -> dict[str, object]:
    resource = files("base28") / "data" / name
    return cast(dict[str, object], json.loads(resource.read_text()))


def verify() -> VerifyResult:
    """Re-derive every frozen vector independently and report mismatches."""
    result = VerifyResult()
    table = cast(list[list[int]], _load("damm_table.json")["table"])
    vectors = _load("test-vectors.json")
    if vectors["bits"] != 45 or vectors["payload_symbols"] != 10:
        result.failures.append("vector header is not the rev45 profile")
        return result

    for case in cast(list[dict[str, object]], vectors["valid"]):
        v = cast(int, case["value"])
        encoded = cast(str, case["encoded"])
        display = cast(str, case["display"])
        result.valid_checked += 1

        digits: list[int] = []
        rest = v
        for _ in range(10):
            digits.append(rest % 28)
            rest //= 28
        payload = "".join(_ALPHABET[d] for d in reversed(digits))
        interim = 0
        for c in payload:
            interim = table[interim][_ALPHABET.index(c)]
        check = _ALPHABET[table[interim].index(0)]
        expect = payload + check
        if expect != encoded:
            result.failures.append(f"value {v}: expected {expect}, file has {encoded}")
        expected_display = f"{encoded[0:3]}-{encoded[3:7]}-{encoded[7:11]}"
        if display != expected_display:
            result.failures.append(
                f"value {v}: display expected {expected_display}, file has {display}"
            )
        full = 0
        for c in encoded:
            full = table[full][_ALPHABET.index(c)]
        if full != 0:
            result.failures.append(f"value {v}: full fold is not zero")

    for case in cast(list[dict[str, object]], vectors["invalid"]):
        inp = cast(str, case["input"])
        declared = cast(str, case["error"])
        result.invalid_checked += 1
        actual = _classify_invalid(inp, table)
        if actual != declared:
            result.failures.append(f"input {inp!r}: declared {declared}, is {actual}")

    return result
