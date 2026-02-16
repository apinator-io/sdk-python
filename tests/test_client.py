"""
Tests for Apinator client
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from urllib.error import HTTPError, URLError
from io import BytesIO

from apinator import Apinator
from apinator.errors import ValidationError, AuthenticationError, ApiError


TEST_APP_ID = "test-app-123"
TEST_KEY = "test-key"
TEST_SECRET = "test-secret"
TEST_CLUSTER = "eu"


class TestApinatorClient:
    """Tests for Apinator client initialization"""

    def test_client_initialization(self):
        """Client should initialize with correct attributes"""
        client = Apinator(
            app_id=TEST_APP_ID,
            key=TEST_KEY,
            secret=TEST_SECRET,
            cluster=TEST_CLUSTER,
        )

        assert client.app_id == TEST_APP_ID
        assert client.key == TEST_KEY
        assert client.secret == TEST_SECRET
        assert client.host == "https://ws-eu.apinator.io"

    def test_cluster_eu_derives_url(self):
        """Client should derive host URL from eu cluster"""
        client = Apinator(
            app_id=TEST_APP_ID,
            key=TEST_KEY,
            secret=TEST_SECRET,
            cluster="eu",
        )

        assert client.host == "https://ws-eu.apinator.io"

    def test_cluster_us_derives_url(self):
        """Client should derive host URL from us cluster"""
        client = Apinator(
            app_id=TEST_APP_ID,
            key=TEST_KEY,
            secret=TEST_SECRET,
            cluster="us",
        )

        assert client.host == "https://ws-us.apinator.io"


class TestTrigger:
    """Tests for trigger method"""

    def test_trigger_single_channel(self):
        """Trigger should send event to single channel"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            client.trigger("message", '{"text":"Hello"}', channel="chat")

            # Verify request was made
            assert mock_urlopen.called
            call_args = mock_urlopen.call_args
            request = call_args[0][0]

            assert request.get_method() == "POST"
            assert f"/apps/{TEST_APP_ID}/events" in request.full_url
            assert request.get_header('Content-type') == 'application/json'
            assert request.get_header('X-realtime-key') == TEST_KEY

            # Verify body
            body = json.loads(request.data.decode('utf-8'))
            assert body["name"] == "message"
            assert body["data"] == '{"text":"Hello"}'
            assert body["channel"] == "chat"

    def test_trigger_multiple_channels(self):
        """Trigger should send event to multiple channels"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            client.trigger("message", '{"text":"Hello"}', channels=["chat", "notifications"])

            request = mock_urlopen.call_args[0][0]
            body = json.loads(request.data.decode('utf-8'))
            assert body["channels"] == ["chat", "notifications"]

    def test_trigger_with_socket_id(self):
        """Trigger should include socket_id when provided"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            client.trigger(
                "message",
                '{"text":"Hello"}',
                channel="chat",
                socket_id="12345.67890"
            )

            request = mock_urlopen.call_args[0][0]
            body = json.loads(request.data.decode('utf-8'))
            assert body["socket_id"] == "12345.67890"

    def test_trigger_validation_both_channel_and_channels(self):
        """Trigger should raise ValidationError if both channel and channels provided"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with pytest.raises(ValidationError) as exc_info:
            client.trigger(
                "message",
                '{"text":"Hello"}',
                channel="chat",
                channels=["notifications"]
            )

        assert "Cannot specify both" in str(exc_info.value)

    def test_trigger_validation_neither_channel_nor_channels(self):
        """Trigger should raise ValidationError if neither channel nor channels provided"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with pytest.raises(ValidationError) as exc_info:
            client.trigger("message", '{"text":"Hello"}')

        assert "Must specify either" in str(exc_info.value)

    def test_trigger_http_error(self):
        """Trigger should raise AuthenticationError on 401 RFC 7807 response"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            error_response = BytesIO(
                b'{"type":"https://docs.apinator.io/problems/unauthorized","title":"Unauthorized","status":401,"detail":"Unauthorized","code":"unauthorized"}'
            )
            mock_urlopen.side_effect = HTTPError(
                "http://example.com", 401, "Unauthorized", {}, error_response
            )

            with pytest.raises(AuthenticationError) as exc_info:
                client.trigger("message", '{"text":"Hello"}', channel="chat")

            assert "Unauthorized" in str(exc_info.value)

    def test_trigger_network_error(self):
        """Trigger should raise ApiError on network error"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = URLError("Connection refused")

            with pytest.raises(ApiError) as exc_info:
                client.trigger("message", '{"text":"Hello"}', channel="chat")

            assert exc_info.value.status == 0
            assert "Network error" in str(exc_info.value)


