"""Independently verify test-vectors.json.

Deliberately does NOT import base28ref: alphabet, base conversion, and the
Damm fold are reimplemented here from the spec text alone, against the
frozen damm_table.json. Run: uv run python tools/verify_vectors.py
"""

import json
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parent.parent
ALPHABET = "01346789ABCDEFGHJKMNPQRTVWXY"
ALIASES = {"I": "1", "L": "1", "O": "0"}
EXCLUDED = set("25SZU")


def classify_invalid(inp: str, table: list[list[int]]) -> str:
    """Return the error class the decode pipeline (SPEC section 6) raises first.

    Reimplemented from the spec text, independent of base28ref, so a
    mislabeled invalid vector is caught rather than rubber-stamped.
    """
    symbols: list[str] = []
    for raw in inp.strip():
        c = raw.upper()
        if c in "- \t":
            continue
        c = ALIASES.get(c, c)
        if c in EXCLUDED:
            return "ExcludedConfusable"
        if c not in ALPHABET:
            return "InvalidCharacter"
        symbols.append(c)
    if len(symbols) != 11:
        return "WrongLength"
    interim = 0
    for c in symbols:
        interim = table[interim][ALPHABET.index(c)]
    if interim != 0:
        return "CheckMismatch"
    value = 0
    for c in symbols[:10]:
        value = value * 28 + ALPHABET.index(c)
    if value >= 2**45:
        return "Overflow"
    return "VALID"


def main() -> int:
    table_data = cast(
        dict[str, object], json.loads((ROOT / "damm_table.json").read_text())
    )
    table = cast(list[list[int]], table_data["table"])
    vectors = cast(
        dict[str, object], json.loads((ROOT / "test-vectors.json").read_text())
    )
    assert vectors["bits"] == 45 and vectors["payload_symbols"] == 10
    valid_cases = cast(list[dict[str, object]], vectors["valid"])
    failures = 0
    for case in valid_cases:
        v = cast(int, case["value"])
        encoded = cast(str, case["encoded"])
        display = cast(str, case["display"])
        # independent big-endian base-28 conversion
        digits: list[int] = []
        rest = v
        for _ in range(10):
            digits.append(rest % 28)
            rest //= 28
        payload = "".join(ALPHABET[d] for d in reversed(digits))
        interim = 0
        for c in payload:
            interim = table[interim][ALPHABET.index(c)]
        check = ALPHABET[table[interim].index(0)]
        expect = payload + check
        if expect != encoded:
            print(f"MISMATCH value={v}: expected {expect}, file has {encoded}")
            failures += 1
        expected_display = f"{encoded[0:3]}-{encoded[3:7]}-{encoded[7:11]}"
        if display != expected_display:
            print(
                f"DISPLAY MISMATCH value={v}: expected {expected_display}, "
                + f"file has {display}"
            )
            failures += 1
        full_interim = 0
        for c in encoded:
            full_interim = table[full_interim][ALPHABET.index(c)]
        if full_interim != 0:
            print(f"FOLD NOT ZERO value={v}")
            failures += 1
    invalid_cases = cast(list[dict[str, object]], vectors["invalid"])
    for case in invalid_cases:
        inp = cast(str, case["input"])
        declared = cast(str, case["error"])
        actual = classify_invalid(inp, table)
        if actual != declared:
            print(f"INVALID MISLABELED input={inp!r}: declared {declared}, is {actual}")
            failures += 1
    if failures:
        print(f"{failures} failures", file=sys.stderr)
        return 1
    print(
        f"all {len(valid_cases)} valid and {len(invalid_cases)} invalid "
        + "vectors verified independently"
    )
    return 0


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
