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
    socket_id = request.form["socket_id"]
    channel_name = request.form["channel_name"]

    auth = client.authenticate_channel(socket_id, channel_name)
    return jsonify(auth)
```

For presence channels, include channel data with user information:

```python
import json

@app.route("/auth/channel", methods=["POST"])
def auth_channel():
    socket_id = request.form["socket_id"]
    channel_name = request.form["channel_name"]

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

```python
import json
from flask import Flask, request, abort
from apinator import Apinator

app = Flask(__name__)
client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-webhook-secret",
    cluster="eu",
)

@app.route("/webhooks/apinator", methods=["POST"])
def handle_webhook():
    headers = dict(request.headers)
    body = request.get_data(as_text=True)

    if not client.verify_webhook(headers, body, max_age=300):
        abort(401)

    payload = json.loads(body)
    # Process the webhook payload
    print(f"Received event: {payload}")
    return "", 200
```

## Next Steps

- See the [API Reference](api-reference.md) for the full API
- Check out the [examples](../examples/) for more usage patterns
