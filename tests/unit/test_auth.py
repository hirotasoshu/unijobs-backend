from uuid import uuid4

from src.infra.auth import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_verifies_original_password_only():
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_access_token_round_trip_contains_user_claims(monkeypatch):
    user_id = uuid4()
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret")
    monkeypatch.setenv("AUTH_ACCESS_TOKEN_TTL_SECONDS", "3600")

    token = create_access_token(
        user_id=user_id, email="student@example.com", role="student"
    )
    claims = decode_access_token(token)

    assert claims.user_id == user_id
    assert claims.email == "student@example.com"
    assert claims.role == "student"
