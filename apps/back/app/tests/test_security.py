"""core/security 占位工具的单元测试(纯函数, 无需 DB)。"""

from app.core.security import hash_password, verify_password


def test_should_verify_correct_password() -> None:
    hashed = hash_password("s3cret")

    assert verify_password("s3cret", hashed) is True


def test_should_reject_wrong_password() -> None:
    hashed = hash_password("s3cret")

    assert verify_password("wrong", hashed) is False


def test_should_reject_malformed_hash() -> None:
    assert verify_password("s3cret", "not-a-valid-hash") is False
