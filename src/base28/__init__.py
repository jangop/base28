"""base28: a confusable-hardened symbol encoding for short printed codes.

Crockford base32 with 2, 5, S, and Z removed (28 symbols), fixed-width integer
encoding, and a Damm check symbol that catches any single-symbol error or
adjacent transposition. See ``SPEC.md`` for the normative specification.

Everyday use is the :mod:`base28.rev45` profile::

    from base28 import rev45
    code = rev45.encode(2832504837759)   # '09F-WWAH-NMTK'
    rev45.decode('09f-wwah-nmtk')        # 2832504837759

The generic width mechanism is available directly::

    import base28
    base28.encode(0, 45)                  # '00000000000'
    base28.decode('00000000000', 45)      # 0
"""

from importlib.metadata import PackageNotFoundError, version

from base28._alphabet import ALPHABET
from base28._core import (
    MAX_BITS,
    MIN_BITS,
    decode,
    encode,
    encode_payload,
    format_rev45,
    symbol_count,
)
from base28._damm import check_symbol
from base28.errors import (
    Base28Error,
    CheckMismatch,
    ExcludedConfusable,
    InvalidCharacter,
    Overflow,
    WrongLength,
)

try:
    __version__ = version("base28")
except PackageNotFoundError:  # pragma: no cover - source tree without metadata
    __version__ = "0.0.0+unknown"

__all__ = [
    "ALPHABET",
    "MAX_BITS",
    "MIN_BITS",
    "Base28Error",
    "CheckMismatch",
    "ExcludedConfusable",
    "InvalidCharacter",
    "Overflow",
    "WrongLength",
    "__version__",
    "check_symbol",
    "decode",
    "encode",
    "encode_payload",
    "format_rev45",
    "symbol_count",
]
