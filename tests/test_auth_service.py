import pytest
from jose import jwt

from app.services import auth_service


def test_create_and_decode_round_trips_user_id():
    token = auth_service.create_access_token(42)
    assert auth_service.decode_access_token(token) == 42


def test_decode_rejects_tampered_token():
    token = auth_service.create_access_token(1)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(Exception):
        auth_service.decode_access_token(tampered)


def test_decode_rejects_expired_token():
    from datetime import datetime, timedelta, timezone

    expired_payload = {
        "sub": "7",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    from app.config import get_settings

    settings = get_settings()
    expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm=auth_service.ALGORITHM)

    with pytest.raises(Exception):
        auth_service.decode_access_token(expired_token)
