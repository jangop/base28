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
        if display.replace("-", "") != encoded:
            print(f"DISPLAY MISMATCH value={v}")
            failures += 1
        full_interim = 0
        for c in encoded:
            full_interim = table[full_interim][ALPHABET.index(c)]
        if full_interim != 0:
            print(f"FOLD NOT ZERO value={v}")
            failures += 1
    if failures:
        print(f"{failures} failures", file=sys.stderr)
        return 1
    print(f"all {len(valid_cases)} valid vectors verified independently")
    return 0


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
