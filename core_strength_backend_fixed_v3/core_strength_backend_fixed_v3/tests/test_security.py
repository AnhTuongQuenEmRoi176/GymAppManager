from app.core.security import hash_password, normalize_role, verify_password


def test_role_aliases():
    assert normalize_role("pt") == "TRAINER"
    assert normalize_role("member") == "MEMBER"
    assert normalize_role("receptionist") == "RECEPTIONIST"


def test_password_hash_roundtrip():
    password_hash = hash_password("123456")
    assert verify_password("123456", password_hash)
    assert not verify_password("wrong", password_hash)
