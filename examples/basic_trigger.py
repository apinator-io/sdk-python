"""
Basic event triggering example.

Usage:
    python basic_trigger.py
"""

import json
from apinator import Apinator

client = Apinator(
    app_id="your-app-id",
    key="your-app-key",
    secret="your-app-secret",
    cluster="eu",
)

# Trigger to a single channel
client.trigger(
    "new-message",
    json.dumps({"text": "Hello from Python!"}),
    channel="chat-room",
)

print("Event triggered on 'chat-room'")

# Trigger to multiple channels
client.trigger(
    "notification",
    json.dumps({"message": "System update available"}),
    channels=["room-1", "room-2", "room-3"],
)

print("Event triggered on multiple channels")

# Trigger with socket_id exclusion
client.trigger(
    "typing",
    json.dumps({"user": "alice"}),
    channel="chat-room",
    socket_id="123.456",
)

print("Event triggered excluding socket 123.456")
