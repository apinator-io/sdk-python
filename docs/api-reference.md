# API Reference

## `Apinator` Class

The main client for interacting with the Apinator API.

### Constructor

```python
from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `app_id` | `str` | Application ID |
| `key` | `str` | API key |
| `secret` | `str` | API secret |
| `cluster` | `str` | Cluster region identifier (e.g. `"eu"`, `"us"`) |

---

### `trigger(name, data, *, channel=None, channels=None, socket_id=None)`

Trigger an event to one or more channels.

```python
# Single channel
client.trigger("new-message", '{"text": "Hello!"}', channel="chat-room")

# Multiple channels
client.trigger("update", '{"status": "active"}', channels=["room-1", "room-2"])

# Exclude a socket
client.trigger("typing", '{}', channel="chat-room", socket_id="123.456")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Event name |
| `data` | `str` | Event data as JSON string |
| `channel` | `str \| None` | Single channel name (mutually exclusive with `channels`) |
| `channels` | `list[str] \| None` | List of channel names (mutually exclusive with `channel`) |
| `socket_id` | `str \| None` | Optional socket ID to exclude from broadcast |

**Returns:** `None`

**Raises:**
- `ValidationError` — if both `channel` and `channels` are provided, or neither
- `ApiError` — if the API request fails

---

### `authenticate_channel(socket_id, channel_name, channel_data=None)`

Authenticate a channel subscription request for private or presence channels.

```python
# Private channel
auth = client.authenticate_channel("123.456", "private-chat")

# Presence channel
import json
channel_data = json.dumps({"user_id": "user-1", "user_info": {"name": "Alice"}})
auth = client.authenticate_channel("123.456", "presence-chat", channel_data)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `socket_id` | `str` | Socket ID from the client |
| `channel_name` | `str` | Channel name to authenticate |
| `channel_data` | `str \| None` | Optional JSON string with user data for presence channels |

**Returns:** `dict` with keys:
- `auth` (`str`) — the authentication signature (`"{key}:{signature}"`)
- `channel_data` (`str`, optional) — echoed back for presence channels

---

### `get_channels(prefix=None)`

Get a list of active channels.

```python
# All channels
channels = client.get_channels()

# Filter by prefix
presence_channels = client.get_channels(prefix="presence-")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefix` | `str \| None` | Optional prefix filter for channel names |

**Returns:** `list[dict]` — list of channel info dictionaries

**Raises:**
- `ApiError` — if the API request fails

---

### `get_channel(channel_name)`

Get information about a specific channel.

```python
info = client.get_channel("presence-chat")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel_name` | `str` | Channel name |

**Returns:** `dict` — channel info dictionary

**Raises:**
- `ApiError` — if the API request fails

---

### `verify_webhook(headers, body, max_age=None)`

Verify a webhook signature.

```python
is_valid = client.verify_webhook(headers, body, max_age=300)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `headers` | `dict[str, str]` | HTTP headers from the webhook request |
| `body` | `str` | Webhook body as string |
| `max_age` | `int \| None` | Optional max age in seconds for timestamp freshness check |

**Returns:** `bool` — `True` if the signature is valid

---

## Standalone Functions

These functions can be used without creating an `Apinator` client instance.

### `authenticate_channel(secret, key, socket_id, channel_name, channel_data=None)`

```python
from apinator import authenticate_channel

auth = authenticate_channel(
    secret="your-secret",
    key="your-key",
    socket_id="123.456",
    channel_name="private-chat",
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `secret` | `str` | API secret key |
| `key` | `str` | API key |
| `socket_id` | `str` | Socket ID from the client |
| `channel_name` | `str` | Channel name to authenticate |
| `channel_data` | `str \| None` | Optional channel data for presence channels |

**Returns:** `dict` with `auth` and optionally `channel_data` keys

---

### `verify_webhook(secret, headers, body, max_age=None)`

```python
from apinator import verify_webhook

is_valid = verify_webhook(
    secret="your-webhook-secret",
    headers=headers,
    body=body,
    max_age=300,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `secret` | `str` | Webhook secret |
| `headers` | `dict[str, str]` | HTTP headers (case-insensitive lookup) |
| `body` | `str` | Webhook body as string |
| `max_age` | `int \| None` | Optional max age in seconds |

**Returns:** `bool` — `True` if the signature is valid and timestamp is fresh

---

## Error Classes

All errors inherit from `RealtimeError`.

### `RealtimeError`

Base exception for all SDK errors.

```python
from apinator import RealtimeError
```

### `AuthenticationError`

Raised when authentication fails (HTTP 401/403).

```python
from apinator import AuthenticationError
```

### `ValidationError`

Raised when input validation fails (HTTP 400/422 or invalid parameters).

```python
from apinator import ValidationError
```

### `ApiError`

Raised when an API request fails.

```python
from apinator import ApiError
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `int` | HTTP status code (0 for network errors) |
| `body` | `str \| None` | Response body if available |
