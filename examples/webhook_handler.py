"""
Flask webhook handler example.

Usage:
    pip install flask
    export APINATOR_WEBHOOK_SECRET=whsec_...   # from the webhook endpoint in the console
    python webhook_handler.py
"""

import json
import os

from flask import Flask, request, abort
from apinator import Apinator

app = Flask(__name__)

client = Apinator(
    app_id=os.environ.get("APINATOR_APP_ID", "your-app-id"),
    key=os.environ.get("APINATOR_KEY", "your-app-key"),
    secret=os.environ.get("APINATOR_SECRET", "your-app-secret"),
    cluster="eu",
)

# Each webhook endpoint has its own signing secret (whsec_...). It is not the
# app's API secret.
WEBHOOK_SECRET = os.environ["APINATOR_WEBHOOK_SECRET"]

# Deliveries are at-least-once, so remember which event ids were handled.
# Use a persistent store (database, Redis) in production.
processed_ids: set[str] = set()


@app.route("/webhooks/apinator", methods=["POST"])
def handle_webhook():
    headers = dict(request.headers)
    body = request.get_data(as_text=True)

    # Reject bad signatures, and timestamps older than 5 minutes or more than
    # 5 minutes in the future.
    if not client.verify_webhook(WEBHOOK_SECRET, headers, body, max_age=300):
        abort(401)

    # {"id": "<event uuid>", "event": "member_added", "app_id": "...",
    #  "channel": "presence-room", "user_id": "42", "time_ms": 1760000000000}
    payload = json.loads(body)

    if payload["id"] in processed_ids:
        return "", 200  # duplicate delivery
    processed_ids.add(payload["id"])

    event = payload.get("event")
    channel = payload.get("channel")

    if event == "channel_occupied":
        print(f"Channel occupied: {channel}")
    elif event == "channel_vacated":
        print(f"Channel vacated: {channel}")
    elif event == "member_added":
        print(f"Member added to {channel}: {payload.get('user_id')}")
    elif event == "member_removed":
        print(f"Member removed from {channel}: {payload.get('user_id')}")
    elif event == "webhook.test":
        print("Test webhook received from the console")
    else:
        print(f"Received event: {event}")

    return "", 200


if __name__ == "__main__":
    app.run(port=3001, debug=True)
