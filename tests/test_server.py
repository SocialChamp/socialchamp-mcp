"""Tests for the Social Champ MCP server.

These run without a real API key. HTTP is mocked with respx; the live API is
never called.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from socialchamp_mcp import server

# The published Social Champ MCP submission catalog (mcp-submission/mcp-schema.md).
EXPECTED_TOOLS = {
    "create_image_post",
    "create_text_post",
    "update_post",
    "delete_post",
    "get_channel",
    "get_channels",
    "get_filtered_channels",
    "get_workspaces",
    "get_paginated_posts",
    "get_posts_for_channels",
    "get_posts_with_assets",
    "get_scheduled_posts",
    "get_calendar_view_options",
    "get_shareable_calendars",
    "create_public_calendar_link",
    "get_in_app_calendar_url",
    "update_shareable_calendar",
    "delete_shareable_calendar",
}


async def _tools_by_name() -> dict:
    return {tool.name: tool for tool in await server.mcp.list_tools()}


async def test_all_tools_registered() -> None:
    tools = await _tools_by_name()
    assert EXPECTED_TOOLS <= set(tools)
    assert len(tools) == len(EXPECTED_TOOLS)


async def test_destructive_tools_carry_destructive_hint() -> None:
    tools = await _tools_by_name()
    assert tools["delete_post"].annotations.destructiveHint is True
    assert tools["delete_shareable_calendar"].annotations.destructiveHint is True


async def test_read_only_tool_carries_read_only_hint() -> None:
    tools = await _tools_by_name()
    assert tools["get_channels"].annotations.readOnlyHint is True


async def test_write_tool_is_not_read_only_or_destructive() -> None:
    tools = await _tools_by_name()
    annotations = tools["create_text_post"].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is False


async def test_create_text_post_makes_request(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOCIALCHAMP_API_KEY", "dummy-key")
    # Reset the cached client so it picks up the dummy key.
    server._client = None
    try:
        with respx.mock(base_url="https://api.socialchamp.com/api/v1") as mock:
            route = mock.post("/posts").mock(
                return_value=httpx.Response(
                    201, json={"id": "post_1", "status": "scheduled"}
                )
            )
            result = await server.create_text_post(
                text="hello world",
                channelIds=["chan_1"],
                dateTime="2026-07-01T14:30:00Z",
                isScheduled=True,
            )
            assert route.called
            sent = route.calls.last.request
            assert sent.headers["Authorization"] == "Bearer dummy-key"
            assert result == {"id": "post_1", "status": "scheduled"}
    finally:
        server._client = None
