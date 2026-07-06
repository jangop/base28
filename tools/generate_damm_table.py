"""Generate and verify the order-28 WTA quasigroup for the Damm check.

Run: uv run python tools/generate_damm_table.py
Writes damm_table.json in the repo root. Exits nonzero if no candidate
passes verification.
"""

import json
import math
import sys
from pathlib import Path

ORDER = 28
OUT_PATH = Path(__file__).resolve().parent.parent / "damm_table.json"


def is_latin_square(table: list[list[int]]) -> bool:
    full = set(range(ORDER))
    if len(table) != ORDER:
        return False
    for row in table:
        if set(row) != full:
            return False
    for col in range(ORDER):
        if {table[row][col] for row in range(ORDER)} != full:
            return False
    return True


def is_weak_totally_antisymmetric(table: list[list[int]]) -> bool:
    for c in range(ORDER):
        for x in range(ORDER):
            for y in range(x + 1, ORDER):
                if table[table[c][x]][y] == table[table[c][y]][x]:
                    return False
    return True


def coprime_units() -> list[int]:
    return [a for a in range(1, ORDER) if math.gcd(a, ORDER) == 1]


def linear_table(a: int, b: int) -> list[list[int]]:
    return [[(a * x + b * y) % ORDER for y in range(ORDER)] for x in range(ORDER)]


def to_group(i: int) -> tuple[int, int, int]:
    """Index 0..27 as an element of Z_2 x Z_2 x Z_7."""
    return (i // 14, (i % 14) // 7, i % 7)


def from_group(a: int, b: int, z: int) -> int:
    return a * 14 + b * 7 + z


def add_idx(x: int, y: int) -> int:
    xa, xb, xz = to_group(x)
    ya, yb, yz = to_group(y)
    return from_group((xa + ya) % 2, (xb + yb) % 2, (xz + yz) % 7)


def sigma_idx(i: int) -> int:
    """Orthomorphism of Z_2 x Z_2 x Z_7: [[0,1],[1,1]] on the Klein part, doubling on Z_7."""
    a, b, z = to_group(i)
    return from_group(b, (a + b) % 2, (2 * z) % 7)


CONSTRUCTION = (
    "product-orthomorphism Z2xZ2xZ7: sigma = ([[0,1],[1,1]] on Z2^2, z->2z on Z7), "
    "T[x][y] = sigma[x + y], index i = (i//14, (i%14)//7, i%7)"
)


def orthomorphism_table() -> list[list[int]]:
    return [[sigma_idx(add_idx(x, y)) for y in range(ORDER)] for x in range(ORDER)]


def main() -> int:
    # Sanity sweep: every linear candidate over Z_28 must fail WTA
    # (cyclic groups of even order have no orthomorphisms). A pass here
    # means the checker is broken.
    for a in coprime_units():
        for b in coprime_units():
            t = linear_table(a, b)
            if not is_latin_square(t):
                print(f"CHECKER BUG: linear a={a} b={b} not Latin", file=sys.stderr)
                return 1
            if is_weak_totally_antisymmetric(t):
                print(f"CHECKER BUG: linear a={a} b={b} passed WTA", file=sys.stderr)
                return 1
    table = orthomorphism_table()
    if not (is_latin_square(table) and is_weak_totally_antisymmetric(table)):
        print("construction failed verification; STOP and investigate", file=sys.stderr)
        return 1
    _ = OUT_PATH.write_text(
        json.dumps({"order": ORDER, "construction": CONSTRUCTION, "table": table})
        + "\n"
    )
    print(f"orthomorphism table verified (Latin + WTA): {CONSTRUCTION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
