"""FastMCP server exposing Social Champ tools.

The tool catalog, names, argument names, and nouns mirror the published Social
Champ MCP schema (``mcp-submission/mcp-schema.md``) and the definitions in the
auth backend's ``api/mcp/tools.ts``. Argument names use the same camelCase as
the published schema so a client sees the same interface as the hosted server.

Tools call methods on :class:`SocialChampClient` and never make HTTP calls
directly. The client is created lazily on first tool use and cached.

The hosted Social Champ MCP server exposes more tools than the published
submission catalog (location search, AI wizard, queue ops, labels, recycling,
agency workflows, bulk operations). This port covers the published catalog.
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


# Annotation presets.
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


# ----------------------------------------------------------------------
# Channels (read-only)
# ----------------------------------------------------------------------


@mcp.tool(annotations=READ)
async def get_channels(accountId: str | None = None) -> Any:
    """List all connected channels for the account.

    Args:
        accountId: Social Champ account id. Omit when the user has only one
            account; the default account is used automatically.
    """
    return await _get_client().get_channels(accountId)


@mcp.tool(annotations=READ)
async def get_channel(channelId: str, accountId: str | None = None) -> Any:
    """Fetch details for a single connected channel.

    Args:
        channelId: Channel id to fetch, from ``get_channels`` or ``get_filtered_channels``.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_channel(channelId, accountId)


@mcp.tool(annotations=READ)
async def get_filtered_channels(
    types: list[str] | None = None,
    search: str | None = None,
    accountId: str | None = None,
) -> Any:
    """List channels filtered by platform type and free text.

    Args:
        types: Platform names (for example twitter, facebook, linkedin,
            instagram, tiktok, youtube, pinterest, bluesky, threads, mastodon,
            google) or internal codes (TW, FB_PAGE, IN). Case-insensitive.
        search: Free text matched against channel name, screen name, or email.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_filtered_channels(types, search, accountId)


# ----------------------------------------------------------------------
# Workspaces (read-only)
# ----------------------------------------------------------------------


@mcp.tool(annotations=READ)
async def get_workspaces(accountId: str | None = None) -> Any:
    """List available workspaces for the account.

    Args:
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_workspaces(accountId)


# ----------------------------------------------------------------------
# Posts (read-only)
# ----------------------------------------------------------------------


@mcp.tool(annotations=READ)
async def get_paginated_posts(
    page: int = 1,
    pageSize: int = 20,
    fromDate: str | None = None,
    toDate: str | None = None,
    accountId: str | None = None,
) -> Any:
    """Browse post history with page controls.

    Args:
        page: 1-based page number. Defaults to 1.
        pageSize: Maximum posts per page. Defaults to 20.
        fromDate: ISO 8601 start date-time filter, inclusive (for example
            2026-04-01T00:00:00Z).
        toDate: ISO 8601 end date-time filter, inclusive.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_paginated_posts(page, pageSize, fromDate, toDate, accountId)


@mcp.tool(annotations=READ)
async def get_posts_for_channels(
    channelIds: list[str],
    limit: int = 50,
    fromDate: str | None = None,
    toDate: str | None = None,
    accountId: str | None = None,
) -> Any:
    """Fetch posts scoped to specific channels.

    Args:
        channelIds: Channel ids to scope results to, from ``get_channels``.
        limit: Maximum posts to return across the channels. Defaults to 50.
        fromDate: ISO 8601 start date-time filter, inclusive.
        toDate: ISO 8601 end date-time filter, inclusive.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_posts_for_channels(channelIds, limit, fromDate, toDate, accountId)


@mcp.tool(annotations=READ)
async def get_posts_with_assets(limit: int = 50, accountId: str | None = None) -> Any:
    """Fetch posts that include media assets such as images or videos.

    Args:
        limit: Maximum posts to return. Defaults to 50.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_posts_with_assets(limit, accountId)


@mcp.tool(annotations=READ)
async def get_scheduled_posts(
    limit: int = 50,
    fromDate: str | None = None,
    toDate: str | None = None,
    accountId: str | None = None,
) -> Any:
    """Fetch upcoming scheduled posts.

    Args:
        limit: Maximum posts to return. Defaults to 50.
        fromDate: ISO 8601 start date-time filter, inclusive.
        toDate: ISO 8601 end date-time filter, inclusive.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_scheduled_posts(limit, fromDate, toDate, accountId)


