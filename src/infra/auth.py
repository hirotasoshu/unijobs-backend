from dataclasses import dataclass
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from uuid import UUID

from src.domain.value_object.ids import UserId


@dataclass(frozen=True)
class AuthClaims:
    user_id: UserId
    email: str
    role: str


class InvalidTokenError(Exception):
    pass


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _jwt_secret() -> str:
    return os.getenv("AUTH_JWT_SECRET", "dev-only-change-me")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 390000)
    return f"pbkdf2_sha256${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt_b64, digest_b64 = password_hash.split("$", 2)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    salt = _b64url_decode(salt_b64)
    expected = _b64url_decode(digest_b64)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 390000)
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: UUID, email: str, role: str) -> str:
    now = int(time.time())
    ttl = int(os.getenv("AUTH_ACCESS_TOKEN_TTL_SECONDS", "86400"))
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": os.getenv("AUTH_JWT_ISSUER", "unijobs"),
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + ttl,
    }
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode()),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(
        _jwt_secret().encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> AuthClaims:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise InvalidTokenError from exc

    signing_input = f"{header_b64}.{payload_b64}"
    expected_signature = hmac.new(
        _jwt_secret().encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    actual_signature = _b64url_decode(signature_b64)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise InvalidTokenError

    payload = json.loads(_b64url_decode(payload_b64))
    if int(payload["exp"]) < int(time.time()):
        raise InvalidTokenError

    return AuthClaims(
        user_id=UserId(UUID(payload["sub"])),
        email=payload["email"],
        role=payload.get("role", "student"),
    )
