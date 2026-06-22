"""Tests for the Social Champ MCP server.

These run without a real API key. HTTP is mocked with respx; the live API is
never called.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from socialchamp_mcp import server

EXPECTED_TOOLS = {
    "list_social_accounts",
    "get_best_time_to_post",
    "get_account_analytics",
    "list_scheduled_posts",
    "get_post",
    "get_post_analytics",
    "schedule_post",
    "update_post",
    "delete_post",
}


async def _tools_by_name() -> dict:
    return {tool.name: tool for tool in await server.mcp.list_tools()}


async def test_all_nine_tools_registered() -> None:
    tools = await _tools_by_name()
    assert EXPECTED_TOOLS <= set(tools)
    assert len(tools) == len(EXPECTED_TOOLS)


async def test_delete_post_is_destructive() -> None:
    tools = await _tools_by_name()
    assert tools["delete_post"].annotations.destructiveHint is True


async def test_read_only_tool_carries_read_only_hint() -> None:
    tools = await _tools_by_name()
    assert tools["list_social_accounts"].annotations.readOnlyHint is True


async def test_schedule_post_makes_request(monkeypatch: pytest.MonkeyPatch) -> None:
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
            result = await server.schedule_post(
                content="hello world",
                account_ids=["acc_1"],
                scheduled_time="2026-07-01T14:30:00Z",
            )
            assert route.called
            sent = route.calls.last.request
            assert sent.headers["Authorization"] == "Bearer dummy-key"
            assert result == {"id": "post_1", "status": "scheduled"}
    finally:
        server._client = None
