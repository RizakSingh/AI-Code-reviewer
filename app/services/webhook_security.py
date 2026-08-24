"""
GitHub signs each webhook payload with HMAC-SHA256 using the shared
webhook secret. We MUST verify this before trusting the payload,
otherwise anyone could POST fake PR events to our endpoint.
"""
import hmac
import hashlib


def verify_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = "sha256=" + hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # constant-time comparison - avoids timing attacks on the signature check
    return hmac.compare_digest(expected, signature_header)
