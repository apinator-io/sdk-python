"""
Error classes for Realtime SDK
"""

from __future__ import annotations


class RealtimeError(Exception):
    """Base exception for all Realtime SDK errors"""
    pass


class AuthenticationError(RealtimeError):
    """Raised when authentication fails"""
    pass


class ValidationError(RealtimeError):
    """Raised when input validation fails"""
    pass


class ApiError(RealtimeError):
    """Raised when API request fails"""

    def __init__(self, message: str, status: int, body: str | None = None):
        super().__init__(message)
        self.status = status
        self.body = body

    def __str__(self) -> str:
        base = f"{self.args[0]} (status: {self.status})"
        if self.body:
            return f"{base}, body: {self.body}"
        return base
