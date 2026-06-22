"""FastMCP server exposing Social Champ tools.

Tools call methods on :class:`SocialChampClient` and never make HTTP calls
directly. The client is created lazily on first tool use and cached.
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

    The constructor requires ``SOCIALCHAMP_API_KEY``, so importing this module
    and listing tools works without credentials, but the first real call fails
    clearly if the key is missing.
    """
    global _client
    if _client is None:
        _client = SocialChampClient()
    return _client


# ----------------------------------------------------------------------
# Read-only tools
# ----------------------------------------------------------------------


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def list_social_accounts() -> Any:
    """List the social profiles connected to the Social Champ account.

    Returns each connected profile with its id, network (for example the social
    platform name), and display name. Use the returned ids as ``account_id`` or
    ``account_ids`` arguments for the other tools.
    """
    return await _get_client().list_social_accounts()


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def get_best_time_to_post(account_id: str) -> Any:
    """Get recommended posting times for a connected profile.

    Args:
        account_id: The id of the profile, from ``list_social_accounts``.
    """
    return await _get_client().get_best_time_to_post(account_id)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def get_account_analytics(
    account_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Any:
    """Get aggregate metrics for a profile over a date range.

    Args:
        account_id: The id of the profile, from ``list_social_accounts``.
        start_date: Start of the range as an ISO 8601 date (YYYY-MM-DD).
            Omit to use the API default.
        end_date: End of the range as an ISO 8601 date (YYYY-MM-DD).
            Omit to use the API default.
    """
    return await _get_client().get_account_analytics(account_id, start_date, end_date)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def list_scheduled_posts(
    account_id: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> Any:
    """List scheduled, queued, and published posts.

    Args:
        account_id: Restrict results to one profile. Omit to include all profiles.
        status: Filter by post status, for example scheduled, queued, or published.
            Omit to include all statuses.
        limit: Maximum number of posts to return. Defaults to 20.
    """
    return await _get_client().list_scheduled_posts(account_id, status, limit)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def get_post(post_id: str) -> Any:
    """Get a single post by id.

    Args:
        post_id: The id of the post, from ``list_scheduled_posts`` or ``schedule_post``.
    """
    return await _get_client().get_post(post_id)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def get_post_analytics(post_id: str) -> Any:
    """Get engagement metrics for one published post.

    Args:
        post_id: The id of a published post.
    """
    return await _get_client().get_post_analytics(post_id)


# ----------------------------------------------------------------------
# Write tools
# ----------------------------------------------------------------------


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
async def schedule_post(
    content: str,
    account_ids: list[str],
    scheduled_time: str | None = None,
    media_urls: list[str] | None = None,
) -> Any:
    """Create or schedule a post to one or more profiles.

    Args:
        content: The text body of the post.
        account_ids: One or more profile ids to publish to, from
            ``list_social_accounts``.
        scheduled_time: When to publish, as an ISO 8601 timestamp
            (for example 2026-07-01T14:30:00Z). If omitted, the post is added
            to the queue instead of being scheduled for a specific time.
        media_urls: Optional list of image or video URLs to attach.
    """
    return await _get_client().schedule_post(
        content, account_ids, scheduled_time, media_urls
    )


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def update_post(
    post_id: str,
    content: str | None = None,
    scheduled_time: str | None = None,
) -> Any:
    """Edit the content or scheduled time of an existing post.

    Args:
        post_id: The id of the post to edit.
        content: New text body. Omit to leave the content unchanged.
        scheduled_time: New publish time as an ISO 8601 timestamp
            (for example 2026-07-01T14:30:00Z). Omit to leave the time unchanged.
    """
    return await _get_client().update_post(post_id, content, scheduled_time)


# ----------------------------------------------------------------------
# Destructive tools
# ----------------------------------------------------------------------


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def delete_post(post_id: str) -> Any:
    """Permanently delete a scheduled post.

    This cannot be undone. Clients should confirm before running.

    Args:
        post_id: The id of the post to delete.
    """
    return await _get_client().delete_post(post_id)


def main() -> None:
    """Console entry point. Runs the server over the configured transport."""
    settings = load_settings()
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
