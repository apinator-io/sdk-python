"""
Tests for cryptographic utilities
"""

import pytest
from apinator.crypto import sign_request, sign_channel, sign_webhook_payload


# Test vectors for cross-SDK verification
TEST_SECRET = "my-secret-key"


class TestSignRequest:
    """Tests for sign_request function"""

    def test_sign_request_with_empty_body(self):
        """Empty body should result in empty body_md5"""
        signature = sign_request(
            secret=TEST_SECRET,
            method="GET",
            path="/apps/123/channels",
            body=b'',
            timestamp=1700000000
        )
        # Empty body means body_md5 is "", not hash of empty bytes
        # Expected sig_string: "1700000000\nGET\n/apps/123/channels\n"
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex digest
        # Cross-SDK verified: matches Node.js and Go
        assert signature == "ef64acd57f8011c92968cb57c875ed59c06adc5b4bc7f1aed04f739bd1856e34"

    def test_sign_request_with_body(self):
        """Request with body should include MD5 of body"""
        body = b'{"name":"test"}'
        signature = sign_request(
            secret=TEST_SECRET,
            method="POST",
            path="/apps/123/events",
            body=body,
            timestamp=1700000000
        )
        assert isinstance(signature, str)
        assert len(signature) == 64
        # This should match across SDKs
        # Cross-SDK verified: matches Node.js and Go
        assert signature == "b4e3bd1aa726fe02d0c28b4316e7e1d507d11971fea0f5cfd3cd71b101dc325c"

    def test_sign_request_different_timestamps(self):
        """Different timestamps should produce different signatures"""
        sig1 = sign_request(TEST_SECRET, "GET", "/test", b'', 1000000000)
        sig2 = sign_request(TEST_SECRET, "GET", "/test", b'', 2000000000)
        assert sig1 != sig2

    def test_sign_request_different_methods(self):
        """Different methods should produce different signatures"""
        sig1 = sign_request(TEST_SECRET, "GET", "/test", b'', 1700000000)
        sig2 = sign_request(TEST_SECRET, "POST", "/test", b'', 1700000000)
        assert sig1 != sig2

    def test_sign_request_different_paths(self):
        """Different paths should produce different signatures"""
        sig1 = sign_request(TEST_SECRET, "GET", "/test1", b'', 1700000000)
        sig2 = sign_request(TEST_SECRET, "GET", "/test2", b'', 1700000000)
        assert sig1 != sig2


class TestSignChannel:
    """Tests for sign_channel function"""

    def test_sign_channel_private(self):
        """Sign private channel without channel_data"""
        signature = sign_channel(
            secret=TEST_SECRET,
            socket_id="12345.67890",
            channel_name="private-chat"
        )
        assert isinstance(signature, str)
        assert len(signature) == 64
        # Cross-SDK verified: matches Node.js and Go
        assert signature == "a938cf2c05ce33130efb37b4b730d4e3c0a5bef21ce68604d87684efdcb68ec3"

    def test_sign_channel_with_channel_data(self):
        """Sign presence channel with channel_data"""
        signature = sign_channel(
            secret=TEST_SECRET,
            socket_id="12345.67890",
            channel_name="presence-chat",
            channel_data='{"user_id":"user1"}'
        )
        assert isinstance(signature, str)
        assert len(signature) == 64
        # Cross-SDK verified: matches Node.js and Go
        assert signature == "34138811c35c4adda7a7e76f03ce5d54908df7d2b51748081b405a8df4f1a217"

    def test_sign_channel_different_socket_ids(self):
        """Different socket IDs should produce different signatures"""
        sig1 = sign_channel(TEST_SECRET, "111.111", "private-test")
        sig2 = sign_channel(TEST_SECRET, "222.222", "private-test")
        assert sig1 != sig2

    def test_sign_channel_different_channels(self):
        """Different channels should produce different signatures"""
        sig1 = sign_channel(TEST_SECRET, "12345.67890", "private-chat1")
        sig2 = sign_channel(TEST_SECRET, "12345.67890", "private-chat2")
        assert sig1 != sig2

    def test_sign_channel_with_and_without_data(self):
        """Same channel with/without data should produce different signatures"""
        sig1 = sign_channel(TEST_SECRET, "12345.67890", "presence-chat")
        sig2 = sign_channel(TEST_SECRET, "12345.67890", "presence-chat", '{"user_id":"user1"}')
        assert sig1 != sig2


class TestSignWebhookPayload:
    """Tests for sign_webhook_payload function"""

    def test_sign_webhook_payload(self):
        """Sign webhook payload"""
        signature = sign_webhook_payload(
            secret=TEST_SECRET,
            timestamp="1700000000",
            payload='{"event":"channel_occupied","channel":"test"}'
        )
        assert isinstance(signature, str)
        assert len(signature) == 64
        # Cross-SDK verified: matches Node.js and Go
        assert signature == "79bbc868f72034bf5d7ea77727d6c705f0edc6de24bdcb51dd52ca05c11617f8"

    def test_sign_webhook_payload_different_timestamps(self):
        """Different timestamps should produce different signatures"""
        sig1 = sign_webhook_payload(TEST_SECRET, "1700000000", '{"test":"data"}')
        sig2 = sign_webhook_payload(TEST_SECRET, "1700000001", '{"test":"data"}')
        assert sig1 != sig2

    def test_sign_webhook_payload_different_payloads(self):
        """Different payloads should produce different signatures"""
        sig1 = sign_webhook_payload(TEST_SECRET, "1700000000", '{"test":"data1"}')
        sig2 = sign_webhook_payload(TEST_SECRET, "1700000000", '{"test":"data2"}')
        assert sig1 != sig2

    def test_sign_webhook_payload_empty_payload(self):
        """Empty payload should still produce valid signature"""
        signature = sign_webhook_payload(TEST_SECRET, "1700000000", "")
        assert isinstance(signature, str)
        assert len(signature) == 64
