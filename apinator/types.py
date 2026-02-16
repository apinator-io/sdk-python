"""
Type definitions for Apinator SDK
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ApinatorOptions:
    """Configuration options for Apinator client"""
    app_id: str
    key: str
    secret: str
    cluster: str


@dataclass
class TriggerParams:
    """Parameters for triggering an event"""
    name: str
    data: str
    channel: Optional[str] = None
    channels: Optional[list] = None
    socket_id: Optional[str] = None


@dataclass
class ChannelAuthResponse:
    """Response from channel authentication"""
    auth: str
    channel_data: Optional[str] = None


@dataclass
class ChannelInfo:
    """Information about a channel"""
    name: str
    subscription_count: int = 0
    user_count: Optional[int] = None
