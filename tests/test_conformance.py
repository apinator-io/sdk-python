import json
from pathlib import Path
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from apinator import Apinator
from apinator.crypto import sign_request, sign_channel, sign_webhook_payload
from apinator.auth import authenticate_channel
from apinator.errors import AuthenticationError


ROOT = Path(__file__).resolve().parents[3]


def _load_fixture(name: str):
    path = ROOT / "backend" / "specs" / "conformance" / name
    if not path.exists():
        pytest.skip(f"Conformance fixture not available: {name} (only runs inside monorepo)")
    return json.loads(path.read_text())


def test_hmac_fixture_vectors():
    fixture = _load_fixture("hmac-request.v1.json")
    for case in fixture["cases"]:
        assert (
            sign_request(
                case["secret"],
                case["method"],
                case["path"],
                case["body"].encode("utf-8"),
                case["timestamp"],
            )
            == case["expected_signature"]
        )


def test_query_not_signed_case_uses_canonical_path():
    fixture = _load_fixture("hmac-request.v1.json")
    query_case = next(c for c in fixture["cases"] if c["name"] == "query-not-signed")

    canonical = sign_request(
        query_case["secret"],
        query_case["method"],
        query_case["path"],
        query_case["body"].encode("utf-8"),
        query_case["timestamp"],
    )
    assert canonical == query_case["expected_signature"]

    legacy = sign_request(
        query_case["secret"],
        query_case["method"],
        query_case["raw_path"],
        query_case["body"].encode("utf-8"),
        query_case["timestamp"],
    )
    assert legacy != query_case["expected_signature"]


def test_channel_fixture_vectors():
    fixture = _load_fixture("channel-auth.v1.json")
    for case in fixture["cases"]:
        signature = sign_channel(
            case["secret"],
            case["socket_id"],
            case["channel_name"],
            case.get("channel_data"),
        )
        assert signature == case["expected_signature"]

        auth = authenticate_channel(
            case["secret"],
            case["key"],
            case["socket_id"],
            case["channel_name"],
            case.get("channel_data"),
        )
        assert auth["auth"] == case["expected_auth"]


def test_webhook_fixture_vectors():
    fixture = _load_fixture("webhook-signature.v1.json")
    for case in fixture["cases"]:
        assert (
            sign_webhook_payload(case["secret"], case["timestamp"], case["body"])
            == case["expected_signature"]
        )


def test_client_parses_rfc7807_errors():
    client = Apinator("app", "key", "secret", cluster="eu")
    body = BytesIO(
        b'{"type":"https://docs.apinator.io/problems/unauthorized","title":"Unauthorized","status":401,"detail":"signature mismatch","code":"unauthorized"}'
    )

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = HTTPError(
            "https://ws-eu.apinator.io/apps/app/events", 401, "Unauthorized", {}, body
        )
        with pytest.raises(AuthenticationError):
            client.trigger("msg", "{}", channel="chat")
