# Social Champ MCP server

A Model Context Protocol (MCP) server for the [Social Champ](https://developers.socialchamp.com)
API. It exposes the Social Champ REST API to MCP-compatible AI clients such as
Claude Desktop, Claude Code, and Cursor as tools for scheduling posts, managing
connected social profiles, and reading analytics.

## Tools

| Tool | Description | Type |
| --- | --- | --- |
| `list_social_accounts` | List connected profiles with id, network, and display name | Read-only |
| `get_best_time_to_post` | Recommended posting times for a profile | Read-only |
| `get_account_analytics` | Aggregate metrics for a profile over a date range | Read-only |
| `list_scheduled_posts` | List scheduled, queued, and published posts | Read-only |
| `get_post` | Get a single post | Read-only |
| `get_post_analytics` | Engagement metrics for one published post | Read-only |
| `schedule_post` | Create or schedule a post to one or more profiles | Write |
| `update_post` | Edit the content or time of an existing post | Write |
| `delete_post` | Permanently delete a scheduled post | Destructive |

Each tool is annotated with `ToolAnnotations` so clients can apply the right
confirmation behavior. Destructive tools carry `destructiveHint=True`.

## Requirements

- Python 3.10 or newer.
- A Social Champ API key.

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
| `SOCIALCHAMP_API_KEY` | yes | none | Bearer token for API calls |
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

The base URL and Bearer authentication are confirmed from the Social Champ
[authentication guide](https://developers.socialchamp.com/docs/authentication).
The endpoint paths, request body field names, and query parameters live in
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
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False))
async def archive_post(post_id: str) -> dict:
    """Archive a post so it no longer appears in the active queue.

    Args:
        post_id: The id of the post to archive.
    """
    return await _get_client().archive_post(post_id)
```

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
