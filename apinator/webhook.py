"""
Webhook signature verification
"""

from __future__ import annotations

import hmac
import time
from typing import Any, Mapping, Union

from .crypto import sign_webhook_payload

#: How far in the future (seconds) a webhook timestamp may be before it is
#: rejected, when ``max_age`` is given. Allows for clock skew.
MAX_FUTURE_SKEW_SECONDS = 300

HeaderValue = Union[str, list[str], tuple[str, ...], None]


def _header_value(value: Any) -> str | None:
    """Return a header value as a string; list/tuple values use the first string entry."""
    if isinstance(value, (list, tuple)):
        value = next((v for v in value if isinstance(v, str)), None)
    if isinstance(value, bytes):
        value = value.decode("latin-1")
    return value if isinstance(value, str) else None


def verify_webhook(
    secret: str,
    headers: Mapping[str, HeaderValue],
    body: str,
    max_age: int | None = None
) -> bool:
    """
    Verify a webhook signature.

    Apinator signs each delivery with the webhook endpoint's own signing secret
    (``whsec_...``, shown in the console per endpoint), not the app's API secret:
    ``X-Realtime-Signature: sha256=hex(hmac_sha256(secret, "{timestamp}.{raw_body}"))``.

    Args:
        secret: The webhook endpoint's signing secret (``whsec_...``)
        headers: HTTP headers (case-insensitive lookup; list values use the first entry)
        body: The raw webhook body as string, exactly as received
        max_age: Optional max age in seconds (300 recommended). When set,
            timestamps older than ``max_age`` or more than 300 seconds in the
            future are rejected.

    Returns:
        True if signature is valid and timestamp is fresh (if max_age provided)
    """
    # Case-insensitive header lookup
    headers_lower = {str(k).lower(): v for k, v in headers.items()}

    signature_header = _header_value(headers_lower.get('x-realtime-signature'))
    timestamp_header = _header_value(headers_lower.get('x-realtime-timestamp'))

    if not signature_header or not timestamp_header:
        return False

    # Strip "sha256=" prefix if present
    if signature_header.startswith('sha256='):
        provided_signature = signature_header[7:]
    else:
        provided_signature = signature_header

    # Verify timestamp freshness if max_age is provided
    if max_age is not None:
        try:
            timestamp = int(timestamp_header)
        except ValueError:
            return False
        age = int(time.time()) - timestamp
        if age > max_age or -age > MAX_FUTURE_SKEW_SECONDS:
            return False

    # Compute expected signature
    expected_signature = sign_webhook_payload(secret, timestamp_header, body)

    # Timing-safe comparison (compare_digest rejects non-ASCII str input)
    if not provided_signature.isascii():
        return False
    return hmac.compare_digest(expected_signature, provided_signature)
