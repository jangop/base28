"""Generate test-vectors.json for the rev45 profile.

Run: uv run python -m tools.generate_vectors
SHA-256-derived values use fixed input strings so output is reproducible.
"""

import hashlib
import json
from pathlib import Path

from tools.base28ref import check_symbol, encode, format_rev45

OUT_PATH = Path(__file__).resolve().parent.parent / "test-vectors.json"


def sha_value(seed: str) -> int:
    digest = hashlib.sha256(seed.encode()).digest()
    return int.from_bytes(digest[:6], "big") >> 3  # top 45 bits


def main() -> None:
    seeds = [0, 2**45 - 1, sha_value("base28"), sha_value("rev45"), sha_value("vector-3")]
    encoded = [encode(v, 45) for v in seeds]
    valid = [
        {"value": v, "encoded": e, "display": format_rev45(e)}
        for v, e in zip(seeds, encoded, strict=True)
    ]
    good = encoded[2]
    overflow_payload = "Y" * 10
    invalid = [
        {"input": "S" + good[1:], "error": "ExcludedConfusable"},
        {"input": good[:5] + "*" + good[6:], "error": "InvalidCharacter"},
        {"input": good[:8], "error": "WrongLength"},
        {
            "input": good[:10] + ("0" if good[10] != "0" else "1"),
            "error": "CheckMismatch",
        },
        {
            "input": overflow_payload + check_symbol(overflow_payload),
            "error": "Overflow",
        },
    ]
    _ = OUT_PATH.write_text(
        json.dumps(
            {
                "profile": "rev45",
                "bits": 45,
                "payload_symbols": 10,
                "total_symbols": 11,
                "valid": valid,
                "invalid": invalid,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
