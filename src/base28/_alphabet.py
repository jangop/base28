"""base28 alphabet and normalization tables (SPEC sections 2 and 6).

The alphabet is Crockford base32 with the four confusable symbols 2, 5, S, Z
removed, leaving 28 symbols. ``ALIASES`` folds the transcription-confusable
letters onto their intended digit; ``EXCLUDED`` names the symbols that are
never part of a code and must be rejected rather than silently repaired.
"""

ALPHABET = "01346789ABCDEFGHJKMNPQRTVWXY"

# Decode-time repairs: uppercase letters a reader is likely to write for a
# digit. I and L read as 1; O reads as 0.
ALIASES = {"I": "1", "L": "1", "O": "0"}

# Confusable symbols that are deliberately not in the alphabet. Hitting one
# during decode is a hard error (re-read the source), not a repair.
EXCLUDED = frozenset("25SZU")
