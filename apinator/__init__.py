"""
Apinator Server SDK for Python
"""

from .client import Apinator
from .auth import authenticate_channel
from .webhook import verify_webhook
from .errors import RealtimeError, AuthenticationError, ValidationError, ApiError

__version__ = "1.0.0"
__all__ = [
    "Apinator",
    "authenticate_channel",
    "verify_webhook",
    "RealtimeError",
    "AuthenticationError",
    "ValidationError",
    "ApiError",
]
