# Installing the Social Champ MCP server in Cline

The Social Champ MCP server is published on PyPI as `socialchamp-mcp` and runs locally over stdio, forwarding to the hosted Social Champ MCP server.

## Steps

1. **Install the package** (Python 3.10+):
   ```bash
   pip install socialchamp-mcp
   ```
   (or run with no install via `uvx socialchamp-mcp`)

2. **Get an API key.** Ask the user to create a Social Champ API key at **Social Champ → Settings → Developer**. It is sent as a Bearer token.

3. **Add the server to Cline** (`cline_mcp_settings.json`):
   ```json
   {
     "mcpServers": {
       "socialchamp": {
         "command": "socialchamp-mcp",
         "env": { "SOCIALCHAMP_API_KEY": "<USER_API_KEY>" }
       }
     }
   }
   ```
   If `socialchamp-mcp` is not on PATH, use `"command": "uvx", "args": ["socialchamp-mcp"]`.

4. **Verify** by calling the `get_channels` tool — it should return the user's connected social accounts.

## Notes
- 41 tools: channels/workspaces, posts (create/schedule/bulk), AI content (generate/rewrite/hashtags/images), queue control, labels, agency approvals, shareable calendars. Full reference: https://developers.socialchamp.com/docs/mcp-tools
- Requires a Social Champ account with at least one connected channel.
