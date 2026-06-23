# Social Champ MCP server

A Model Context Protocol (MCP) server for the [Social Champ](https://developers.socialchamp.com)
platform. It exposes the full Social Champ tool catalog to MCP-compatible AI
clients such as Claude Desktop, Claude Code, and Cursor: scheduling and managing
posts, managing connected channels and workspaces, labels, queues, recycling,
shareable calendars, agency approval workflows, and the AI content wizard.

## Tools

This server mirrors the live Social Champ MCP tool catalog. Channels are
connected social profiles; workspaces group channels and shareable calendars.
The tool definitions are generated from `tools.schema.json`, a snapshot of the
live server's catalog, so the full set of tools, argument names, and
descriptions stays in parity with the hosted server.

Tools are grouped by domain:

- Posts: create, update, delete, bulk schedule, browse, reorder the queue, set Instagram first comment.
- Channels: list, filter, fetch one, location search.
- Workspaces: list.
- Calendars: view options, in-app URL, shareable calendar create, list, update, delete.
- Queue: pause, resume, clear.
- Labels: list, create, apply, remove, bulk apply.
- Recycling: list collections, recycle a post.
- Agency workflows: list pending approvals, approve, reject, remind approvers, bulk delete.
- AI wizard: generate a post, suggest hashtags, rewrite, generate images.

Each tool is annotated with `ToolAnnotations` so clients can apply the right
confirmation behavior. Read-only tools carry `readOnlyHint=True`; destructive
tools (`delete_post`, `delete_shareable_calendar`, `bulk_delete`, `queue_clear`)
carry `destructiveHint=True`. Agency tools require the caller token to also
carry the `manage_team` scope; this is noted in each tool's description.

For the full per-tool list with required arguments and scopes, see
`tools.schema.json` here, or `api/mcp/IMPLEMENTED.md` in the auth repo.

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
| `SOCIALCHAMP_API_BASE_URL` | no | `https://mcp.socialchamp.com/mcp` | Override the hosted MCP endpoint (for example a local test server) |
| `SOCIALCHAMP_TIMEOUT` | no | `30` | Request timeout in seconds |
| `SOCIALCHAMP_TRANSPORT` | no | `stdio` | `stdio`, `sse`, or `streamable-http` |
| `SOCIALCHAMP_MCP_PROTOCOL_VERSION` | no | `2025-06-18` | MCP protocol version sent on initialize |

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

The tools forward to the hosted Social Champ MCP server over JSON-RPC. The live
tools are implemented in the auth backend (`api/mcp/handlers.ts`) and reach
champ through internal service routes that an external API key cannot call
directly, so the only surface a user's token can reach for the full catalog is
the hosted MCP server. `src/socialchamp_mcp/client.py` is the only file that
makes HTTP calls: it speaks JSON-RPC 2.0 (`initialize`, `tools/list`,
`tools/call`) to the endpoint in `SOCIALCHAMP_API_BASE_URL`.

`src/socialchamp_mcp/server.py` is generated from `tools.schema.json`, a
snapshot of the live server's `api/mcp/tools.ts`. To refresh after the live
catalog changes:

1. Re-export the snapshot from the auth repo into `tools.schema.json` (the live
   `tools.ts` array, as JSON).
2. Run `python scripts/generate_server.py`.

The base URL and Bearer authentication are confirmed from the Social Champ
[authentication guide](https://developers.socialchamp.com/docs/authentication).

## Project structure

```
socialchamp-mcp/
├── tools.schema.json        # snapshot of the live tool catalog (source for codegen)
├── scripts/
│   └── generate_server.py   # regenerates server.py from tools.schema.json
├── src/
│   └── socialchamp_mcp/
│       ├── __init__.py
│       ├── __main__.py      # python -m socialchamp_mcp
│       ├── config.py        # settings from the environment
│       ├── client.py        # the only file that makes HTTP calls (JSON-RPC)
│       └── server.py        # GENERATED: FastMCP instance and tool definitions
└── tests/
    └── test_server.py
```

## Adding a tool

Tools are generated, not hand-written. Add the tool to the live `api/mcp/tools.ts`
in the auth repo, refresh `tools.schema.json`, then run
`python scripts/generate_server.py`. The generator maps each tool to a
`@mcp.tool` function that forwards to `call_tool`, picks a `ToolAnnotations`
preset (`READ`, `WRITE`, `UPDATE`, `DESTRUCTIVE`), and writes the docstring from
the tool description. Update the classification sets in `scripts/generate_server.py`
when adding a destructive or read-only tool.

See `CONTRIBUTING.md` for the full checklist.

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
- Tools are annotated read-only, write, or destructive. Destructive tools
  (`delete_post`, `delete_shareable_calendar`, `bulk_delete`, `queue_clear`)
  carry `destructiveHint=True` so clients can confirm before running them.
- Agency tools require the caller token to carry the `manage_team` scope. Tokens
  without it cannot invoke them.
- Scope your token to only the permissions the tools need. If a token is
  exposed, rotate it in your Social Champ account.

## License

MIT. See [LICENSE](LICENSE).
