"""Tests for the Social Champ MCP server.

These run without a real API key. HTTP is mocked with respx; the live MCP server
is never called.
"""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import httpx
import pytest
import respx

from socialchamp_mcp import server
from socialchamp_mcp.client import SocialChampClient, SocialChampError

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
    "get_calendar_summary",
    "get_post_metrics",
    "get_drafts",
    "get_queue_slots",
    "get_best_times",
    "get_calendar_events",
    "get_post_comments",
    "get_post_app_url",
    "bulk_schedule",
    "queue_clear",
    "generate_post",
    "approval_approve",
    "delete_shareable_calendar",
    "create_media_upload",
    "complete_media_upload",
    "import_media_from_url",
}


async def _tools_by_name() -> dict:
    return {tool.name: tool for tool in await server.mcp.list_tools()}


async def test_full_catalog_registered() -> None:
    tools = await _tools_by_name()
    # Merged catalog includes the eight calendar read tools.
    assert len(tools) == 52
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


async def test_media_upload_schema_preserves_validation_constraints() -> None:
    tools = await _tools_by_name()
    schema = tools["create_media_upload"].inputSchema
    assert schema["properties"]["contentType"]["enum"] == [
        "image/jpeg",
        "image/png",
        "image/gif",
        "video/mp4",
        "video/quicktime",
    ]
    assert schema["properties"]["sizeBytes"]["minimum"] == 1
    assert schema["properties"]["sizeBytes"]["maximum"] == 209715200
    assert "requires an MCP host" in tools["create_media_upload"].description
    assert tools["complete_media_upload"].annotations.idempotentHint is True


async def test_reel_short_channel_options_preserve_nested_schema() -> None:
    tools = await _tools_by_name()
    for name in ("create_text_post", "create_image_post"):
        optional_options = tools[name].inputSchema["properties"]["channelOptions"]
        options = next(
            branch
            for branch in optional_options["anyOf"]
            if branch.get("type") == "object"
        )
        assert options["additionalProperties"] is False
        assert set(options["properties"]) == {"instagram", "facebook", "youtube"}
        assert options["properties"]["instagram"]["properties"]["placement"][
            "enum"
        ] == ["REEL_ONLY", "REEL_AND_FEED"]
        assert options["properties"]["youtube"]["properties"]["contentType"][
            "enum"
        ] == ["VIDEO", "SHORT"]
        assert options["properties"]["youtube"]["required"] == [
            "contentType",
            "title",
            "madeForKids",
        ]

    posts = tools["bulk_schedule"].inputSchema["properties"]["posts"]
    assert posts["minItems"] == 1
    assert posts["maxItems"] == 100
    assert posts["items"]["required"] == ["text", "channelIds"]
    assert posts["items"]["properties"]["channelOptions"]["properties"][
        "youtube"
    ]["required"] == ["contentType", "title", "madeForKids"]


async def test_update_post_exposes_video_cover_and_channel_options() -> None:
    tools = await _tools_by_name()
    update_properties = tools["update_post"].inputSchema["properties"]

    assert {"videoUrls", "coverMediaId", "channelOptions"} <= set(
        update_properties
    )
    update_options = next(
        branch
        for branch in update_properties["channelOptions"]["anyOf"]
        if branch.get("type") == "object"
    )
    assert "required" not in update_options["properties"]["youtube"]
    assert "coverMediaId" not in tools["create_image_post"].inputSchema[
        "properties"
    ]
    assert "pending approval" in tools["update_post"].description


async def test_nested_channel_options_are_validated_before_forwarding() -> None:
    with pytest.raises(Exception, match="title|required"):
        await server.mcp.call_tool(
            "create_text_post",
            {
                "text": "Launch",
                "channelIds": ["yt-1"],
                "videoUrls": ["https://cdn.example/clip.mp4"],
                "channelOptions": {"youtube": {"contentType": "SHORT"}},
            },
        )


def test_generated_server_matches_schema_snapshot() -> None:
    root = Path(__file__).resolve().parent.parent
    generator_path = root / "scripts" / "generate_server.py"
    spec = importlib.util.spec_from_file_location("generate_server", generator_path)
    assert spec and spec.loader
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)

    tools = json.loads((root / "tools.schema.json").read_text(encoding="utf-8"))
    expected = (
        generator.HEADER
        + "\n"
        + "\n\n".join(generator.render_tool(tool) for tool in tools)
        + "\n"
        + generator.FOOTER
    )
    actual = (root / "src" / "socialchamp_mcp" / "server.py").read_text(
        encoding="utf-8"
    )
    assert actual == expected


async def test_url_import_uses_extended_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOCIALCHAMP_API_KEY", "dummy-key")
    client = SocialChampClient()
    client._initialized = True
    observed: dict[str, object] = {}

    async def post(url: str, **kwargs: object) -> httpx.Response:
        observed.update(kwargs)
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"jsonrpc": "2.0", "id": 1, "result": {"ok": True}},
        )

    monkeypatch.setattr(client._client, "post", post)
    try:
        await client.call_tool("import_media_from_url", {"url": "https://test/media.mp4"})
        assert observed["timeout"] == 150.0
    finally:
        await client.aclose()