# ----------------------------------------------------------------------
# Posts (write)
# ----------------------------------------------------------------------


@mcp.tool(annotations=WRITE)
async def create_text_post(
    text: str,
    channelIds: list[str],
    dateTime: str | None = None,
    isScheduled: bool = False,
    location: dict[str, Any] | None = None,
    firstComment: dict[str, Any] | None = None,
    accountId: str | None = None,
) -> Any:
    """Create and optionally schedule a text post to one or more channels.

    Args:
        text: Post text to publish, exactly as the user wants it.
        channelIds: Target channel ids, from ``get_channels`` or ``get_filtered_channels``.
        dateTime: ISO 8601 publish time (for example 2026-04-10T14:00:00Z).
            Required when isScheduled is true. Omit to post immediately.
        isScheduled: Set true to schedule for a future dateTime. False or omitted
            posts immediately.
        location: Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT
            posts. Object with id, name, and optional place. Only the id is
            applied at publish. Other platforms ignore it.
        firstComment: Optional auto first comment. Object with text, optional
            media URL, and optional delayMinutes. Applies on supporting platforms.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().create_text_post(
        text, channelIds, dateTime, isScheduled, location, firstComment, accountId
    )


@mcp.tool(annotations=WRITE)
async def create_image_post(
    text: str,
    imageUrls: list[str],
    channelIds: list[str],
    dateTime: str | None = None,
    isScheduled: bool = False,
    location: dict[str, Any] | None = None,
    firstComment: dict[str, Any] | None = None,
    accountId: str | None = None,
) -> Any:
    """Create and optionally schedule an image post to one or more channels.

    Args:
        text: Caption or post text to publish with the images.
        imageUrls: Publicly accessible image URLs to attach.
        channelIds: Target channel ids, from ``get_channels`` or ``get_filtered_channels``.
        dateTime: ISO 8601 publish time. Required when isScheduled is true.
            Omit to post immediately.
        isScheduled: Set true to schedule for a future dateTime.
        location: Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT
            posts. Object with id, name, and optional place.
        firstComment: Optional auto first comment. Object with text, optional
            media URL, and optional delayMinutes.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().create_image_post(
        text, imageUrls, channelIds, dateTime, isScheduled, location, firstComment, accountId
    )


@mcp.tool(annotations=UPDATE)
async def update_post(
    postId: str,
    text: str | None = None,
    dateTime: str | None = None,
    channelIds: list[str] | None = None,
    imageUrls: list[str] | None = None,
    accountId: str | None = None,
) -> Any:
    """Update an existing post by postId.

    Args:
        postId: Post id to update.
        text: Updated text or caption. Omit to leave unchanged.
        dateTime: Updated ISO 8601 schedule time. Omit to leave unchanged.
        channelIds: Updated target channel ids. Omit to leave unchanged.
        imageUrls: Updated image URL list for media posts. Omit to leave unchanged.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().update_post(postId, text, dateTime, channelIds, imageUrls, accountId)


# ----------------------------------------------------------------------
# Posts (destructive)
# ----------------------------------------------------------------------


@mcp.tool(annotations=DESTRUCTIVE)
async def delete_post(postId: str, accountId: str | None = None) -> Any:
    """Delete an existing post by postId, such as canceling a scheduled post.

    This cannot be undone. Clients should confirm before running.

    Args:
        postId: Post id to delete.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().delete_post(postId, accountId)


# ----------------------------------------------------------------------
# Calendars (read-only)
# ----------------------------------------------------------------------


