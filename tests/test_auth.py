"""
Tests for channel authentication
"""

import pytest
from apinator.auth import authenticate_channel


TEST_SECRET = "my-secret-key"
TEST_KEY = "my-api-key"


class TestAuthenticateChannel:
    """Tests for authenticate_channel function"""

    def test_authenticate_private_channel(self):
        """Authenticate private channel without channel_data"""
        result = authenticate_channel(
            secret=TEST_SECRET,
            key=TEST_KEY,
            socket_id="12345.67890",
            channel_name="private-chat"
        )

        assert isinstance(result, dict)
        assert "auth" in result
        assert result["auth"].startswith(f"{TEST_KEY}:")
        assert "channel_data" not in result

        # Extract signature part
        auth_parts = result["auth"].split(":", 1)
        assert len(auth_parts) == 2
        assert auth_parts[0] == TEST_KEY
        assert len(auth_parts[1]) == 64  # SHA256 hex

    def test_authenticate_presence_channel_with_data(self):
        """Authenticate presence channel with channel_data"""
        channel_data = '{"user_id":"user1","user_info":{"name":"John"}}'
        result = authenticate_channel(
            secret=TEST_SECRET,
            key=TEST_KEY,
            socket_id="12345.67890",
            channel_name="presence-chat",
            channel_data=channel_data
        )

        assert isinstance(result, dict)
        assert "auth" in result
        assert "channel_data" in result
        assert result["channel_data"] == channel_data
        assert result["auth"].startswith(f"{TEST_KEY}:")

    def test_authenticate_channel_format(self):
        """Verify auth format is key:signature"""
        result = authenticate_channel(
            TEST_SECRET, TEST_KEY, "socket.id", "private-test"
        )

        auth = result["auth"]
        assert auth.count(":") == 1
        key, signature = auth.split(":")
        assert key == TEST_KEY
        assert len(signature) == 64

    def test_authenticate_different_socket_ids(self):
        """Different socket IDs should produce different signatures"""
        result1 = authenticate_channel(
            TEST_SECRET, TEST_KEY, "111.111", "private-test"
        )
        result2 = authenticate_channel(
            TEST_SECRET, TEST_KEY, "222.222", "private-test"
        )

        assert result1["auth"] != result2["auth"]

    def test_authenticate_different_channels(self):
        """Different channels should produce different signatures"""
        result1 = authenticate_channel(
            TEST_SECRET, TEST_KEY, "12345.67890", "private-chat1"
        )
        result2 = authenticate_channel(
            TEST_SECRET, TEST_KEY, "12345.67890", "private-chat2"
        )

        assert result1["auth"] != result2["auth"]

    def test_authenticate_with_and_without_data(self):
        """Same channel with/without data should produce different signatures"""
        result1 = authenticate_channel(
            TEST_SECRET, TEST_KEY, "12345.67890", "presence-chat"
        )
        result2 = authenticate_channel(
            TEST_SECRET, TEST_KEY, "12345.67890", "presence-chat", '{"user_id":"user1"}'
        )

        assert result1["auth"] != result2["auth"]
        assert "channel_data" not in result1
        assert "channel_data" in result2

    def test_authenticate_none_channel_data(self):
        """Explicitly passing None for channel_data should omit it from result"""
        result = authenticate_channel(
            TEST_SECRET, TEST_KEY, "socket.id", "presence-test", None
        )

        assert "channel_data" not in result

    def test_authenticate_empty_string_channel_data(self):
        """Empty string channel_data should be included in result"""
        result = authenticate_channel(
            TEST_SECRET, TEST_KEY, "socket.id", "presence-test", ""
        )

        assert "channel_data" in result
        assert result["channel_data"] == ""
