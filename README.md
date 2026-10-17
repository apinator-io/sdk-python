# apinator-server

[![PyPI Version](https://img.shields.io/pypi/v/apinator-server.svg)](https://pypi.org/project/apinator-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/apinator-io/sdk-python/actions/workflows/test.yml/badge.svg)](https://github.com/apinator-io/sdk-python/actions/workflows/test.yml)

Python server SDK for [Apinator](https://apinator.io) — trigger real-time events, authenticate channels, and verify webhooks.

## Features

- Trigger events on public, private, and presence channels
- Channel authentication (HMAC-SHA256)
- Webhook signature verification
- Channel introspection (list channels, get channel info)
- Zero external dependencies — Python 3.10+ stdlib only
- Full type hints throughout

## Installation

```bash
pip install apinator-server
```

## Quick Start

```python
from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",  # or "us"
)

# Trigger an event
client.trigger(
    "new-message",
    '{"text": "Hello!"}',
    channel="chat-room",
)
```

## Cache Channels

Publish to a channel named `cache-`, `private-cache-` or `presence-cache-` and Apinator keeps
the last event for 30 minutes, so a client that subscribes after the publish still receives it.
Nothing else changes: trigger as usual, and authorize private and presence cache channels like
any other private or presence channel.

```python
client.trigger(
    "job-finished",
    '{"status": "done"}',
    channel=f"private-cache-job-{job_id}",
)
```

## Channel Authentication

For private and presence channels, your backend must provide an auth endpoint:

```python
from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",
)

# In your auth route handler — the client SDKs POST a JSON body:
body = request.get_json()
socket_id = body["socket_id"]
channel_name = body["channel_name"]

auth = client.authenticate_channel(socket_id, channel_name)
# Return auth as JSON response
```

For presence channels, include channel data:

```python
import json

channel_data = json.dumps({
    "user_id": current_user.id,
    "user_info": {"name": current_user.name},
})

auth = client.authenticate_channel(socket_id, channel_name, channel_data)
```

## Webhook Verification

Each webhook endpoint you create in the console has its own signing secret
(`whsec_...`). Verify deliveries with that secret, not the app's API secret, and
pass the raw request body exactly as received.

```python
import json
import os

from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",
)
WEBHOOK_SECRET = os.environ["APINATOR_WEBHOOK_SECRET"]  # whsec_...

# In your webhook route handler (Flask shown):
headers = dict(request.headers)
body = request.get_data(as_text=True)

if not client.verify_webhook(WEBHOOK_SECRET, headers, body, max_age=300):
    abort(401)

payload = json.loads(body)
# {"id": "<event uuid>", "event": "member_added", "app_id": "...",
#  "channel": "presence-room", "user_id": "42", "time_ms": 1760000000000}
# user_id is only present on member_added / member_removed.

# Deliveries are at-least-once: skip an id you have already processed.
if already_processed(payload["id"]):
    return "", 200
```

Each delivery carries `X-Realtime-Signature` (`sha256=<hex>`),
`X-Realtime-Timestamp` (unix seconds), `X-Realtime-Event` and
`X-Realtime-Delivery-ID`. Events: `channel_occupied`, `channel_vacated`,
`member_added`, `member_removed`; the console's test button sends `webhook.test`.
With `max_age` set, timestamps older than `max_age` seconds or more than 300
seconds in the future are rejected.

## Channel Introspection

```python
# List all channels
channels = client.get_channels()

# Filter by prefix
presence_channels = client.get_channels(prefix="presence-")

# Get info about a specific channel
info = client.get_channel("presence-chat")
```

## API Reference

See [docs/api-reference.md](docs/api-reference.md) for the full API.

## Links

- [Quick Start Tutorial](docs/quickstart.md)
- [API Reference](docs/api-reference.md)
- [Examples](examples/)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## License

MIT — see [LICENSE](LICENSE).
