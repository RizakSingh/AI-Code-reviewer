"""
Issues and verifies session JWTs. The raw GitHub OAuth token is never
handed to the browser - after login we mint our own short-lived session
token instead, so a leaked frontend token can't be used to act as the
user on GitHub's API directly.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import get_settings

settings = get_settings()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Returns the user id encoded in the token. Raises jose.JWTError on an
    invalid/expired token or ValueError if the subject isn't an int - callers
    should treat both as "not authenticated"."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    return int(payload["sub"])
