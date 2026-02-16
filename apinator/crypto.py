"""
Cryptographic utilities for HMAC signing
"""

from __future__ import annotations

import hmac
import hashlib


def sign_request(
    secret: str,
    method: str,
    path: str,
    body: bytes,
    timestamp: int
) -> str:
    """
    Sign an API request using HMAC-SHA256.

    Args:
        secret: The API secret key
        method: HTTP method (e.g., "POST", "GET")
        path: Request path (e.g., "/apps/123/events")
        body: Request body as bytes
        timestamp: Unix timestamp

    Returns:
        HMAC-SHA256 hex digest
    """
    # Important: empty body means body_md5 is empty string, not hash of empty bytes
    if len(body) == 0:
        body_md5 = ""
    else:
        body_md5 = hashlib.md5(body).hexdigest()

    # Format: {timestamp}\n{method}\n{path}\n{body_md5}
    sig_string = f"{timestamp}\n{method}\n{path}\n{body_md5}"

    return hmac.new(
        secret.encode('utf-8'),
        sig_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def sign_channel(
    secret: str,
    socket_id: str,
    channel_name: str,
    channel_data: str | None = None
) -> str:
    """
    Sign a channel authentication request using HMAC-SHA256.

    Args:
        secret: The API secret key
        socket_id: The socket ID from the client
        channel_name: The channel name to authenticate
        channel_data: Optional channel data for presence channels

    Returns:
        HMAC-SHA256 hex digest
    """
    if channel_data is None:
        sig_string = f"{socket_id}:{channel_name}"
    else:
        sig_string = f"{socket_id}:{channel_name}:{channel_data}"

    return hmac.new(
        secret.encode('utf-8'),
        sig_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def sign_webhook_payload(
    secret: str,
    timestamp: str,
    payload: str
) -> str:
    """
    Sign a webhook payload using HMAC-SHA256.

    Args:
        secret: The webhook secret
        timestamp: The timestamp from the webhook header
        payload: The webhook body

    Returns:
        HMAC-SHA256 hex digest
    """
    sig_string = f"{timestamp}.{payload}"

    return hmac.new(
        secret.encode('utf-8'),
        sig_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
