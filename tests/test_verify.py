from base28 import _verify


def test_frozen_vectors_verify_independently() -> None:
    result = _verify.verify()
    assert result.ok, result.failures
    assert result.valid_checked == 5
    assert result.invalid_checked == 5
