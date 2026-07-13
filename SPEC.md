# base28 v0.1 (draft)

## 1. Introduction

base28 is a confusable-hardened symbol encoding for short, printed,
human-transcribable codes: fixed-width unsigned integers rendered as
uppercase alphanumeric strings, with a trailing check symbol that catches
the two dominant typed-back error classes. It exists for codes that a human
reads off a screen or a label and types back in elsewhere, where every
excluded glyph pair is one fewer chance for a misread to silently become a
different, valid-looking code. Prior art: Douglas Crockford's
[base32](https://www.crockford.com/base32.html) drops the visually
confusable `I`, `L`, `O`, `U` and defines decode aliases for the ones it
keeps close to the alphabet (`I`/`L` to `1`, `O` to `0`); Zooko
Wilcox-O'Hearn's [z-base-32](https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt)
uses its own distinct 32-symbol alphabet, `ybndrfg8ejkmcpqxot1uwisza345h769`,
which is not a permutation of Crockford's: rather than dropping both
members of a confusable pair, it picks one survivor per pair (for example,
keeps `z`, drops `2`; keeps `o`, drops `0`), and orders its own symbol set
by human-perceived frequency for spoken and handwritten transcription.
base28 instead keeps Crockford's alphabet, its ascending order, and its
I/L/O alias mechanism, but goes one step further: it drops `2`, `5`, `S`,
and `Z` entirely rather than aliasing or picking a survivor, on the
reasoning in section 6. Twenty-eight symbols remain.

## 2. Alphabet

28 symbols, values 0 through 27, ascending. Encoding always emits
uppercase; no symbol below is ever emitted in lowercase.

| Value | Symbol | Value | Symbol | Value | Symbol | Value | Symbol |
|---|---|---|---|---|---|---|---|
| 0 | `0` | 7 | `9` | 14 | `G` | 21 | `Q` |
| 1 | `1` | 8 | `A` | 15 | `H` | 22 | `R` |
| 2 | `3` | 9 | `B` | 16 | `J` | 23 | `T` |
| 3 | `4` | 10 | `C` | 17 | `K` | 24 | `V` |
| 4 | `6` | 11 | `D` | 18 | `M` | 25 | `W` |
| 5 | `7` | 12 | `E` | 19 | `N` | 26 | `X` |
| 6 | `8` | 13 | `F` | 20 | `P` | 27 | `Y` |

The alphabet string, in ascending value order:

```
01346789ABCDEFGHJKMNPQRTVWXY
```

The table and the string above encode the same mapping (table read
column-major, seven rows by four columns, index = value). The alphabet is
Crockford base32's 32-symbol set (which already omits `I`, `L`, `O`, `U`)
minus `2`, `5`, `S`, `Z`, leaving `01346789ABCDEFGHJKMNPQRTVWXY`.

## 3. Data model

The value being encoded is an unsigned integer `v` with a declared bit
width `n`, where `1 <= n <= 128` and `0 <= v < 2^n`. The bit width is a
profile parameter (see section 8): it is agreed out of band between
encoder and decoder and is never self-describing in the encoded string
itself. A base28 string carries no marker of which profile or bit width
produced it; the same string of symbols decodes to different values under
different profiles. This is a deliberate scope boundary, not an oversight:
see section 11.

## 4. Symbol count

The payload symbol count `k` for a given bit width `n` is the smallest
integer such that `28^k >= 2^n`. Equivalently, `k = ceil(n / log2(28))`,
with `log2(28)` approximately `4.807`. Implementations should use the
precomputed table below rather than floating-point math, since floating
point rounding near an exact power boundary can produce an off-by-one `k`.

Full table for `n = 1` through `n = 128`, written as `n:k` pairs, eight per
line:

```
1:1  2:1  3:1  4:1  5:2  6:2  7:2  8:2
9:2  10:3  11:3  12:3  13:3  14:3  15:4  16:4
17:4  18:4  19:4  20:5  21:5  22:5  23:5  24:5
25:6  26:6  27:6  28:6  29:7  30:7  31:7  32:7
33:7  34:8  35:8  36:8  37:8  38:8  39:9  40:9
41:9  42:9  43:9  44:10  45:10  46:10  47:10  48:10
49:11  50:11  51:11  52:11  53:12  54:12  55:12  56:12
57:12  58:13  59:13  60:13  61:13  62:13  63:14  64:14
65:14  66:14  67:14  68:15  69:15  70:15  71:15  72:15
73:16  74:16  75:16  76:16  77:17  78:17  79:17  80:17
81:17  82:18  83:18  84:18  85:18  86:18  87:19  88:19
89:19  90:19  91:19  92:20  93:20  94:20  95:20  96:20
97:21  98:21  99:21  100:21  101:22  102:22  103:22  104:22
105:22  106:23  107:23  108:23  109:23  110:23  111:24  112:24
113:24  114:24  115:24  116:25  117:25  118:25  119:25  120:25
121:26  122:26  123:26  124:26  125:27  126:27  127:27  128:27
```

Generated with:

```python
from tools.base28ref import symbol_count
pairs = [(n, symbol_count(n)) for n in range(1, 129)]
```

## 5. Encoding

Given a value `v` and bit width `n`:

1. Compute `k = symbol_count(n)` per section 4.
2. Validate `0 <= v < 2^n`. A value outside this range cannot be
   represented at the declared bit width; reject it as `Overflow`, the
   same error class used by decoding's value check (section 6, step 6).
3. Write `v` big-endian in base 28 using the alphabet of section 2, then
   left-pad with the symbol `0` (value 0, not the letter O, which is not in
   the alphabet) to exactly `k` symbols. This is the payload.
4. Compute the Damm check symbol (section 7) over the `k` payload symbols
   and append it.

The total encoded length is `k + 1` symbols: `k` payload symbols followed
by exactly one check symbol. There is no separator between payload and
check symbol in the canonical encoded form; display grouping (section 8)
is a presentation concern layered on top.

## 6. Decoding

Decoding a candidate string `s` against a profile with bit width `n` (and
therefore `k = symbol_count(n)`) runs the following pipeline in order.
Each step is fail-loud: on failure it raises immediately with enough
information to locate the problem, and no later step runs.

1. **Normalize.** Uppercase the string; strip hyphens and whitespace.
2. **Alias.** Replace `I` and `L` with `1`; replace `O` with `0`. This is
   the only silent correction anywhere in the pipeline.
3. **Reject.** Any character remaining that is not in the 28-symbol
   alphabet is rejected, naming the character and its position (position
   counted in the normalized string, 0-indexed). `2`, `5`, `S`, `Z`, and
   `U` are recognized as excluded confusables and raise a distinct error
   subclass with a message telling the reader to re-check the source,
   rather than the generic invalid-character message.
4. **Length check.** The cleaned string must be exactly `k + 1` symbols.
   Mismatch raises with both the observed and expected length.
5. **Damm verify.** Fold all `k + 1` symbols through the Damm table
   (section 7). The fold must land on interim value 0; any other result
   raises a check-mismatch error.
6. **Value check.** Convert the first `k` symbols back to a big-endian
   base-28 integer. Because `28^k` is generally strictly greater than
   `2^n` (the table in section 4 rounds up), part of the `k`-symbol space
   encodes values `>= 2^n` that no valid encoding ever produces. If the
   decoded value is `>= 2^n`, reject as overflow; never silently truncate
   or wrap it into range.

### Error taxonomy

| Error | Raised at step | Required information |
|---|---|---|
| `InvalidCharacter` | 3 | offending character, position |
| `ExcludedConfusable` (subclass of `InvalidCharacter`) | 3 | offending character, position |
| `WrongLength` | 4 | observed length, expected length |
| `CheckMismatch` | 5 | (indicates at least one symbol is wrong; Damm alone cannot say which) |
| `Overflow` | 6 (also reachable from encoding, section 5, for out-of-range input) | decoded value, bit width |

### Why alias I/L/O but reject 2/5/S/Z

For `I`, `L`, and `O`, the partner symbols `1` and `0` are present in the
alphabet: a reader reporting `I` misread a written `1`, so the alias
target is unique and the correction is safe. For `2`, `5`, `S`, and `Z`,
both members of each confusion pair are dropped from the alphabet: none of
the four is ever written by an encoder, so a reported `S` misread some
unknown other glyph, and any alias choice would be a guess. Hard reject is
the only honest answer in that case.

## 7. Check symbol

The check symbol uses the Damm algorithm over a weak totally
antisymmetric (WTA) quasigroup of order 28. A WTA quasigroup of order 28
exists (such quasigroups exist for every order except 2 and 6).

### Construction provenance

The table is not derived from memory or literature by hand. A generation
script produces a candidate table and brute-force verifies the WTA
property over all `28^3 = 21952` triples; the verified table is then
frozen verbatim below and in `damm_table.json`. The script is kept in
`tools/` for reproducibility, but the table in this section and in
`damm_table.json` is normative; the script is not.

Construction string, copied verbatim from `damm_table.json`:

```
product-orthomorphism Z2xZ2xZ7: sigma = ([[0,1],[1,1]] on Z2^2, z->2z on Z7), T[x][y] = sigma[x + y], index i = (i//14, (i%14)//7, i%7)
```

### The table

`T[x][y]` gives the interim value after folding in a symbol of value `y`
when the running interim value is `x`. Row index is `x` (0-27, top to
bottom), column index is `y` (0-27, left to right). Each row is 28
space-separated integers:

```
0 2 4 6 1 3 5 21 23 25 27 22 24 26 7 9 11 13 8 10 12 14 16 18 20 15 17 19
2 4 6 1 3 5 0 23 25 27 22 24 26 21 9 11 13 8 10 12 7 16 18 20 15 17 19 14
4 6 1 3 5 0 2 25 27 22 24 26 21 23 11 13 8 10 12 7 9 18 20 15 17 19 14 16
6 1 3 5 0 2 4 27 22 24 26 21 23 25 13 8 10 12 7 9 11 20 15 17 19 14 16 18
1 3 5 0 2 4 6 22 24 26 21 23 25 27 8 10 12 7 9 11 13 15 17 19 14 16 18 20
3 5 0 2 4 6 1 24 26 21 23 25 27 22 10 12 7 9 11 13 8 17 19 14 16 18 20 15
5 0 2 4 6 1 3 26 21 23 25 27 22 24 12 7 9 11 13 8 10 19 14 16 18 20 15 17
21 23 25 27 22 24 26 0 2 4 6 1 3 5 14 16 18 20 15 17 19 7 9 11 13 8 10 12
23 25 27 22 24 26 21 2 4 6 1 3 5 0 16 18 20 15 17 19 14 9 11 13 8 10 12 7
25 27 22 24 26 21 23 4 6 1 3 5 0 2 18 20 15 17 19 14 16 11 13 8 10 12 7 9
27 22 24 26 21 23 25 6 1 3 5 0 2 4 20 15 17 19 14 16 18 13 8 10 12 7 9 11
22 24 26 21 23 25 27 1 3 5 0 2 4 6 15 17 19 14 16 18 20 8 10 12 7 9 11 13
24 26 21 23 25 27 22 3 5 0 2 4 6 1 17 19 14 16 18 20 15 10 12 7 9 11 13 8
26 21 23 25 27 22 24 5 0 2 4 6 1 3 19 14 16 18 20 15 17 12 7 9 11 13 8 10
7 9 11 13 8 10 12 14 16 18 20 15 17 19 0 2 4 6 1 3 5 21 23 25 27 22 24 26
9 11 13 8 10 12 7 16 18 20 15 17 19 14 2 4 6 1 3 5 0 23 25 27 22 24 26 21
11 13 8 10 12 7 9 18 20 15 17 19 14 16 4 6 1 3 5 0 2 25 27 22 24 26 21 23
13 8 10 12 7 9 11 20 15 17 19 14 16 18 6 1 3 5 0 2 4 27 22 24 26 21 23 25
8 10 12 7 9 11 13 15 17 19 14 16 18 20 1 3 5 0 2 4 6 22 24 26 21 23 25 27
10 12 7 9 11 13 8 17 19 14 16 18 20 15 3 5 0 2 4 6 1 24 26 21 23 25 27 22
12 7 9 11 13 8 10 19 14 16 18 20 15 17 5 0 2 4 6 1 3 26 21 23 25 27 22 24
14 16 18 20 15 17 19 7 9 11 13 8 10 12 21 23 25 27 22 24 26 0 2 4 6 1 3 5
16 18 20 15 17 19 14 9 11 13 8 10 12 7 23 25 27 22 24 26 21 2 4 6 1 3 5 0
18 20 15 17 19 14 16 11 13 8 10 12 7 9 25 27 22 24 26 21 23 4 6 1 3 5 0 2
20 15 17 19 14 16 18 13 8 10 12 7 9 11 27 22 24 26 21 23 25 6 1 3 5 0 2 4
15 17 19 14 16 18 20 8 10 12 7 9 11 13 22 24 26 21 23 25 27 1 3 5 0 2 4 6
17 19 14 16 18 20 15 10 12 7 9 11 13 8 24 26 21 23 25 27 22 3 5 0 2 4 6 1
19 14 16 18 20 15 17 12 7 9 11 13 8 10 26 21 23 25 27 22 24 5 0 2 4 6 1 3
```

### Weak totally antisymmetric property

`T` is a Latin square of order 28 (each row and each column is a
permutation of the values 0-27) satisfying: for all `c`, `x`, `y` in the
symbol range with `x != y`, `T[T[c][x]][y] != T[T[c][y]][x]`. Equivalently,
whenever `T[T[c][x]][y] = T[T[c][y]][x]`, `x = y` follows. The brute-force
check in the generation script verifies both the Latin-square property and
this condition over all `c, x, y` triples before the table is frozen.

### Fold and check symbol

Standard Damm fold: the interim value starts at 0. For each symbol in
sequence, look up its alphabet value and fold: `interim = T[interim][value]`.

For encoding, the check symbol appended to a `k`-symbol payload is the
symbol `c` such that `T[interim][value(c)] = 0`, where `interim` is the
fold result after all `k` payload symbols. Since each row of `T` is a
permutation of 0-27, exactly one such `c` exists.

For decoding, verification folds all `k + 1` symbols (payload followed by
check symbol) through the same table starting from interim 0; the string
is valid only if the final interim value is 0.

### Guarantees

The Damm algorithm over a WTA quasigroup catches all single-symbol errors
(one symbol replaced by a different one) and all adjacent transpositions
(two neighboring symbols swapped), the two dominant typed-back error
classes.

## 8. Profiles

A profile fixes the bit width `n` (and therefore `k`) and, optionally, a
display grouping for human-readable rendering. base28 strings are only
meaningfully decoded against an agreed profile; the encoding itself
carries no self-describing width marker (section 3).

### Profile registry

| Profile | `n` | `k` | Total (`k+1`) | Display |
|---|---|---|---|---|
| `rev45` | 45 | 10 | 11 | `XXX-XXXX-XXXX` |

### `rev45`

`rev45` is the first registered profile. Bit width `n = 45`. Payload
symbol count `k = 10` (`45 / log2(28) ~= 9.36`, rounded up to 10;
`28^10 ~= 2^48.07 > 2^45`, confirming 10 is sufficient and matches the
table in section 4). Total encoded length 11 symbols: 10 payload symbols
plus 1 Damm check symbol.

Display form groups the 11 symbols as `XXX-XXXX-XXXX` (3, then 4, then 4
symbols, hyphen-separated). Hyphens and letter case in the display form
are presentation sugar only: decoding strips hyphens and whitespace and
uppercases before any alphabet check (section 6, step 1), so
`4b4-k8nk-dg9r`, `4B4K8NKDG9R`, and `4B4-K8NK-DG9R` all decode identically.

`rev45` matches an existing live use case: an existing identifier scheme `rev` tags are
currently 9-symbol RFC 4648 base32 encodings of a 45-bit truncated
SHA-256 hash. The same entropy becomes 11 base28 symbols once the Damm
check symbol is included.

## 9. Test vectors

Also shipped machine-readable as `test-vectors.json` at the repo root;
the tables below are its exact content.

### Valid (`rev45`, `n = 45`, `k = 10`)

| Value | Encoded | Display |
|---|---|---|
| 0 | `00000000000` | `000-0000-0000` |
| 35184372088831 | `4B4K8NKDG9R` | `4B4-K8NK-DG9R` |
| 21798788025799 | `31NHYW4HGH7` | `31N-HYW4-HGH7` |
| 12388390988806 | `16R4WCVGCGY` | `16R-4WCV-GCGY` |
| 25477152372883 | `3DE77EQ3HHF` | `3DE-77EQ-3HHF` |

### Invalid (`rev45`), one per error class

| Input | Required error class |
|---|---|
| `S1NHYW4HGH7` | `ExcludedConfusable` |
| `31NHY*4HGH7` | `InvalidCharacter` |
| `31NHYW4H` | `WrongLength` |
| `31NHYW4HGH0` | `CheckMismatch` |
| `YYYYYYYYYYJ` | `Overflow` |

## 10. Design rationale

### base28 vs base30

base30 is an alternative considered and rejected during design: Crockford
minus `S` and `Z` only, keeping `5` and `2`, with decode aliases `S -> 5`
and `Z -> 2` (extending Crockford's own alias mechanism rather than
introducing hard rejects). Comparison:

- **Length is a tie at the live use case.** `28^10 ~= 2^48.1`,
  `30^10 ~= 2^49.1`: both need 10 payload symbols for 45 bits, and both
  need 27 for 128 bits. base30 saves one symbol only in narrow width
  windows (for example `n = 49`).
- **Same protection, different philosophy.** base30 silently repairs the
  common misread; base28 prevents it. base28 errors are position-specific
  and fire before check math ever runs (fail loud). base30 has a silent
  corruption path: if a third, unrelated glyph is misread as `S` or `Z`,
  the alias silently substitutes the wrong digit, and only the generic
  check-mismatch error (if any) catches it afterward.
- **base28's invariant is teachable**: "codes never contain 2, 5, S, Z" is
  printable on a form and cheap to validate client-side, with no alias
  table to reason about.
- **The door stays open.** If the sibling typeface study
  (`a typeface study.md`) shows the confusions are asymmetric (for
  example `5` proving robust in practice while `S` proves fragile), the
  profile registry and parameterized alphabet admit a base30-style
  revision without redesigning the rest of the spec.

### Relationship to the a typeface study study

The alphabet exclusions in section 2 (`2`, `5`, `S`, `Z`, plus Crockford's
existing `I`, `L`, `O`, `U`) are a design-time judgment call about which
glyph pairs are confusable enough in print and handwriting to exclude
outright rather than alias. That judgment is not backed, at v0.1, by an
empirical confusion matrix; the sibling `a typeface study` project
is where such empirical validation belongs, and it is out of scope for
this spec (section 11).

The alphabet may be revised via a new profile major version if the
empirical confusion data from that study contradicts the `2`/`5`/`S`/`Z`
exclusions made here. Any such revision changes the alphabet and
therefore the encoding for existing profiles; it does not change the
mechanism (Damm check over a WTA quasigroup, alias-then-reject decode
pipeline) defined in sections 5 through 7.

## 11. Out of scope

- General-purpose binary-to-text encoding of arbitrary byte strings.
  base28 encodes a single fixed-width unsigned integer per profile, not
  an arbitrary byte stream.
- Streaming encode or decode.
- Padding schemes beyond the fixed left-pad-to-`k` described in section 5;
  there is no variable-length or unpadded mode.
- A published library implementation. `tools/base28ref.py` is a reference
  implementation used to generate and verify the frozen artifacts in this
  repository; it is not a published package, and this spec plus
  `test-vectors.json` is the contract any future implementation is
  written against.
- Migrating an existing identifier scheme's existing `rev` tags to `rev45` encodings. That
  is a separate, later effort, blocked on this spec existing.
- Empirical confusion-matrix validation of the excluded glyph pairs. That
  work lives in the sibling `a typeface study` project; see
  section 10.