class TestGetChannels:
    """Tests for get_channels method"""

    def test_get_channels(self):
        """get_channels should return list of channels"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "channels": [
                    {"name": "chat", "subscription_count": 5},
                    {"name": "notifications", "subscription_count": 10}
                ]
            }).encode('utf-8')
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            channels = client.get_channels()

            assert len(channels) == 2
            assert channels[0]["name"] == "chat"
            assert channels[1]["name"] == "notifications"

            # Verify request
            request = mock_urlopen.call_args[0][0]
            assert request.get_method() == "GET"
            assert f"/apps/{TEST_APP_ID}/channels" in request.full_url

    def test_get_channels_with_prefix(self):
        """get_channels should include prefix query parameter"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"channels":[]}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            client.get_channels(prefix="private-")

            request = mock_urlopen.call_args[0][0]
            assert "filter_by_prefix=private-" in request.full_url

    def test_get_channels_empty_response(self):
        """get_channels should return empty list for empty response"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"channels":[]}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            channels = client.get_channels()
            assert channels == []


class TestGetChannel:
    """Tests for get_channel method"""

    def test_get_channel(self):
        """get_channel should return channel info"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "name": "chat",
                "subscription_count": 5
            }).encode('utf-8')
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            channel = client.get_channel("chat")

            assert channel["name"] == "chat"
            assert channel["subscription_count"] == 5

            # Verify request
            request = mock_urlopen.call_args[0][0]
            assert request.get_method() == "GET"
            assert f"/apps/{TEST_APP_ID}/channels/chat" in request.full_url

    def test_get_channel_url_encoding(self):
        """get_channel should URL encode channel name"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"name":"private-chat room"}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            client.get_channel("private-chat room")

            request = mock_urlopen.call_args[0][0]
            # Space should be encoded
            assert "private-chat%20room" in request.full_url


class TestAuthenticateChannel:
    """Tests for authenticate_channel method"""

    def test_authenticate_channel(self):
        """authenticate_channel should return auth response"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        result = client.authenticate_channel(
            socket_id="12345.67890",
            channel_name="private-chat"
        )

        assert "auth" in result
        assert result["auth"].startswith(f"{TEST_KEY}:")

    def test_authenticate_channel_with_data(self):
        """authenticate_channel should include channel_data"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        result = client.authenticate_channel(
            socket_id="12345.67890",
            channel_name="presence-chat",
            channel_data='{"user_id":"user1"}'
        )

        assert "auth" in result
        assert "channel_data" in result
        assert result["channel_data"] == '{"user_id":"user1"}'


class TestVerifyWebhook:
    """Tests for verify_webhook method"""

    def test_verify_webhook(self):
        """verify_webhook should verify signature"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        # Create valid signature
        from apinator.crypto import sign_webhook_payload
        timestamp = "1700000000"
        body = '{"event":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        assert client.verify_webhook(headers, body) is True

    def test_verify_webhook_invalid(self):
        """verify_webhook should reject invalid signature"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        headers = {
            "X-Realtime-Signature": "invalid",
            "X-Realtime-Timestamp": "1700000000"
        }

        assert client.verify_webhook(headers, '{"event":"test"}') is False


class TestRequestSigning:
    """Tests for request signing"""

    def test_request_includes_auth_headers(self):
        """Requests should include authentication headers"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"channels":[]}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            client.get_channels()

            request = mock_urlopen.call_args[0][0]
            assert request.get_header('X-realtime-key') == TEST_KEY
            assert request.has_header('X-realtime-timestamp')
            assert request.has_header('X-realtime-signature')

    def test_request_signature_changes_with_body(self):
        """Request signature should differ based on body"""
        client = Apinator(TEST_APP_ID, TEST_KEY, TEST_SECRET, cluster=TEST_CLUSTER)

        signatures = []

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            # First request
            with patch('time.time', return_value=1700000000):
                client.trigger("event1", '{"data":"test1"}', channel="chat")
                signatures.append(mock_urlopen.call_args[0][0].get_header('X-realtime-signature'))

            # Second request with different body
            with patch('time.time', return_value=1700000000):
                client.trigger("event2", '{"data":"test2"}', channel="chat")
                signatures.append(mock_urlopen.call_args[0][0].get_header('X-realtime-signature'))

        # Signatures should be different
        assert signatures[0] != signatures[1]
