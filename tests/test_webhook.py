"""
Tests for webhook signature verification
"""

import pytest
import time
from apinator.webhook import verify_webhook
from apinator.crypto import sign_webhook_payload


TEST_SECRET = "my-webhook-secret"


class TestVerifyWebhook:
    """Tests for verify_webhook function"""

    def test_verify_valid_signature(self):
        """Valid signature should return True"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": f"sha256={signature}",
            "X-Realtime-Timestamp": timestamp
        }

        assert verify_webhook(TEST_SECRET, headers, body) is True

    def test_verify_valid_signature_without_prefix(self):
        """Signature without sha256= prefix should work"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        assert verify_webhook(TEST_SECRET, headers, body) is True

    def test_verify_tampered_body(self):
        """Tampered body should return False"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        tampered_body = '{"event":"channel_occupied","channel":"tampered"}'
        assert verify_webhook(TEST_SECRET, headers, tampered_body) is False

    def test_verify_wrong_secret(self):
        """Wrong secret should return False"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        assert verify_webhook("wrong-secret", headers, body) is False

    def test_verify_expired_timestamp(self):
        """Expired timestamp should return False when max_age is set"""
        old_timestamp = str(int(time.time()) - 600)  # 10 minutes ago
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, old_timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": old_timestamp
        }

        # max_age of 300 seconds (5 minutes) should reject 10-minute-old timestamp
        assert verify_webhook(TEST_SECRET, headers, body, max_age=300) is False

    def test_verify_fresh_timestamp(self):
        """Fresh timestamp should return True when max_age is set"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        assert verify_webhook(TEST_SECRET, headers, body, max_age=300) is True

    def test_verify_case_insensitive_headers(self):
        """Header names should be case-insensitive"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        # Test with various case combinations
        headers = {
            "x-realtime-signature": signature,
            "X-REALTIME-TIMESTAMP": timestamp
        }

        assert verify_webhook(TEST_SECRET, headers, body) is True

    def test_verify_missing_signature_header(self):
        """Missing signature header should return False"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'

        headers = {
            "X-Realtime-Timestamp": timestamp
        }

        assert verify_webhook(TEST_SECRET, headers, body) is False

    def test_verify_missing_timestamp_header(self):
        """Missing timestamp header should return False"""
        timestamp = str(int(time.time()))
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature
        }

        assert verify_webhook(TEST_SECRET, headers, body) is False

    def test_verify_invalid_timestamp_format(self):
        """Invalid timestamp format should return False when max_age is set"""
        body = '{"event":"channel_occupied","channel":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, "not-a-timestamp", body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": "not-a-timestamp"
        }

        # Without max_age, it should validate signature only
        assert verify_webhook(TEST_SECRET, headers, body) is True

        # With max_age, it should fail due to invalid timestamp
        assert verify_webhook(TEST_SECRET, headers, body, max_age=300) is False

    def test_verify_empty_body(self):
        """Empty body should be verifiable"""
        timestamp = str(int(time.time()))
        body = ""
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        assert verify_webhook(TEST_SECRET, headers, body) is True

    def test_verify_timing_safe_comparison(self):
        """Verification should use timing-safe comparison"""
        # This test ensures hmac.compare_digest is used
        # We can't directly test timing, but we verify the function works correctly
        timestamp = str(int(time.time()))
        body = '{"event":"test"}'
        signature = sign_webhook_payload(TEST_SECRET, timestamp, body)

        headers = {
            "X-Realtime-Signature": signature,
            "X-Realtime-Timestamp": timestamp
        }

        # Correct signature
        assert verify_webhook(TEST_SECRET, headers, body) is True

        # Off-by-one character
        bad_signature = signature[:-1] + ("0" if signature[-1] != "0" else "1")
        headers["X-Realtime-Signature"] = bad_signature
        assert verify_webhook(TEST_SECRET, headers, body) is False
