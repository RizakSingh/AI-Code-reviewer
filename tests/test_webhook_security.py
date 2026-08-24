import hmac
import hashlib

from app.services.webhook_security import verify_signature


SECRET = "test_webhook_secret"


def sign(payload: bytes, secret: str = SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def test_valid_signature_passes():
    payload = b'{"action": "opened"}'
    signature = sign(payload)
    assert verify_signature(payload, signature, SECRET) is True


def test_tampered_payload_fails():
    payload = b'{"action": "opened"}'
    signature = sign(payload)
    tampered_payload = b'{"action": "closed"}'
    assert verify_signature(tampered_payload, signature, SECRET) is False


def test_wrong_secret_fails():
    payload = b'{"action": "opened"}'
    signature = sign(payload, secret="wrong_secret")
    assert verify_signature(payload, signature, SECRET) is False


def test_missing_signature_fails():
    payload = b'{"action": "opened"}'
    assert verify_signature(payload, "", SECRET) is False
    assert verify_signature(payload, None, SECRET) is False


def test_malformed_signature_header_fails():
    payload = b'{"action": "opened"}'
    assert verify_signature(payload, "not-sha256-format", SECRET) is False
