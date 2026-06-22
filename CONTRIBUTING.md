# Contributing

Thanks for helping improve the Social Champ MCP server.

## Setup

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set `SOCIALCHAMP_API_KEY` if you want to run
the server against the live API. Tests do not need a key.

## How to add a tool

1. Add the HTTP call as a method on `SocialChampClient` in `src/socialchamp_mcp/client.py`.
   This is the only file that makes HTTP calls. Keep any assumption about the
   API behind a `TODO` comment so it can be reconciled against the OpenAPI
   reference.
2. Add the tool function in `src/socialchamp_mcp/server.py`. Decorate it with
   `@mcp.tool(...)` and pass `ToolAnnotations`. Have it call the client method.
   Do not call httpx from a tool.
3. Write the docstring for the model: state what the tool does, describe every
   argument, and note expected formats such as ISO 8601 timestamps.
4. Annotate it correctly:
   - Read-only: `readOnlyHint=True`.
   - Write: `readOnlyHint=False` with `destructiveHint=False`.
   - Destructive: `destructiveHint=True`.
5. Add a test in `tests/test_server.py`.

## Testing

```bash
pytest
```

Mock all HTTP with `respx`. Never call the live API from a test. Set a dummy
key through `monkeypatch` when a test exercises a client request. Reset the
cached client (`server._client = None`) so the dummy key is picked up.

## Copy rules for docs and docstrings

- No em dashes.
- No filler phrasing.
- No invented numbers or statistics.
- Do not state a specific count of supported platforms.
