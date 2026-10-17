# Quick Start

## Installation

```bash
pip install apinator-server
```

## Create a Client

```python
from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",  # or "us"
)
```

## Trigger an Event

```python
import json

client.trigger(
    "new-message",
    json.dumps({"text": "Hello, world!"}),
    channel="chat-room",
)
```

You can also trigger to multiple channels at once:

```python
client.trigger(
    "update",
    json.dumps({"status": "active"}),
    channels=["room-1", "room-2", "room-3"],
)
```

## Channel Authentication

Private and presence channels require server-side authentication. Set up an auth endpoint that your client SDK will call:

```python
from flask import Flask, request, jsonify
from apinator import Apinator

app = Flask(__name__)
client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",
)

@app.route("/auth/channel", methods=["POST"])
def auth_channel():
    body = request.get_json()
    socket_id = body["socket_id"]
    channel_name = body["channel_name"]

    auth = client.authenticate_channel(socket_id, channel_name)
    return jsonify(auth)
```

The client SDKs POST a JSON body (`Content-Type: application/json`), so read it with
`request.get_json()` — `request.form` will be empty.

For presence channels, include channel data with user information:

```python
import json

@app.route("/auth/channel", methods=["POST"])
def auth_channel():
    body = request.get_json()
    socket_id = body["socket_id"]
    channel_name = body["channel_name"]

    channel_data = None
    if channel_name.startswith("presence-"):
        channel_data = json.dumps({
            "user_id": current_user.id,
            "user_info": {"name": current_user.name},
        })

    auth = client.authenticate_channel(socket_id, channel_name, channel_data)
    return jsonify(auth)
```

## Webhook Verification

Verify incoming webhooks to ensure they are authentic:

Use the webhook endpoint's signing secret (`whsec_...`, shown in the console per
endpoint), not the app's API secret:

```python
import json
import os
from flask import Flask, request, abort
from apinator import Apinator

app = Flask(__name__)
client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",
)
WEBHOOK_SECRET = os.environ["APINATOR_WEBHOOK_SECRET"]
processed_ids: set[str] = set()  # use a persistent store in production

@app.route("/webhooks/apinator", methods=["POST"])
def handle_webhook():
    headers = dict(request.headers)
    body = request.get_data(as_text=True)

    if not client.verify_webhook(WEBHOOK_SECRET, headers, body, max_age=300):
        abort(401)

    payload = json.loads(body)
    # {"id": "...", "event": "member_added", "app_id": "...", "channel": "presence-room",
    #  "user_id": "42", "time_ms": 1760000000000}

    # Deliveries are at-least-once: dedupe on id.
    if payload["id"] in processed_ids:
        return "", 200
    processed_ids.add(payload["id"])

    print(f"Received {payload['event']} on {payload.get('channel')}")
    return "", 200
```

## Next Steps

- See the [API Reference](api-reference.md) for the full API
- Check out the [examples](../examples/) for more usage patterns
