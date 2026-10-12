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
- Calendars: daily/channel/status summary, view options, in-app URL, shareable calendar create, list, update, delete.
- Calendar data: cached post metrics, workspace drafts, queue slots, best-time heat maps, public holidays, stored comments and individual post links.
- Media: direct upload, completion and public URL import.
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
  OAuth2 scopes used by the published tools are `read_profile` and `manage_post`;
  the agency tools (approvals, reminders, bulk delete) also need `manage_team`.

## Install

With [uv](https://docs.astral.sh/uv/), as a command on your PATH:

```bash
uv tool install socialchamp-mcp
```

If your shell then cannot find `socialchamp-mcp`, run `uv tool update-shell` and
open a new terminal. To run it without installing, use `uvx socialchamp-mcp`
wherever this README says `socialchamp-mcp`.

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
| `SOCIALCHAMP_MEDIA_IMPORT_TIMEOUT` | no | `150` | URL media import timeout in seconds |
| `SOCIALCHAMP_TRANSPORT` | no | `stdio` | `stdio`, `sse`, or `streamable-http` |
| `SOCIALCHAMP_MCP_PROTOCOL_VERSION` | no | `2025-06-18` | MCP protocol version sent on initialize |

The server reads only the environment; it does not load a `.env` file itself.
For local use, put the variables in a `.env` file (in a source checkout, copy
`.env.example`; otherwise create it with a line `SOCIALCHAMP_API_KEY=...` in an
editor), make it readable only by you, and load it into your shell before
starting the server:

```bash
chmod 600 .env
set -a; . ./.env; set +a
```

Run `unset SOCIALCHAMP_API_KEY` when you are done. Never commit `.env`.

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

The simplest way is the hosted server, with no API key: you sign in to Social
Champ in your browser instead.

```bash
claude mcp add --scope user --transport http SocialChamp https://mcp.socialchamp.com/mcp
```

Then run `/mcp` in Claude Code, choose `SocialChamp` and sign in. `--scope user`
makes the server available in every folder you open Claude Code in; without it,
only in the folder where you ran the command. The sign-in grants `read_profile`
and `manage_post`; approvals and other agency tools need `manage_team`, so use
an API key that has it if you need those.

To run this package locally with an API key instead, read the key without
showing it or saving it to your shell history:

```bash
printf 'Social Champ API key: '; read -rs SOCIALCHAMP_API_KEY; printf '\n'
claude mcp add --scope user SocialChamp --env SOCIALCHAMP_API_KEY="$SOCIALCHAMP_API_KEY" -- socialchamp-mcp
unset SOCIALCHAMP_API_KEY
```

With `uvx`, end the second line with `-- uvx socialchamp-mcp` instead. Claude
Code keeps the key in its own settings (`~/.claude.json`), as it does for any
server's environment, and the key is visible to other processes on the machine
for the moment the command runs. On a shared machine, prefer the hosted sign-in.

#### Calendar pane for Claude Code

Using Claude Code? The [Social Champ calendar mod](https://github.com/SocialChamp/socialchamp-claude-mods)
adds a side pane on top of this server: week, month and day views, failed posts
and approvals, drafts, and new posts written with Claude. It shows every change
first and sends it only after you press Yes. It also asks you before Claude
changes anything in Social Champ from chat.

```bash
claude plugin marketplace add SocialChamp/socialchamp-claude-mods
claude plugin install socialchamp-calendar@socialchamp-mods
```

It needs Claude Code 2.1.293 or later. Run `/reload-plugins`, then
`/socialchamp-calendar`. The mod looks for this server under the name
`SocialChamp`, as added above, so there is nothing to set. If you added it under
another name, set that name once with
`/plugin configure socialchamp-calendar@socialchamp-mods`. In auto mode,
add the permission rules from the
[mod's README](https://github.com/SocialChamp/socialchamp-claude-mods#auto-mode-permission-rules)
(`mcp__<server name>__<tool>`, spaces in the name as underscores) once the pane
has opened.

## Running over HTTP

The default transport is stdio, which is what Claude Desktop and Claude Code
use. To run over HTTP instead, set `SOCIALCHAMP_TRANSPORT`:

```bash
printf 'Social Champ API key: '; read -rs SOCIALCHAMP_API_KEY; printf '\n'
export SOCIALCHAMP_API_KEY
SOCIALCHAMP_TRANSPORT=streamable-http socialchamp-mcp
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
- Keep your key in `.env` or your client's secret store. Never commit it, and
  never type it into a command line, where shell history keeps it. The
  `.gitignore` excludes `.env`. Signing in with OAuth (the hosted server)
  needs no key at all.
- Tools are annotated read-only, write, or destructive. Destructive tools
  (`delete_post`, `delete_shareable_calendar`, `bulk_delete`, `queue_clear`)
  carry `destructiveHint=True` so clients can confirm before running them.
- Agency tools require the caller token to carry the `manage_team` scope. Tokens
  without it cannot invoke them.
- Scope your token to only the permissions the tools need. If a token is
  exposed, rotate it in your Social Champ account.

## License

MIT. See [LICENSE](LICENSE).


## Calendar and media tool compatibility

The catalog includes 52 tools and requires matching hosted Auth and Publisher implementations. Calendar summaries use inclusive ranges of at most 93 days and an IANA timezone. Counts are sparse; missing combinations mean zero. Metrics are cached, and comments are already-ingested inbox items. Use `get_paginated_posts` status, channel, label, approval and error filters for details, and `slim=true` to omit heavy media fields.

`get_post_app_url` opens the authenticated post preview; native live rows and drafts have no supported preview link. The new calendar reads require owner connections; delegated Admin/team-member contexts are rejected by the hosted service until its bridges preserve their permissions. Approval workflows require `manage_team`; reconnect OAuth and opt in on an owned account to grant it. Existing tokens are not upgraded.

Media tools support direct upload and public URL import. Imports use a separate 150-second client timeout. If an import times out or returns an ambiguous gateway failure, check the Media Library before retrying to avoid duplicate imports. Schema generation preserves nested platform options, enums and validation bounds.
