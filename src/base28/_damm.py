"""Damm check-symbol machinery over the frozen order-28 WTA table.

The table is loaded once from packaged data (``base28/data/damm_table.json``),
the same artifact the spec freezes. A single wrong symbol or a single adjacent
transposition always changes the fold result, so both are always detected.
"""

import json
from importlib.resources import files
from typing import cast

from base28._alphabet import ALPHABET

_TABLE_RESOURCE = files("base28") / "data" / "damm_table.json"
_TABLE_DATA = cast(dict[str, object], json.loads(_TABLE_RESOURCE.read_text()))
DAMM_TABLE = cast(list[list[int]], _TABLE_DATA["table"])


def damm_fold(values: list[int]) -> int:
    """Fold a list of alphabet indices through the Damm table, starting at 0."""
    interim = 0
    for v in values:
        interim = DAMM_TABLE[interim][v]
    return interim


def check_symbol(payload: str) -> str:
    """Return the single symbol that makes the full string fold to 0."""
    interim = damm_fold([ALPHABET.index(c) for c in payload])
    row = DAMM_TABLE[interim]
    return ALPHABET[row.index(0)]
