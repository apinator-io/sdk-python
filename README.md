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

```python
from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-webhook-secret",
    cluster="eu",
)

# In your webhook route handler:
headers = dict(request.headers)
body = request.get_data(as_text=True)

if client.verify_webhook(headers, body, max_age=300):
    # Webhook is valid — process the payload
    payload = json.loads(body)
else:
    # Invalid webhook
    abort(401)
```

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
