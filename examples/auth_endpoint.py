"""
Flask auth endpoint example for private and presence channels.

Usage:
    pip install flask
    python auth_endpoint.py
"""

import json
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
    # The client SDKs POST a JSON body: {"socket_id": ..., "channel_name": ...}
    body = request.get_json(silent=True) or {}
    socket_id = body.get("socket_id")
    channel_name = body.get("channel_name")

    if not socket_id or not channel_name:
        return jsonify({"error": "Missing socket_id or channel_name"}), 400

    # TODO: Add your own authorization logic here.
    # Check if the current user is allowed to subscribe to this channel.

    # For presence channels, include channel data
    channel_data = None
    if channel_name.startswith("presence-"):
        # In a real app, get user info from session/auth
        channel_data = json.dumps({
            "user_id": "user-123",
            "user_info": {"name": "Alice"},
        })

    auth = client.authenticate_channel(socket_id, channel_name, channel_data)
    return jsonify(auth)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
