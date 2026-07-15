import json
from pathlib import Path
from typing import cast

from tools.generate_damm_table import (
    is_latin_square,
    is_weak_totally_antisymmetric,
)

TABLE_PATH = Path(__file__).resolve().parent.parent / "damm_table.json"


def load_table() -> list[list[int]]:
    data = cast(dict[str, object], json.loads(TABLE_PATH.read_text()))
    assert data["order"] == 28
    assert isinstance(data["construction"], str) and data["construction"]
    table = cast(list[list[int]], data["table"])
    return table


def test_table_is_latin_square() -> None:
    assert is_latin_square(load_table())


def test_table_is_weak_totally_antisymmetric() -> None:
    assert is_weak_totally_antisymmetric(load_table())


def test_property_checkers_reject_bad_tables() -> None:
    # x + y mod 28 is a Latin square but not WTA (it is commutative,
    # so (c*x)*y == (c*y)*x for all x, y).
    add_table = [[(x + y) % 28 for y in range(28)] for x in range(28)]
    assert is_latin_square(add_table)
    assert not is_weak_totally_antisymmetric(add_table)
    not_latin = [[0] * 28 for _ in range(28)]
    assert not is_latin_square(not_latin)
    # Every row is a valid permutation of 0..27 (passes the row check), but
    # all rows are identical, so every column is constant. This exercises
    # is_latin_square's column-uniqueness branch, which the row-broken
    # all-zero fixture above never reaches.
    row_ok_col_bad = [list(range(28)) for _ in range(28)]
    assert not is_latin_square(row_ok_col_bad)
