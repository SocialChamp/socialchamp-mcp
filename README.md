# Social Champ MCP server

A Model Context Protocol (MCP) server for the [Social Champ](https://developers.socialchamp.com)
API. It exposes the Social Champ REST API to MCP-compatible AI clients such as
Claude Desktop, Claude Code, and Cursor as tools for scheduling posts, managing
connected social profiles, and reading analytics.

## Tools

The tool catalog mirrors the published Social Champ MCP schema. Channels are
connected social profiles; workspaces group channels and shareable calendars.

| Tool | Description | Type |
| --- | --- | --- |
| `get_channels` | List all connected channels | Read-only |
| `get_channel` | Fetch one channel by id | Read-only |
| `get_filtered_channels` | Find channels by platform type and search text | Read-only |
| `get_workspaces` | List available workspaces | Read-only |
| `get_paginated_posts` | Browse post history by page | Read-only |
| `get_posts_for_channels` | Fetch posts for specific channels | Read-only |
| `get_posts_with_assets` | Fetch posts that contain media | Read-only |
| `get_scheduled_posts` | Fetch upcoming scheduled posts | Read-only |
| `get_calendar_view_options` | Supported calendar view modes | Read-only |
| `get_shareable_calendars` | List shareable calendars in a workspace | Read-only |
| `get_in_app_calendar_url` | In-app calendar URL | Read-only |
| `create_text_post` | Create or schedule a text post to channels | Write |
| `create_image_post` | Create or schedule an image post to channels | Write |
| `update_post` | Update an existing post by id | Write |
| `create_public_calendar_link` | Create a shareable public calendar link | Write |
| `update_shareable_calendar` | Update a shareable calendar | Write |
| `delete_post` | Delete a post by id | Destructive |
| `delete_shareable_calendar` | Delete a shareable calendar | Destructive |

Each tool is annotated with `ToolAnnotations` so clients can apply the right
confirmation behavior. Destructive tools carry `destructiveHint=True`.

The hosted Social Champ MCP server exposes more tools than this published
catalog (location search, AI wizard, queue operations, labels, recycling,
agency approval workflows, and bulk operations). This server covers the
published catalog.

## Requirements

- Python 3.10 or newer.
- A Social Champ API key or OAuth2 access token. Both are sent as a Bearer token.
  OAuth2 scopes used by the published tools are `read_profile` and `manage_post`.

## Install

With [uv](https://docs.astral.sh/uv/):

```bash
uv pip install socialchamp-mcp
```

With pip:

```bash
pip install socialchamp-mcp
```

From source:

```bash
git clone https://github.com/socialchamp/socialchamp-mcp.git
cd socialchamp-mcp
pip install -e ".[dev]"
```

## Configuration

Set configuration through environment variables.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SOCIALCHAMP_API_KEY` | yes | none | Bearer token: a Social Champ API key or OAuth2 access token |
| `SOCIALCHAMP_API_BASE_URL` | no | `https://api.socialchamp.com/api/v1` | Override base URL |
| `SOCIALCHAMP_TIMEOUT` | no | `30` | Request timeout in seconds |
| `SOCIALCHAMP_TRANSPORT` | no | `stdio` | `stdio`, `sse`, or `streamable-http` |

Copy `.env.example` to `.env` for local use. Never commit `.env`.

## MCP client setup

### Claude Desktop

Add the server to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "socialchamp": {
      "command": "socialchamp-mcp",
      "env": {
        "SOCIALCHAMP_API_KEY": "your-api-key"
      }
    }
  }
}
```

If the console script is not on your PATH, use `"command": "python"` with
`"args": ["-m", "socialchamp_mcp"]`.

### Claude Code

```bash
claude mcp add socialchamp --env SOCIALCHAMP_API_KEY=your-api-key -- socialchamp-mcp
```

## Running over HTTP

The default transport is stdio, which is what Claude Desktop and Claude Code
use. To run over HTTP instead, set `SOCIALCHAMP_TRANSPORT`:

```bash
SOCIALCHAMP_TRANSPORT=streamable-http SOCIALCHAMP_API_KEY=your-api-key socialchamp-mcp
```

`sse` is also supported. Point your client at the resulting HTTP endpoint.

## Mapping to the real API

The tool names, argument names, and nouns mirror the published Social Champ MCP
schema and the hosted server's tool definitions. The base URL and Bearer
authentication are confirmed from the Social Champ
[authentication guide](https://developers.socialchamp.com/docs/authentication).

The REST paths, request body field names, and query parameters live in
`src/socialchamp_mcp/client.py`. Where a path or field still needs to be
confirmed against the [OpenAPI reference](https://developers.socialchamp.com/api-reference),
it is marked with a `TODO` comment. All such assumptions are isolated to
`client.py`, so reconciling them never touches a tool definition. When you
confirm a value, update it there and the tools keep working unchanged.

## Project structure

```
socialchamp-mcp/
├── src/
│   └── socialchamp_mcp/
│       ├── __init__.py
│       ├── __main__.py      # python -m socialchamp_mcp
│       ├── config.py        # settings from the environment
│       ├── client.py        # the only file that makes HTTP calls
│       └── server.py        # FastMCP instance and tool definitions
└── tests/
    └── test_server.py
```

## Adding a tool

Add the HTTP call to the client, then expose it as a tool. For example:

```python
# client.py
async def archive_post(self, post_id: str):
    # TODO: confirm path against the OpenAPI reference.
    return await self._request("POST", f"/posts/{post_id}/archive")
```

```python
# server.py
@mcp.tool(annotations=WRITE)
async def archive_post(postId: str) -> dict:
    """Archive a post so it no longer appears in the active queue.

    Args:
        postId: The id of the post to archive.
    """
    return await _get_client().archive_post(postId)
```

`READ`, `WRITE`, `UPDATE`, and `DESTRUCTIVE` are `ToolAnnotations` presets
defined in `server.py`.

The tool never touches httpx. See `CONTRIBUTING.md` for the full checklist.

## Development

```bash
pip install -e ".[dev]"
pytest
```

To confirm the server starts over stdio:

```bash
SOCIALCHAMP_API_KEY=dummy SOCIALCHAMP_TIMEOUT=5 socialchamp-mcp
```

It waits for input on stdin rather than exiting. Stop it with Ctrl+C.

## Security

- The API key is read from the environment and sent as a Bearer token. It is
  never logged or written to disk by this server.
- Keep your key in `.env` or your client's secret store. Never commit it. The
  `.gitignore` excludes `.env`.
- Tools are annotated read-only, write, or destructive. `delete_post` carries
  `destructiveHint=True` so clients can confirm before running it.
- Scope your API key to only the permissions the tools need. If a key is
  exposed, rotate it in your Social Champ account.

## License

MIT. See [LICENSE](LICENSE).
