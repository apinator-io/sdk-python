"""
Webhook signature verification
"""

from __future__ import annotations

import hmac
import time

from .crypto import sign_webhook_payload


def verify_webhook(
    secret: str,
    headers: dict[str, str],
    body: str,
    max_age: int | None = None
) -> bool:
    """
    Verify a webhook signature.

    Args:
        secret: The webhook secret
        headers: HTTP headers (case-insensitive lookup)
        body: The webhook body as string
        max_age: Optional max age in seconds to check timestamp freshness

    Returns:
        True if signature is valid and timestamp is fresh (if max_age provided)
    """
    # Case-insensitive header lookup
    headers_lower = {k.lower(): v for k, v in headers.items()}

    signature_header = headers_lower.get('x-realtime-signature')
    timestamp_header = headers_lower.get('x-realtime-timestamp')

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
            current_time = int(time.time())
            if current_time - timestamp > max_age:
                return False
        except ValueError:
            return False

    # Compute expected signature
    expected_signature = sign_webhook_payload(secret, timestamp_header, body)

    # Timing-safe comparison
    return hmac.compare_digest(expected_signature, provided_signature)
