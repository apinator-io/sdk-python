"""
Flask webhook handler example.

Usage:
    pip install flask
    python webhook_handler.py
"""

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

    # Verify the webhook signature (max_age=300 means reject if older than 5 min)
    if not client.verify_webhook(headers, body, max_age=300):
        abort(401)

    payload = json.loads(body)

    # Handle different event types
    event_type = payload.get("type")

    if event_type == "channel_occupied":
        print(f"Channel occupied: {payload.get('channel')}")
    elif event_type == "channel_vacated":
        print(f"Channel vacated: {payload.get('channel')}")
    elif event_type == "member_added":
        print(f"Member added to {payload.get('channel')}: {payload.get('user_id')}")
    elif event_type == "member_removed":
        print(f"Member removed from {payload.get('channel')}: {payload.get('user_id')}")
    else:
        print(f"Received event: {event_type}")

    return "", 200


if __name__ == "__main__":
    app.run(port=3001, debug=True)
