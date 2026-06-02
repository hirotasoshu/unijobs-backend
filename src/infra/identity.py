from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Request, status

from src.domain.value_object.ids import UserId
from src.infra.auth import InvalidTokenError, decode_access_token


@dataclass(frozen=True)
class CurrentUser:
    id: UserId
    email: str
    role: str


class IdentityProvider:
    def current_user(self) -> CurrentUser:
        raise NotImplementedError


class RequestIdentityProvider(IdentityProvider):
    def __init__(self, request: Request):
        self.request = request

    def current_user(self) -> CurrentUser:
        authorization = self.request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        try:
            claims = decode_access_token(authorization.removeprefix("Bearer "))
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            ) from exc

        return CurrentUser(
            id=UserId(UUID(str(claims.user_id))),
            email=claims.email,
            role=claims.role,
        )
