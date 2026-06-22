"""Configuration loaded from environment variables.

Loading settings never raises, so the package stays importable for tests and
tool discovery without credentials. The API key is required only when a request
is actually made, which is enforced in the client constructor, not here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Confirmed against the Social Champ authentication guide
# (https://developers.socialchamp.com/docs/authentication).
DEFAULT_BASE_URL = "https://api.socialchamp.com/api/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_TRANSPORT = "stdio"
VALID_TRANSPORTS = ("stdio", "sse", "streamable-http")


@dataclass(frozen=True)
class Settings:
    """Resolved server settings."""

    api_key: str | None
    base_url: str
    timeout: float
    transport: str


def _get_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_transport() -> str:
    transport = (os.environ.get("SOCIALCHAMP_TRANSPORT") or DEFAULT_TRANSPORT).strip()
    if transport not in VALID_TRANSPORTS:
        return DEFAULT_TRANSPORT
    return transport


def load_settings() -> Settings:
    """Read settings from the environment. This function never raises."""
    api_key = os.environ.get("SOCIALCHAMP_API_KEY") or None
    base_url = (os.environ.get("SOCIALCHAMP_API_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    return Settings(
        api_key=api_key,
        base_url=base_url,
        timeout=_get_float("SOCIALCHAMP_TIMEOUT", DEFAULT_TIMEOUT),
        transport=_get_transport(),
    )
