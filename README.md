# base28

A confusable-hardened symbol encoding for short, printed,
human-transcribable codes. Crockford base32 with 2, 5, S, and Z removed:
28 symbols, arbitrary-precision encoding, Damm check symbol.

Normative specification: [SPEC.md](SPEC.md). Frozen artifacts:
[damm_table.json](damm_table.json), [test-vectors.json](test-vectors.json).

Status: draft v0.1. No published library yet; tools/ holds the reference
implementation used to generate and verify the frozen artifacts.

```bash
uv run pytest              # property + vector tests
uv run python tools/verify_vectors.py   # independent re-verification
```
