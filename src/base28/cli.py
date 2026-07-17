"""Command-line interface: ``base28 encode | decode | verify``.

Defaults to the rev45 profile, the common case. ``--bits`` switches encode and
decode to the generic width mechanism and prints the ungrouped form.
"""

import argparse
import sys
from collections.abc import Sequence

from base28 import _core, _verify, rev45
from base28.errors import Base28Error


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="base28", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_encode = sub.add_parser("encode", help="integer -> base28 code")
    _ = p_encode.add_argument("value", type=int, help="non-negative integer to encode")
    _ = p_encode.add_argument(
        "--bits",
        type=int,
        default=None,
        help=f"generic bit width (default: the rev45 profile, {rev45.BITS} bits)",
    )
    _ = p_encode.add_argument(
        "--compact",
        action="store_true",
        help="omit the rev45 group separators (no effect when --bits is set)",
    )

    p_decode = sub.add_parser("decode", help="base28 code -> integer")
    _ = p_decode.add_argument("code", help="base28 code (grouped or compact)")
    _ = p_decode.add_argument(
        "--bits",
        type=int,
        default=None,
        help=f"generic bit width (default: the rev45 profile, {rev45.BITS} bits)",
    )

    _ = sub.add_parser("verify", help="re-check the frozen test vectors")
    return parser


def _cmd_encode(value: int, bits: int | None, compact: bool) -> int:
    if bits is None:
        print(rev45.encode_compact(value) if compact else rev45.encode(value))
    else:
        print(_core.encode(value, bits))
    return 0


def _cmd_decode(code: str, bits: int | None) -> int:
    print(_core.decode(code, rev45.BITS if bits is None else bits))
    return 0


def _cmd_verify() -> int:
    result = _verify.verify()
    if result.ok:
        print(
            f"all {result.valid_checked} valid and {result.invalid_checked} "
            "invalid vectors verified independently"
        )
        return 0
    for failure in result.failures:
        print(failure, file=sys.stderr)
    print(f"{len(result.failures)} failures", file=sys.stderr)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "encode":
            return _cmd_encode(args.value, args.bits, args.compact)
        if args.command == "decode":
            return _cmd_decode(args.code, args.bits)
        if args.command == "verify":
            return _cmd_verify()
    except (Base28Error, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command {args.command!r}")  # unreachable; required=True


if __name__ == "__main__":
    sys.exit(main())
