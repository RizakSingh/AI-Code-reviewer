from typing import Optional

from fastapi import Cookie, Depends, Header, HTTPException
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token

SESSION_COOKIE_NAME = "access_token"


def get_current_user(
    access_token: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    # Cookie is how the frontend authenticates; Bearer header is kept as a
    # fallback for non-browser API clients (scripts, tests).
    token = access_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):]

    if not token:
        raise HTTPException(401, "Not authenticated")

    try:
        user_id = decode_access_token(token)
    except (JWTError, ValueError):
        raise HTTPException(401, "Invalid or expired session")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User no longer exists")

    return user