@mcp.tool(annotations=READ)
async def get_calendar_view_options(accountId: str | None = None) -> Any:
    """Return supported calendar viewing modes and capabilities.

    Args:
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_calendar_view_options(accountId)


@mcp.tool(annotations=READ)
async def get_shareable_calendars(workspaceId: str, accountId: str | None = None) -> Any:
    """List existing shareable calendars for a workspace.

    Args:
        workspaceId: Workspace id to list shareable calendars for, from ``get_workspaces``.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_shareable_calendars(workspaceId, accountId)


@mcp.tool(annotations=READ)
async def get_in_app_calendar_url(
    calendarToken: str | None = None, accountId: str | None = None
) -> Any:
    """Return the authenticated in-app Social Champ calendar URL.

    Args:
        calendarToken: Optional public calendar token (calendarId) from
            ``get_shareable_calendars`` or ``create_public_calendar_link``.
            Omit when only the in-app calendar URL is needed.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().get_in_app_calendar_url(calendarToken, accountId)


# ----------------------------------------------------------------------
# Calendars (write)
# ----------------------------------------------------------------------


@mcp.tool(annotations=WRITE)
async def create_public_calendar_link(
    workspaceId: str,
    name: str,
    profileIds: list[str],
    fromDate: str,
    toDate: str,
    password: str | None = None,
    permissionRoles: list[str] | None = None,
    isActive: bool = True,
    accountId: str | None = None,
) -> Any:
    """Create a shareable public calendar link for selected channels and date range.

    Args:
        workspaceId: Workspace id where the calendar is created, from ``get_workspaces``.
        name: Display name for the shareable calendar link.
        profileIds: Channel ids to include, from ``get_channels`` or ``get_filtered_channels``.
        fromDate: ISO 8601 start date-time for the shared window.
        toDate: ISO 8601 end date-time for the shared window.
        password: Optional password to protect the link. Must be 8 to 20 characters.
        permissionRoles: Optional roles allowed in the shared calendar. Any of
            EDIT, DELETE, APPROVE.
        isActive: Whether the link is active immediately. Defaults to true.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().create_public_calendar_link(
        workspaceId, name, profileIds, fromDate, toDate, password, permissionRoles, isActive, accountId
    )


@mcp.tool(annotations=UPDATE)
async def update_shareable_calendar(
    calendarId: str,
    workspaceId: str | None = None,
    name: str | None = None,
    fromDate: str | None = None,
    toDate: str | None = None,
    password: str | None = None,
    permissionRoles: list[str] | None = None,
    isActive: bool | None = None,
    accountId: str | None = None,
) -> Any:
    """Update a shareable calendar by calendarId.

    Args:
        calendarId: Shareable calendar id to update.
        workspaceId: Optional workspace id override.
        name: Updated display name. Omit to leave unchanged.
        fromDate: Updated ISO 8601 start date-time. Omit to leave unchanged.
        toDate: Updated ISO 8601 end date-time. Omit to leave unchanged.
        password: Updated password, 8 to 20 characters. Omit to keep current.
        permissionRoles: Updated roles. Any of EDIT, DELETE, APPROVE.
        isActive: Updated active status. Omit to leave unchanged.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().update_shareable_calendar(
        calendarId, workspaceId, name, fromDate, toDate, password, permissionRoles, isActive, accountId
    )


# ----------------------------------------------------------------------
# Calendars (destructive)
# ----------------------------------------------------------------------


@mcp.tool(annotations=DESTRUCTIVE)
async def delete_shareable_calendar(
    calendarId: str,
    workspaceId: str | None = None,
    accountId: str | None = None,
) -> Any:
    """Delete a shareable calendar by calendarId.

    This cannot be undone. Clients should confirm before running.

    Args:
        calendarId: Shareable calendar id to delete.
        workspaceId: Optional workspace id fallback for workspace-scoped delete.
        accountId: Social Champ account id. Omit to use the default account.
    """
    return await _get_client().delete_shareable_calendar(calendarId, workspaceId, accountId)


def main() -> None:
    """Console entry point. Runs the server over the configured transport."""
    settings = load_settings()
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
