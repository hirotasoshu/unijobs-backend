from types import SimpleNamespace
from uuid import uuid4

from src.infra.auth import create_access_token
from src.infra.identity import RequestIdentityProvider


def test_reads_current_user_from_authorization_header(monkeypatch):
    user_id = uuid4()
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret")
    monkeypatch.setenv("AUTH_ACCESS_TOKEN_TTL_SECONDS", "3600")
    token = create_access_token(
        user_id=user_id, email="student@example.com", role="student"
    )
    request = SimpleNamespace(headers={"authorization": f"Bearer {token}"})

    user = RequestIdentityProvider(request).current_user()

    assert user.id == user_id
    assert user.email == "student@example.com"
    assert user.role == "student"
