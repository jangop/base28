import json
from pathlib import Path
from typing import cast

import pytest

from base28 import (
    Base28Error,
    CheckMismatch,
    ExcludedConfusable,
    InvalidCharacter,
    Overflow,
    WrongLength,
    decode,
)

VECTORS_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "base28"
    / "data"
    / "test-vectors.json"
)

ERROR_TYPES: dict[str, type[Base28Error]] = {
    "ExcludedConfusable": ExcludedConfusable,
    "InvalidCharacter": InvalidCharacter,
    "WrongLength": WrongLength,
    "CheckMismatch": CheckMismatch,
    "Overflow": Overflow,
}


def load_vectors() -> dict[str, object]:
    return cast(dict[str, object], json.loads(VECTORS_PATH.read_text()))


def test_valid_vectors_decode() -> None:
    vectors = load_vectors()
    valid_cases = cast(list[dict[str, object]], vectors["valid"])
    assert len(valid_cases) == 5
    for case in valid_cases:
        encoded = cast(str, case["encoded"])
        display = cast(str, case["display"])
        value = cast(int, case["value"])
        assert decode(encoded, 45) == value
        assert decode(display, 45) == value


def test_invalid_vectors_raise_declared_error() -> None:
    vectors = load_vectors()
    invalid_cases = cast(list[dict[str, object]], vectors["invalid"])
    assert len(invalid_cases) == 5
    for case in invalid_cases:
        error_name = cast(str, case["error"])
        bad_input = cast(str, case["input"])
        with pytest.raises(ERROR_TYPES[error_name]):
            _ = decode(bad_input, 45)
