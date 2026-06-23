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

`src/socialchamp_mcp/server.py` is generated, so tools are not added by hand.

1. Add the tool to the live `api/mcp/tools.ts` in the auth repo.
2. Refresh `tools.schema.json` (the JSON snapshot of that array).
3. If the tool is read-only or destructive, add its name to the matching set in
   `scripts/generate_server.py`. Everything else is treated as a write.
4. Run `python scripts/generate_server.py` and commit the regenerated
   `server.py` together with the updated snapshot.
5. Add or extend a test in `tests/test_server.py`.

The client in `src/socialchamp_mcp/client.py` is the only file that makes HTTP
calls. It forwards every tool to the hosted MCP server over JSON-RPC, so a new
tool needs no client change.

## Testing

```bash
pytest
```

Mock all HTTP with `respx`. Never call the live MCP server from a test. Set a
dummy key through `monkeypatch` when a test exercises a request, and reset the
cached client (`server._client = None`) so the dummy key is picked up.

## Copy rules for docs and docstrings

- No em dashes.
- No filler phrasing.
- No invented numbers or statistics.
- Do not state a specific count of supported platforms.
