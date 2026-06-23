"""Client for the hosted Social Champ MCP server.

This is the only module that makes HTTP calls. Tools in ``server.py`` call
:meth:`SocialChampClient.call_tool` and never touch httpx directly.

Why this talks to the MCP endpoint, not the REST API
----------------------------------------------------
The live Social Champ tools are implemented in the auth backend
(``api/mcp/handlers.ts``) and reach champ through internal service routes
(``/api/v1/interCommunication/*``) that an external API key cannot call
directly. The only surface a user's API key or OAuth2 token can reach for the
full tool catalog is the hosted MCP server. So this client speaks JSON-RPC 2.0
to that server, the same way the Node proxy in the auth repo does. The tool
catalog and argument names are generated from the live ``tools.ts`` snapshot, so
arguments are forwarded as-is.

Authentication accepts either a Social Champ API key or an OAuth2 access token
(scopes ``read_profile`` and ``manage_post``, plus ``manage_team`` for the
agency tools). Both are sent as a Bearer token.
"""

from __future__ import annotations

from typing import Any

import httpx

from . import __version__
from .config import Settings, load_settings


class SocialChampError(RuntimeError):
    """A JSON-RPC error returned by the hosted MCP server."""

    def __init__(self, message: str, code: Any = None, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.data = data


class SocialChampClient:
    """Async JSON-RPC client for the hosted Social Champ MCP server."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()
        if not self._settings.api_key:
            raise RuntimeError(
                "SOCIALCHAMP_API_KEY is not set. Provide a Social Champ API key "
                "or OAuth2 access token in the environment before making requests."
            )
        self._url = self._settings.base_url
        self._protocol_version = self._settings.protocol_version
        self._client = httpx.AsyncClient(
            timeout=self._settings.timeout,
            headers={
                "Authorization": f"Bearer {self._settings.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        self._request_id = 0
        self._initialized = False

    async def aclose(self) -> None:
        await self._client.aclose()

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _rpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": self._next_id(), "method": method}
        if params is not None:
            payload["params"] = params
        response = await self._client.post(self._url, json=payload)
        response.raise_for_status()
        body = response.json()
        error = body.get("error")
        if error:
            raise SocialChampError(
                error.get("message", "Unknown MCP error"),
                code=error.get("code"),
                data=error.get("data"),
            )
        return body.get("result")

    async def _notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        response = await self._client.post(self._url, json=payload)
        response.raise_for_status()

    async def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        await self._rpc(
            "initialize",
            {
                "protocolVersion": self._protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "socialchamp-mcp-python", "version": __version__},
            },
        )
        await self._notify("notifications/initialized")
        self._initialized = True

    async def list_tools(self) -> list[dict[str, Any]]:
        """Return the tool list advertised by the hosted server."""
        await self._ensure_initialized()
        result = await self._rpc("tools/list")
        tools = result.get("tools") if isinstance(result, dict) else None
        return tools or []

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Invoke a tool on the hosted server and return its JSON-RPC result.

        Args:
            name: Tool name, for example ``create_text_post``.
            arguments: Tool arguments, already in the live server's camelCase shape.
        """
        await self._ensure_initialized()
        return await self._rpc("tools/call", {"name": name, "arguments": arguments})