async def test_url_import_timeout_warns_against_duplicate_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SOCIALCHAMP_API_KEY", "dummy-key")
    client = SocialChampClient()
    client._initialized = True

    async def post(url: str, **_kwargs: object) -> httpx.Response:
        request = httpx.Request("POST", url)
        raise httpx.ReadTimeout("timed out", request=request)

    monkeypatch.setattr(client._client, "post", post)
    try:
        with pytest.raises(SocialChampError, match="Check the Media Library before retrying"):
            await client.call_tool(
                "import_media_from_url", {"url": "https://test/media.mp4"}
            )
    finally:
        await client.aclose()


async def test_ordinary_tools_keep_the_configured_client_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SOCIALCHAMP_API_KEY", "dummy-key")
    client = SocialChampClient()
    client._initialized = True
    observed: dict[str, object] = {}

    async def post(url: str, **kwargs: object) -> httpx.Response:
        observed.update(kwargs)
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"jsonrpc": "2.0", "id": 1, "result": {"ok": True}},
        )

    monkeypatch.setattr(client._client, "post", post)
    try:
        await client.call_tool("get_channels", {})
        assert "timeout" not in observed
        assert client._client.timeout.read == 30.0
    finally:
        await client.aclose()


async def test_url_import_gateway_timeout_warns_against_duplicate_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SOCIALCHAMP_API_KEY", "dummy-key")
    client = SocialChampClient()
    client._initialized = True

    async def post(url: str, **_kwargs: object) -> httpx.Response:
        request = httpx.Request("POST", url)
        return httpx.Response(504, request=request)

    monkeypatch.setattr(client._client, "post", post)
    try:
        with pytest.raises(SocialChampError, match="Check the Media Library before retrying"):
            await client.call_tool(
                "import_media_from_url", {"url": "https://test/media.mp4"}
            )
    finally:
        await client.aclose()


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
                videoUrls=["https://cdn.example/clip.mp4"],
                dateTime="2026-07-01T14:30:00Z",
                isScheduled=True,
                channelOptions={
                    "instagram": {
                        "placement": "REEL_AND_FEED",
                        "coverFrameTimeSeconds": 2.5,
                    },
                    "youtube": {
                        "contentType": "VIDEO",
                        "title": "Full video",
                        "privacyStatus": "unlisted",
                        "madeForKids": False,
                        "notifySubscribers": True,
                    },
                },
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
            assert tool_calls[0]["params"]["arguments"]["channelOptions"][
                "instagram"
            ]["coverFrameTimeSeconds"] == 2.5
            assert tool_calls[0]["params"]["arguments"]["channelOptions"][
                "youtube"
            ]["title"] == "Full video"

            assert result["structuredContent"]["result"]["id"] == "post_1"
    finally:
        server._client = None


@pytest.mark.parametrize("name,arguments", [
    ("get_calendar_summary", {"fromDate": "2030-01-01", "toDate": "2030-01-31", "timezone": "Asia/Karachi"}),
    ("get_post_metrics", {"postIds": ["post-1"]}),
    ("get_drafts", {"workspaceId": "workspace-1", "page": 2, "pageSize": 10}),
    ("get_queue_slots", {"channelId": "channel-1"}),
    ("get_best_times", {"channelId": "channel-1", "fromDate": "2030-01-01", "toDate": "2030-01-31"}),
    ("get_calendar_events", {"workspaceId": "workspace-1", "fromDate": "2030-01-01", "toDate": "2030-01-31"}),
    ("get_post_comments", {"postId": "post-1", "pageSize": 5}),
    ("get_post_app_url", {"postId": "post-1"}),
])
async def test_calendar_reads_forward_and_keep_read_only(name, arguments, monkeypatch):
    calls = []

    class Client:
        async def call_tool(self, tool_name, tool_arguments):
            calls.append((tool_name, tool_arguments))
            return {"structuredContent": {"test": True}}

    monkeypatch.setattr(server, "_client", Client())
    await getattr(server, name)(**arguments)
    assert calls[0][0] == name
    for key, value in arguments.items():
        assert calls[0][1][key] == value
    assert (await _tools_by_name())[name].annotations.readOnlyHint is True


async def test_paginated_filters_forward_false(monkeypatch):
    calls = []

    class Client:
        async def call_tool(self, name, arguments):
            calls.append(arguments)
            return {}

    monkeypatch.setattr(server, "_client", Client())
    await server.get_paginated_posts(channelIds=["channel-1"], status="FAILED", hasError=False, labelIds=["label-1"], approvalStatus="DECLINED", slim=True)
    assert calls[0]["hasError"] is False
    assert calls[0]["status"] == "FAILED"
    assert calls[0]["slim"] is True
