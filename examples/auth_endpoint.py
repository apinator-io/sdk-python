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
    socket_id = request.form["socket_id"]
    channel_name = request.form["channel_name"]

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
