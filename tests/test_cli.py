import pytest

from base28.cli import main

KNOWN_VALUE = "2832504837759"
KNOWN_DISPLAY = "09F-WWAH-NMTK"
KNOWN_COMPACT = "09FWWAHNMTK"


def test_encode_default_is_grouped_rev45(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", KNOWN_VALUE]) == 0
    assert capsys.readouterr().out.strip() == KNOWN_DISPLAY


def test_encode_compact(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", KNOWN_VALUE, "--compact"]) == 0
    assert capsys.readouterr().out.strip() == KNOWN_COMPACT


def test_encode_generic_bits_is_ungrouped(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", "0", "--bits", "45"]) == 0
    # --bits set at all switches to the generic (ungrouped) form.
    assert capsys.readouterr().out.strip() == "00000000000"


def test_decode_roundtrips(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["decode", "09f-wwah-nmtk"]) == 0
    assert capsys.readouterr().out.strip() == KNOWN_VALUE


def test_verify_succeeds(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["verify"]) == 0
    assert "verified independently" in capsys.readouterr().out


def test_decode_error_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["decode", "SSSSSSSSSSS"]) == 2
    assert "error:" in capsys.readouterr().err


def test_encode_overflow_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", str(2**45)]) == 2
    assert "error:" in capsys.readouterr().err
