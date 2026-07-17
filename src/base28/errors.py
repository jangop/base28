"""Error taxonomy for base28 (SPEC section 6).

Every decode failure raises a subclass of :class:`Base28Error`, so callers
can catch the base class to reject an input or match a specific subclass to
tell the user what to fix.
"""


class Base28Error(Exception):
    """Base class for all base28 errors."""


class Overflow(Base28Error):
    """Value out of range for the declared bit width."""

    def __init__(self, value: int, bits: int) -> None:
        self.value: int = value
        self.bits: int = bits
        super().__init__(f"value {value} out of range for {bits}-bit width")


class InvalidCharacter(Base28Error):
    """A symbol that is not in the alphabet and has no alias."""

    def __init__(self, char: str, position: int, message: str | None = None) -> None:
        self.char: str = char
        self.position: int = position
        if message is None:
            message = f"invalid character {char!r} at position {position}"
        super().__init__(message)


class ExcludedConfusable(InvalidCharacter):
    """A confusable symbol (2, 5, S, Z, U) deliberately excluded from base28."""

    def __init__(self, char: str, position: int) -> None:
        super().__init__(
            char,
            position,
            f"character {char!r} at position {position} is never part of a "
            + "base28 code (excluded as confusable); re-read the source",
        )


class WrongLength(Base28Error):
    """The input has the wrong number of symbols after normalization."""

    def __init__(self, got: int, expected: int) -> None:
        self.got: int = got
        self.expected: int = expected
        super().__init__(f"expected {expected} symbols, got {got}")


class CheckMismatch(Base28Error):
    """Check symbol does not match payload."""
