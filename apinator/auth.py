"""
Channel authentication utilities
"""

from __future__ import annotations

from .crypto import sign_channel


def authenticate_channel(
    secret: str,
    key: str,
    socket_id: str,
    channel_name: str,
    channel_data: str | None = None
) -> dict:
    """
    Authenticate a channel subscription request.

    Args:
        secret: The API secret key
        key: The API key
        socket_id: The socket ID from the client
        channel_name: The channel name to authenticate
        channel_data: Optional channel data for presence channels

    Returns:
        Dictionary with 'auth' and optionally 'channel_data' keys
    """
    signature = sign_channel(secret, socket_id, channel_name, channel_data)
    auth = f"{key}:{signature}"

    result = {"auth": auth}
    if channel_data is not None:
        result["channel_data"] = channel_data

    return result
