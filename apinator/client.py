"""
Apinator client for server-side operations
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from typing import Any
from urllib.parse import quote, urlencode

from .crypto import sign_request
from .auth import authenticate_channel as auth_channel
from .webhook import verify_webhook as verify_webhook_signature
from .errors import ValidationError, AuthenticationError, ApiError


class Apinator:
    """
    Apinator server SDK client.

    Example:
        client = Apinator(
            app_id="123",
            key="my-key",
            secret="my-secret",
            cluster="eu",  # or "us"
        )
        client.trigger("message", '{"text":"Hello"}', channel="chat")
    """

    def __init__(
        self,
        app_id: str,
        key: str,
        secret: str,
        cluster: str,
    ):
        """
        Initialize Apinator client.

        Args:
            app_id: Application ID
            key: API key
            secret: API secret
            cluster: Cluster region identifier (e.g. "eu", "us")
        """
        self.app_id = app_id
        self.key = key
        self.secret = secret
        self.host = f"https://ws-{cluster}.apinator.io"

    def trigger(
        self,
        name: str,
        data: str,
        *,
        channel: str | None = None,
        channels: list[str] | None = None,
        socket_id: str | None = None
    ) -> None:
        """
        Trigger an event to one or more channels.

        Args:
            name: Event name
            data: Event data as JSON string
            channel: Single channel name (mutually exclusive with channels)
            channels: List of channel names (mutually exclusive with channel)
            socket_id: Optional socket ID to exclude from broadcast

        Raises:
            ValidationError: If both channel and channels are provided or neither
            ApiError: If the API request fails
        """
        if channel and channels:
            raise ValidationError("Cannot specify both 'channel' and 'channels'")
        if not channel and not channels:
            raise ValidationError("Must specify either 'channel' or 'channels'")

        payload: dict[str, Any] = {
            "name": name,
            "data": data,
        }

        if channel:
            payload["channel"] = channel
        if channels:
            payload["channels"] = channels
        if socket_id:
            payload["socket_id"] = socket_id

        path = f"/apps/{self.app_id}/events"
        self._request("POST", path, payload)

    def authenticate_channel(
        self,
        socket_id: str,
        channel_name: str,
        channel_data: str | None = None
    ) -> dict:
        """
        Authenticate a channel subscription request.

        Args:
            socket_id: Socket ID from the client
            channel_name: Channel name to authenticate
            channel_data: Optional channel data for presence channels

        Returns:
            Dictionary with 'auth' and optionally 'channel_data' keys
        """
        return auth_channel(self.secret, self.key, socket_id, channel_name, channel_data)

    def get_channels(self, prefix: str | None = None) -> list[dict]:
        """
        Get list of active channels.

        Args:
            prefix: Optional prefix filter for channel names

        Returns:
            List of channel info dictionaries

        Raises:
            ApiError: If the API request fails
        """
        path = f"/apps/{self.app_id}/channels"
        if prefix:
            path += f"?{urlencode({'filter_by_prefix': prefix})}"

        response = self._request("GET", path)
        return response.get("channels", [])

    def get_channel(self, channel_name: str) -> dict:
        """
        Get information about a specific channel.

        Args:
            channel_name: Channel name

        Returns:
            Channel info dictionary

        Raises:
            ApiError: If the API request fails
        """
        # URL encode channel name to handle special characters
        encoded_name = quote(channel_name, safe='')
        path = f"/apps/{self.app_id}/channels/{encoded_name}"
        return self._request("GET", path)

    def verify_webhook(
        self,
        headers: dict[str, str],
        body: str,
        max_age: int | None = None
    ) -> bool:
        """
        Verify a webhook signature.

        Args:
            headers: HTTP headers from webhook request
            body: Webhook body as string
            max_age: Optional max age in seconds

        Returns:
            True if signature is valid
        """
        return verify_webhook_signature(self.secret, headers, body, max_age)

    def _request(
        self,
        method: str,
        path: str,
        body: dict | None = None
    ) -> dict:
        """
        Make an authenticated HTTP request to the API.

        Args:
            method: HTTP method
            path: Request path
            body: Optional request body dictionary

        Returns:
            Parsed JSON response

        Raises:
            ApiError: If the request fails
        """
        url = f"{self.host}{path}"
        timestamp = int(time.time())

        # Prepare body
        if body is not None:
            body_bytes = json.dumps(body).encode('utf-8')
        else:
            body_bytes = b''

        # Sign request
        canonical_path = path.split('?', 1)[0]
        signature = sign_request(self.secret, method, canonical_path, body_bytes, timestamp)

        # Prepare request
        req = urllib.request.Request(
            url,
            data=body_bytes if len(body_bytes) > 0 else None,
            method=method
        )

        # Set headers
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Realtime-Key', self.key)
        req.add_header('X-Realtime-Timestamp', str(timestamp))
        req.add_header('X-Realtime-Signature', signature)

        # Execute request
        try:
            with urllib.request.urlopen(req) as response:
                response_body = response.read().decode('utf-8')
                if len(response_body) > 0:
                    return json.loads(response_body)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else None
            message = f"API request failed: {e.reason}"
            if error_body:
                try:
                    problem = json.loads(error_body)
                    if isinstance(problem, dict):
                        detail = problem.get('detail')
                        title = problem.get('title')
                        if isinstance(detail, str) and detail:
                            message = detail
                        elif isinstance(title, str) and title:
                            message = title
                except json.JSONDecodeError:
                    pass

            if e.code in (401, 403):
                raise AuthenticationError(message)
            if e.code in (400, 422):
                raise ValidationError(message)

            raise ApiError(message, status=e.code, body=error_body)
        except urllib.error.URLError as e:
            raise ApiError(f"Network error: {e.reason}", status=0)
        except json.JSONDecodeError as e:
            raise ApiError(f"Invalid JSON response: {e}", status=0)
