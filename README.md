# base28

A confusable-hardened symbol encoding for short, printed,
human-transcribable codes. Crockford base32 with 2, 5, S, and Z removed:
28 symbols, fixed-width integer encoding, Damm check symbol that catches any
single wrong symbol or adjacent transposition.

Normative specification: [SPEC.md](SPEC.md). Frozen artifacts:
[damm_table.json](src/base28/data/damm_table.json),
[test-vectors.json](src/base28/data/test-vectors.json).

## Install

Not yet published to PyPI. Install from a checkout:

```bash
uv pip install .       # from the repo root
```

Once published: `uv add base28` (or `pip install base28`).

## Library

The everyday surface is the `rev45` profile: a 45-bit value as an
`XXX-XXXX-XXXX` code.

```python
from base28 import rev45

rev45.encode(2832504837759)     # '09F-WWAH-NMTK'
rev45.encode_compact(2832504837759)  # '09FWWAHNMTK'
rev45.decode('09f-wwah-nmtk')   # 2832504837759  (case, spaces, I/L/O tolerated)
```

The generic width mechanism (any width in 1..128 bits) is available directly:

```python
import base28

base28.encode(0, 45)            # '00000000000'
base28.decode('00000000000', 45)  # 0
base28.symbol_count(45)         # 10
```

Decode failures raise a subclass of `base28.Base28Error`
(`Overflow`, `InvalidCharacter`, `ExcludedConfusable`, `WrongLength`,
`CheckMismatch`), so callers can reject an input or explain what to fix.

## CLI

```bash
base28 encode 2832504837759     # 09F-WWAH-NMTK
base28 encode 2832504837759 --compact   # 09FWWAHNMTK
base28 encode 999 --bits 20     # generic width, ungrouped
base28 decode 09f-wwah-nmtk     # 2832504837759
base28 verify                   # re-check the frozen test vectors independently
```

## Development

```bash
uv sync
uv run pytest             # property, vector, rev45, and CLI tests
uv run ruff check .
uv run basedpyright
```

The frozen artifacts are regenerated (and re-verified) by the dev-only
scripts under `tools/`:

```bash
uv run python -m tools.generate_damm_table   # writes src/base28/data/damm_table.json
uv run python -m tools.generate_vectors      # writes src/base28/data/test-vectors.json
```
