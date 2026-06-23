"""Generate src/socialchamp_mcp/server.py from tools.schema.json.

tools.schema.json is a snapshot of the live Social Champ MCP tool catalog,
exported from the auth backend's api/mcp/tools.ts. Regenerate the server after
updating the snapshot so the Python port stays in parity with the live server:

    python scripts/generate_server.py

Run the export side from the auth repo to refresh the snapshot (see README,
"Mapping to the real API").
"""

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "tools.schema.json"
OUT = ROOT / "src" / "socialchamp_mcp" / "server.py"

# Classification. The live JSON-RPC server does not annotate tools; this is the
# client-facing guidance the Python port encodes as ToolAnnotations. Keep in
# sync with api/mcp/generate-implemented.cjs in the auth repo.
DESTRUCTIVE = {"delete_post", "delete_shareable_calendar", "bulk_delete", "queue_clear"}
READ = {
    "get_channel", "get_channels", "get_filtered_channels", "get_workspaces",
    "get_paginated_posts", "get_posts_for_channels", "get_posts_with_assets",
    "get_scheduled_posts", "get_calendar_view_options", "get_shareable_calendars",
    "get_in_app_calendar_url", "location_search", "approval_list_pending",
    "list_collections", "label_list", "suggest_hashtags", "rewrite",
}
UPDATE = {"update_post", "update_shareable_calendar"}

TYPE_MAP = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "list",
    "object": "dict",
}


def py_type(schema: dict) -> str:
    t = schema.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != "null"), None)
    return TYPE_MAP.get(t, "object").replace("object", "dict[str, object]")


def clean(text: str) -> str:
    if not text:
        return ""
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace('"""', "'").replace("\\", "")


def preset(name: str) -> str:
    if name in DESTRUCTIVE:
        return "DESTRUCTIVE"
    if name in READ:
        return "READ"
    if name in UPDATE:
        return "UPDATE"
    return "WRITE"


def render_default(schema: dict) -> str | None:
    if "default" not in schema:
        return None
    d = schema["default"]
    if isinstance(d, bool):
        return "True" if d else "False"
    if isinstance(d, (int, float, str)):
        return repr(d)
    return None


def build_params(props: dict, required: list[str]) -> tuple[list[str], list[str]]:
    """Return (signature parts, arg-dict entries) with required params first."""
    req_parts: list[str] = []
    opt_parts: list[str] = []
    keys: list[str] = []
    for key, schema in props.items():
        keys.append(key)
        ann = py_type(schema)
        if key in required:
            req_parts.append(f"{key}: {ann}")
            continue
        default = render_default(schema)
        if default is not None:
            opt_parts.append(f"{key}: {ann} = {default}")
        else:
            opt_parts.append(f"{key}: {ann} | None = None")
    return req_parts + opt_parts, keys


def docstring(tool: dict, props: dict, required: list[str]) -> str:
    lines = [clean(tool.get("description", tool["name"]))]
    scopes = tool.get("requiredScopes") or []
    if scopes:
        lines.append("")
        lines.append("Requires the caller token to also carry scope: " + ", ".join(scopes) + ".")
    if props:
        lines.append("")
        lines.append("Args:")
        for key, schema in props.items():
            desc = clean(schema.get("description", ""))
            flag = "" if key in required else " Optional."
            lines.append(f"    {key}: {desc}{flag}".rstrip())
    body = "\n".join(lines)
    return body


def render_tool(tool: dict) -> str:
    name = tool["name"]
    schema = tool.get("inputSchema") or {}
    props = schema.get("properties") or {}
    required = schema.get("required") or []
    sig_parts, keys = build_params(props, required)
    sig = ",\n    ".join(sig_parts)
    sig = f"\n    {sig},\n" if sig_parts else ""
    args_dict = ", ".join(f'"{k}": {k}' for k in keys)
    doc = docstring(tool, props, required)
    return f'''@mcp.tool(annotations={preset(name)})
async def {name}({sig}) -> Any:
    """{doc}
    """
    _args = {{{args_dict}}}
    return await _get_client().call_tool(
        "{name}", {{k: v for k, v in _args.items() if v is not None}}
    )
'''


HEADER = '''"""FastMCP server exposing the Social Champ MCP tool catalog.

GENERATED FILE. Do not edit by hand. Regenerate with:

    python scripts/generate_server.py

The tool catalog, names, argument names, and descriptions are generated from
tools.schema.json, a snapshot of the live server's api/mcp/tools.ts. Tools call
SocialChampClient.call_tool, which forwards the call to the hosted Social Champ
MCP server over JSON-RPC. The client is created lazily on first use and cached.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .client import SocialChampClient
from .config import load_settings

mcp = FastMCP("socialchamp")

_client: SocialChampClient | None = None


def _get_client() -> SocialChampClient:
    """Create the client on first use and cache it.

    The constructor requires a Social Champ API key or OAuth2 access token, so
    importing this module and listing tools works without credentials, but the
    first real call fails clearly if no token is set.
    """
    global _client
    if _client is None:
        _client = SocialChampClient()
    return _client


# ToolAnnotations presets. openWorldHint is true because every tool reaches an
# external service.
READ = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
WRITE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True
)
UPDATE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=True
)
DESTRUCTIVE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True
)

'''

FOOTER = '''
def main() -> None:
    """Console entry point. Runs the server over the configured transport."""
    settings = load_settings()
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
'''


def main() -> None:
    tools = json.loads(SCHEMA.read_text(encoding="utf-8"))
    blocks = [render_tool(t) for t in tools]
    OUT.write_text(HEADER + "\n" + "\n\n".join(blocks) + "\n" + FOOTER, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(tools)} tools")


if __name__ == "__main__":
    main()
