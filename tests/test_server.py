"""Tests for the Social Champ MCP server.

These run without a real API key. HTTP is mocked with respx; the live MCP server
is never called.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from socialchamp_mcp import server

# A representative slice of the generated catalog. The full catalog is generated
# from tools.schema.json, so the count assertion guards against accidental drift.
EXPECTED_SAMPLE = {
    "create_text_post",
    "create_image_post",
    "update_post",
    "delete_post",
    "get_channels",
    "get_workspaces",
    "get_scheduled_posts",
    "bulk_schedule",
    "queue_clear",
    "generate_post",
    "approval_approve",
    "delete_shareable_calendar",
}


async def _tools_by_name() -> dict:
    return {tool.name: tool for tool in await server.mcp.list_tools()}


async def test_full_catalog_registered() -> None:
    tools = await _tools_by_name()
    # The snapshot exported from the live server's tools.ts has 41 tools.
    assert len(tools) == 41
    assert EXPECTED_SAMPLE <= set(tools)


async def test_destructive_tools_carry_destructive_hint() -> None:
    tools = await _tools_by_name()
    for name in ("delete_post", "delete_shareable_calendar", "bulk_delete", "queue_clear"):
        assert tools[name].annotations.destructiveHint is True, name


async def test_read_only_tool_carries_read_only_hint() -> None:
    tools = await _tools_by_name()
    assert tools["get_channels"].annotations.readOnlyHint is True


async def test_write_tool_is_not_read_only_or_destructive() -> None:
    tools = await _tools_by_name()
    annotations = tools["create_text_post"].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is False


async def test_create_text_post_forwards_jsonrpc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOCIALCHAMP_API_KEY", "dummy-key")
    server._client = None  # reset cached client so it picks up the dummy key

    def responder(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        method = payload.get("method")
        if method == "initialize":
            return httpx.Response(
                200,
                json={"jsonrpc": "2.0", "id": payload["id"], "result": {"capabilities": {}}},
            )
        if method == "notifications/initialized":
            return httpx.Response(202, json={})
        if method == "tools/call":
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": payload["id"],
                    "result": {
                        "content": [{"type": "text", "text": "Text post request completed."}],
                        "structuredContent": {"result": {"id": "post_1"}},
                    },
                },
            )
        return httpx.Response(400, json={"error": "unexpected method"})

    try:
        with respx.mock as mock:
            route = mock.post("https://mcp.socialchamp.com/mcp").mock(side_effect=responder)
            result = await server.create_text_post(
                text="hello world",
                channelIds=["chan_1"],
                dateTime="2026-07-01T14:30:00Z",
                isScheduled=True,
            )

            # The Authorization header carries the bearer token.
            assert route.calls.last.request.headers["Authorization"] == "Bearer dummy-key"

            # A tools/call for create_text_post was sent with the camelCase args.
            call_bodies = [json.loads(c.request.content) for c in route.calls]
            tool_calls = [b for b in call_bodies if b.get("method") == "tools/call"]
            assert len(tool_calls) == 1
            assert tool_calls[0]["params"]["name"] == "create_text_post"
            assert tool_calls[0]["params"]["arguments"]["channelIds"] == ["chan_1"]
            assert tool_calls[0]["params"]["arguments"]["isScheduled"] is True

            assert result["structuredContent"]["result"]["id"] == "post_1"
    finally:
        server._client = None
