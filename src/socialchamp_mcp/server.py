"""FastMCP server exposing the Social Champ MCP tool catalog.

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


@mcp.tool(annotations=WRITE)
async def create_image_post(
    text: str,
    imageUrls: list,
    channelIds: list,
    accountId: str | None = None,
    dateTime: str | None = None,
    isScheduled: bool = False,
    location: dict | None = None,
    firstComment: dict | None = None,
    instaFirstComment: str | None = None,
) -> Any:
    """Create and optionally schedule an image post to one or more channels. After successful scheduling, ask whether to view posting calendar, check scheduled posts, or create another post.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    text: Caption or post text to publish with the images; provide plain text as entered by the user.
    imageUrls: Publicly accessible image URL strings to attach to the post (e.g. 'https://example.com/image.jpg').
    channelIds: Target channel id values where the post should be published; obtain these from 'get_channels' or 'get_filtered_channels'.
    dateTime: ISO 8601 date-time for when to publish (e.g. '2026-04-10T14:00:00Z'). Required when isScheduled is true. Omit to post immediately. Optional.
    isScheduled: Set to true to schedule the post for a future dateTime. Set to false or omit to post immediately. When true, dateTime is required. Optional.
    location: Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts. Resolve it FIRST via the 'location_search' tool and pass the returned object - only the `id` is applied when publishing; a bare name/place without a valid platform `id` is stored but NOT tagged on the post. Other platforms ignore this field. Optional.
    firstComment: Optional auto-first-comment. Lights up on every channel in this post that supports it: Instagram, LinkedIn (page + personal), Facebook page, YouTube, TikTok. Other platforms (X, BlueSky, Mastodon, Pinterest, Threads, Google Business) silently ignore the field. Each platform enforces its own char limit at publish time (IG 2200, FB 2000, LI 1250, TikTok 150). Optional.
    instaFirstComment: DEPRECATED - pass `firstComment: { text }` instead. Kept for backwards compatibility; if both are present, `firstComment` wins. Optional.
    """
    _args = {"accountId": accountId, "text": text, "imageUrls": imageUrls, "channelIds": channelIds, "dateTime": dateTime, "isScheduled": isScheduled, "location": location, "firstComment": firstComment, "instaFirstComment": instaFirstComment}
    return await _get_client().call_tool(
        "create_image_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def create_text_post(
    text: str,
    channelIds: list,
    accountId: str | None = None,
    dateTime: str | None = None,
    isScheduled: bool = False,
    location: dict | None = None,
    firstComment: dict | None = None,
    instaFirstComment: str | None = None,
) -> Any:
    """Create and optionally schedule a text post to one or more channels. After successful scheduling, ask whether to view posting calendar, check scheduled posts, or create another post.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    text: Post text content to publish exactly as the user wants it posted.
    channelIds: Target channel id values where the post should be published; obtain these from 'get_channels' or 'get_filtered_channels'.
    dateTime: ISO 8601 date-time for when to publish (e.g. '2026-04-10T14:00:00Z'). Required when isScheduled is true. Omit to post immediately. Optional.
    isScheduled: Set to true to schedule the post for a future dateTime. Set to false or omit to post immediately. When true, dateTime is required. Optional.
    location: Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts. Resolve it FIRST via the 'location_search' tool and pass the returned object - only the `id` is applied when publishing; a bare name/place without a valid platform `id` is stored but NOT tagged on the post. Other platforms ignore this field. Optional.
    firstComment: Optional auto-first-comment. Lights up on every channel in this post that supports it: Instagram, LinkedIn, Facebook page, YouTube, TikTok. Other platforms silently ignore the field. Per-platform char limits enforced at publish time. Optional.
    instaFirstComment: DEPRECATED - pass `firstComment: { text }` instead. Kept for backwards compatibility. Optional.
    """
    _args = {"accountId": accountId, "text": text, "channelIds": channelIds, "dateTime": dateTime, "isScheduled": isScheduled, "location": location, "firstComment": firstComment, "instaFirstComment": instaFirstComment}
    return await _get_client().call_tool(
        "create_text_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=UPDATE)
async def update_post(
    postId: str,
    accountId: str | None = None,
    text: str | None = None,
    dateTime: str | None = None,
    channelIds: list | None = None,
    imageUrls: list | None = None,
) -> Any:
    """Update an existing post by postId. Text maps to upstream message, and the post profile is auto-resolved from the existing post unless one channelId override is provided.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    postId: Post id to update.
    text: Updated text/caption for the post. Optional.
    dateTime: Updated ISO 8601 schedule date-time (e.g. '2026-04-18T14:00:00Z'). Optional.
    channelIds: Updated target channel ids. Optional.
    imageUrls: Updated image URL list for media posts. Optional.
    """
    _args = {"accountId": accountId, "postId": postId, "text": text, "dateTime": dateTime, "channelIds": channelIds, "imageUrls": imageUrls}
    return await _get_client().call_tool(
        "update_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=DESTRUCTIVE)
async def delete_post(
    postId: str,
    accountId: str | None = None,
) -> Any:
    """Delete an existing post by postId, such as canceling a scheduled post.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    postId: Post id to delete.
    """
    _args = {"accountId": accountId, "postId": postId}
    return await _get_client().call_tool(
        "delete_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_channel(
    channelId: str,
    accountId: str | None = None,
) -> Any:
    """Fetch details for a single connected channel by channelId. After returning details, suggest posting or viewing that channel's posts.

Args:
    channelId: Channel id to fetch details for; obtain this id from 'get_channels' or 'get_filtered_channels'.
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    """
    _args = {"channelId": channelId, "accountId": accountId}
    return await _get_client().call_tool(
        "get_channel", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def location_search(
    channelId: str,
    searchQuery: str,
    accountId: str | None = None,
) -> Any:
    """Resolve a free-text place query (e.g. 'Eiffel Tower', 'Starbucks Seattle') into taggable location candidates for an FB_PAGE, IG_BUSINESS, or IG_DIRECT channel. Returns a list of { id, name, place }. Call this FIRST to obtain a valid `id`, then pass that location object to a post-creation tool (create_text_post / create_image_post / bulk_schedule) - only the `id` is honored when the post is published; a bare name/place is ignored. Other channel types do not support location tagging.

Args:
    channelId: Facebook or Instagram channel id to search places for; obtain from 'get_channels' or 'get_filtered_channels'. The channel's connection is used to query the platform, so results are scoped to that platform.
    searchQuery: Free-text place to look up, e.g. a venue, business, or landmark name.
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    """
    _args = {"channelId": channelId, "searchQuery": searchQuery, "accountId": accountId}
    return await _get_client().call_tool(
        "location_search", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_channels(
    accountId: str | None = None,
) -> Any:
    """List all connected channels for the account. After listing, suggest filtering channels or creating a post.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    """
    _args = {"accountId": accountId}
    return await _get_client().call_tool(
        "get_channels", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_filtered_channels(
    accountId: str | None = None,
    types: list | None = None,
    search: str | None = None,
) -> Any:
    """List channels filtered by platform types and/or text search. After results, suggest creating a post or viewing posts for those channels.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    types: Filter by platform names ('twitter','facebook','linkedin','instagram','tiktok','youtube','pinterest','bluesky','threads','mastodon','google') or internal codes ('TW','FB_PAGE','IN', etc.). Names are case-insensitive. Optional.
    search: Free-text search across channel name, screenName, or email fields. Omit to disable text filtering. Optional.
    """
    _args = {"accountId": accountId, "types": types, "search": search}
    return await _get_client().call_tool(
        "get_filtered_channels", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_workspaces(
    accountId: str | None = None,
) -> Any:
    """List available workspaces for the account. After listing, suggest viewing or creating shareable calendars.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    """
    _args = {"accountId": accountId}
    return await _get_client().call_tool(
        "get_workspaces", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_paginated_posts(
    accountId: str | None = None,
    page: float = 1,
    pageSize: float = 20,
    fromDate: str | None = None,
    toDate: str | None = None,
) -> Any:
    """Browse post history with page and pageSize controls. After results, suggest next page, channel-specific posts, or scheduled posts.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    page: 1-based page number to fetch. Omit to use the first page. Optional.
    pageSize: Maximum number of posts to return per page. Omit to use the default page size. Optional.
    fromDate: Optional ISO 8601 start date-time filter (inclusive), e.g. '2026-04-01T00:00:00Z'. Optional.
    toDate: Optional ISO 8601 end date-time filter (inclusive), e.g. '2026-04-30T23:59:59Z'. Optional.
    """
    _args = {"accountId": accountId, "page": page, "pageSize": pageSize, "fromDate": fromDate, "toDate": toDate}
    return await _get_client().call_tool(
        "get_paginated_posts", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_posts_for_channels(
    channelIds: list,
    accountId: str | None = None,
    limit: float = 50,
    fromDate: str | None = None,
    toDate: str | None = None,
) -> Any:
    """Fetch posts scoped to specific channelIds with an optional limit. After results, suggest creating a post or checking scheduled posts.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    channelIds: Channel id values to scope results to; obtain these from 'get_channels' or 'get_filtered_channels'.
    limit: Maximum number of posts to return across the selected channels. Omit to use the default limit. Optional.
    fromDate: Optional ISO 8601 start date-time filter (inclusive), e.g. '2026-04-01T00:00:00Z'. Optional.
    toDate: Optional ISO 8601 end date-time filter (inclusive), e.g. '2026-04-30T23:59:59Z'. Optional.
    """
    _args = {"accountId": accountId, "channelIds": channelIds, "limit": limit, "fromDate": fromDate, "toDate": toDate}
    return await _get_client().call_tool(
        "get_posts_for_channels", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_posts_with_assets(
    accountId: str | None = None,
    limit: float = 50,
) -> Any:
    """Fetch posts that include media assets such as images or videos. After results, suggest creating an image post or viewing all posts.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    limit: Maximum number of asset-containing posts to return. Omit to use the default limit. Optional.
    """
    _args = {"accountId": accountId, "limit": limit}
    return await _get_client().call_tool(
        "get_posts_with_assets", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_scheduled_posts(
    accountId: str | None = None,
    limit: float = 50,
    fromDate: str | None = None,
    toDate: str | None = None,
) -> Any:
    """Fetch upcoming scheduled posts with an optional limit. After results, suggest creating a new post or opening calendar views.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    limit: Maximum number of scheduled posts to return. Omit to use the default limit. Optional.
    fromDate: Optional ISO 8601 start date-time filter (inclusive), e.g. '2026-04-01T00:00:00Z'. Optional.
    toDate: Optional ISO 8601 end date-time filter (inclusive), e.g. '2026-04-30T23:59:59Z'. Optional.
    """
    _args = {"accountId": accountId, "limit": limit, "fromDate": fromDate, "toDate": toDate}
    return await _get_client().call_tool(
        "get_scheduled_posts", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_calendar_view_options(
    accountId: str | None = None,
) -> Any:
    """Return supported calendar viewing modes and capabilities. After results, suggest viewing scheduled posts or creating a shareable link.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    """
    _args = {"accountId": accountId}
    return await _get_client().call_tool(
        "get_calendar_view_options", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_shareable_calendars(
    workspaceId: str,
    accountId: str | None = None,
) -> Any:
    """List existing shareable calendars for a workspace. After results, suggest creating a new link or opening calendar views.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id to list shareable calendars for; obtain this from 'get_workspaces'.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId}
    return await _get_client().call_tool(
        "get_shareable_calendars", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def create_public_calendar_link(
    workspaceId: str,
    name: str,
    profileIds: list,
    fromDate: str,
    toDate: str,
    accountId: str | None = None,
    password: str | None = None,
    permissionRoles: list | None = None,
    isActive: bool = True,
) -> Any:
    """Create a shareable public calendar link for selected channels and date range. Before creating, ask whether the link should be password protected or open; if protected, collect an 8-20 character password.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id where the shareable calendar should be created; obtain this from 'get_workspaces'.
    name: Display name for the shareable calendar link shown to users.
    profileIds: Profile/channel id values to include in the shared calendar; these are channelId values from 'get_channels' or 'get_filtered_channels'.
    fromDate: ISO 8601 start date-time for the shared calendar window (e.g. '2026-04-01T00:00:00Z').
    toDate: ISO 8601 end date-time for the shared calendar window (e.g. '2026-04-30T23:59:59Z').
    password: Optional password to protect the public calendar link; must be 8-20 characters if provided. Omit for an unprotected link. Optional.
    permissionRoles: Optional permission role strings to allow actions in the shared calendar ('EDIT', 'DELETE', 'APPROVE'). Omit to use default permissions. Optional.
    isActive: Whether the created public calendar link should be active immediately. Omit to create it as active. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "name": name, "profileIds": profileIds, "fromDate": fromDate, "toDate": toDate, "password": password, "permissionRoles": permissionRoles, "isActive": isActive}
    return await _get_client().call_tool(
        "create_public_calendar_link", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_in_app_calendar_url(
    accountId: str | None = None,
    calendarToken: str | None = None,
) -> Any:
    """Return the authenticated in-app Social Champ calendar URL. After results, suggest viewing scheduled posts or managing shareable calendars.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    calendarToken: Optional public calendar token (calendarId), typically obtained from 'get_shareable_calendars' or 'create_public_calendar_link'. Omit when only the in-app calendar URL is needed. Optional.
    """
    _args = {"accountId": accountId, "calendarToken": calendarToken}
    return await _get_client().call_tool(
        "get_in_app_calendar_url", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=UPDATE)
async def update_shareable_calendar(
    calendarId: str,
    accountId: str | None = None,
    workspaceId: str | None = None,
    name: str | None = None,
    fromDate: str | None = None,
    toDate: str | None = None,
    password: str | None = None,
    permissionRoles: list | None = None,
    isActive: bool | None = None,
) -> Any:
    """Update a shareable calendar by calendarId, including name, date range, password, isActive, or permissionRoles.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    calendarId: Shareable calendar id to update.
    workspaceId: Optional workspace id override when resolving update payloads. Optional.
    name: Updated display name for the shareable calendar. Optional.
    fromDate: Updated ISO 8601 start date-time for the shared calendar window. Optional.
    toDate: Updated ISO 8601 end date-time for the shared calendar window. Optional.
    password: Optional updated password (8-20 chars). Omit to keep current password unchanged. Optional.
    permissionRoles: Optional updated permission role strings ('EDIT', 'DELETE', 'APPROVE'). Optional.
    isActive: Optional active status for the shareable calendar. Optional.
    """
    _args = {"accountId": accountId, "calendarId": calendarId, "workspaceId": workspaceId, "name": name, "fromDate": fromDate, "toDate": toDate, "password": password, "permissionRoles": permissionRoles, "isActive": isActive}
    return await _get_client().call_tool(
        "update_shareable_calendar", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def approval_list_pending(
    accountId: str | None = None,
    status: str = 'PENDING',
    profileIds: list | None = None,
    teamMemberIds: list | None = None,
    start: int = 0,
    limit: int = 25,
) -> Any:
    """List posts awaiting approval, owned by the account. Returns up to 50 per call. Filterable by channel and team-member id. Use to answer 'what's pending review' or 'show me posts waiting on me'.

Requires the caller token to also carry scope: manage_team.

Args:
    accountId: SocialChamp account id. Optional.
    status: Approval status to filter by. Defaults to PENDING. Optional.
    profileIds: Optional channel-id filter. Optional.
    teamMemberIds: Optional team-member-id filter. Optional.
    start: Pagination offset. Optional.
    limit:  Optional.
    """
    _args = {"accountId": accountId, "status": status, "profileIds": profileIds, "teamMemberIds": teamMemberIds, "start": start, "limit": limit}
    return await _get_client().call_tool(
        "approval_list_pending", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def approval_approve(
    postId: str,
    accountId: str | None = None,
    comment: str | None = None,
    dateTime: str | None = None,
) -> Any:
    """Approve a post that's awaiting review. The account must be in the workflow's approvers list for the active stage - if not, returns NOT_AN_APPROVER. Optional comment is recorded on the workflow history. Optional dateTime reschedules the post when the approval also moves it past the final stage.

Requires the caller token to also carry scope: manage_team.

Args:
    accountId:  Optional.
    postId:
    comment: Optional comment recorded with the decision. Optional.
    dateTime: Optional ISO 8601 reschedule time. When the post moves past the final approval stage, the publish time is set to this value (or now, if omitted). Optional.
    """
    _args = {"accountId": accountId, "postId": postId, "comment": comment, "dateTime": dateTime}
    return await _get_client().call_tool(
        "approval_approve", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def approval_reject(
    postId: str,
    accountId: str | None = None,
    comment: str | None = None,
) -> Any:
    """Reject a post that's awaiting review. Same approver requirement as approval_approve. Optional comment is recorded; the post moves to DECLINED status and a notification fires to the post owner.

Requires the caller token to also carry scope: manage_team.

Args:
    accountId:  Optional.
    postId:
    comment: Optional comment explaining the rejection. Recommended. Optional.
    """
    _args = {"accountId": accountId, "postId": postId, "comment": comment}
    return await _get_client().call_tool(
        "approval_reject", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def approval_assign(
    postId: str,
    accountId: str | None = None,
    email: str | None = None,
) -> Any:
    """Send an approval reminder for a pending post. Wraps the dashboard's 'Send reminder' notification - fires to the workflow stage's approvers (the same set defined in the workflow template). When `email` is supplied, validates that person IS an approver before sending; pass it to assert someone specific is in the loop. Throttled at 1 hour per post - repeated calls return ALREADY_NOTIFIED. Note: this does NOT modify the workflow's approver list - to add someone, edit the workflow template in Settings.

Requires the caller token to also carry scope: manage_team.

Args:
    accountId:  Optional.
    postId: Pending post id. Get from 'approval_list_pending'.
    email: Optional. Email of an approver the user wants to confirm is in the loop. Returns NOT_AN_APPROVER (403) if the email isn't in the workflow stage's approvers list. Notification still goes to ALL stage approvers (notification fan-out is workflow-defined). Optional.
    """
    _args = {"accountId": accountId, "postId": postId, "email": email}
    return await _get_client().call_tool(
        "approval_assign", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=DESTRUCTIVE)
async def bulk_delete(
    accountId: str | None = None,
    postIds: list | None = None,
    channelIds: list | None = None,
    fromDate: str | None = None,
    toDate: str | None = None,
    status: str | None = None,
    hasError: bool | None = None,
    dryRun: bool = True,
) -> Any:
    """Delete many posts at once - past or future, by either an explicit id list OR a predicate (channels × date range × status × error state). DESTRUCTIVE: defaults to dryRun=true; the LLM MUST explicitly pass dryRun=false to actually delete after the user confirms. Cap is 500 posts per call - anything bigger needs scripting. Each delete also cancels its publish job. Note: queue_clear is the lighter primitive for 'clear my upcoming queue' - bulk_delete is for ad-hoc destructive cleanup (failed posts, posts on a deprecated channel, etc.).

Requires the caller token to also carry scope: manage_team.

Args:
    accountId:  Optional.
    postIds: Explicit post-id list. When supplied, the predicate filters below are ignored (you're targeting specific posts). Optional.
    channelIds: Channel filter. Combined with the other predicates with AND. Optional.
    fromDate: ISO 8601. Posts with dateTime >= fromDate are candidates. Optional.
    toDate: ISO 8601. Posts with dateTime <= toDate are candidates. Optional.
    status: Filter by post status. SCHEDULED forces dateTime >= now if no fromDate is given. Optional.
    hasError: Filter by whether the post has a recorded error. Useful for cleaning up the FAILED bucket. Optional.
    dryRun: When true (default), returns the count without deleting. Pass false to actually delete - irreversible. Optional.
    """
    _args = {"accountId": accountId, "postIds": postIds, "channelIds": channelIds, "fromDate": fromDate, "toDate": toDate, "status": status, "hasError": hasError, "dryRun": dryRun}
    return await _get_client().call_tool(
        "bulk_delete", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def queue_reorder(
    items: list,
    accountId: str | None = None,
) -> Any:
    """Reschedule many posts in one call. Takes a list of {postId, dateTime} pairs and applies each as a time-only update - useful for 'swap these two posts', 'shift Tuesday's batch to Wednesday', or 'pull the launch announcement up to morning'. Distinct from queue_pause (which freezes posts in place) and bulk_delete (which removes them) - this just moves their dateTime. Sequential per-post update so a failure on one doesn't roll back the others; per-item failures captured in `data.failures`. Up to 100 items per call.

Args:
    accountId:  Optional.
    items: Array of {postId, dateTime} pairs. Each post is rescheduled to the supplied ISO 8601 dateTime.
    """
    _args = {"accountId": accountId, "items": items}
    return await _get_client().call_tool(
        "queue_reorder", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def bulk_label(
    postIds: list,
    labelIds: list,
    accountId: str | None = None,
    mode: str = 'replace',
) -> Any:
    """Apply (or replace, or clear) labels on up to 200 posts in a single call. Use mode=add to union the supplied labelIds with each post's existing labels (default mode=replace overwrites). The response reports per-post failures so the LLM can re-try only the bad ones.

Requires the caller token to also carry scope: manage_team.

Args:
    accountId:  Optional.
    postIds: Target post ids. Discover via 'get_paginated_posts' / 'get_scheduled_posts' / 'approval_list_pending'.
    labelIds: Label ids to apply. Empty array + mode=replace clears all labels from each post. Discover via 'label_list'.
    mode: 'replace' overwrites each post's labels; 'add' unions with existing labels. Optional.
    """
    _args = {"accountId": accountId, "postIds": postIds, "labelIds": labelIds, "mode": mode}
    return await _get_client().call_tool(
        "bulk_label", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def generate_post(
    workspaceId: str,
    prompt: str,
    accountId: str | None = None,
    channels: list | None = None,
    useBrandVoice: bool = True,
) -> Any:
    """Draft a social-media post body in the user's brand voice. Use when the user says 'write a post about X', 'draft something for our launch', 'give me an idea for Black Friday'. Produces text only - does not schedule. After successful generation, suggest scheduling it via 'create_text_post' or 'bulk_schedule', or refining via 'rewrite'.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account. Optional.
    workspaceId: Workspace id whose brand voice + AI key should be used. Required. Discover via 'get_workspaces'.
    prompt: What the post should be about, plain English. e.g. 'announce our new pricing page in a friendly, slightly playful tone'.
    channels: Optional target channel ids - informs length / format hints to the model. Optional.
    useBrandVoice: Apply the workspace's saved brand-voice description and sample posts. Default true. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "prompt": prompt, "channels": channels, "useBrandVoice": useBrandVoice}
    return await _get_client().call_tool(
        "generate_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def suggest_hashtags(
    workspaceId: str,
    topic: str,
    accountId: str | None = None,
    count: int = 10,
) -> Any:
    """Generate a set of hashtags for a topic or an existing post. The Wizard returns a list - use it to enrich a draft post, populate a post-creation tool's text, or just answer 'what hashtags should I use for X'.

Args:
    accountId:  Optional.
    workspaceId: Workspace id (required).
    topic: Topic or context the hashtags should fit, plain English. e.g. 'Black Friday sale on bath products'.
    count: How many hashtags to suggest. Default: 10. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "topic": topic, "count": count}
    return await _get_client().call_tool(
        "suggest_hashtags", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def rewrite(
    workspaceId: str,
    text: str,
    accountId: str | None = None,
    style: str = 'rephrase',
) -> Any:
    """Rewrite an existing post body - shorten, expand, or rephrase. Use when the user pastes a post and asks for a tweak ('make this shorter', 'tighten this up', 'rewrite more casually'). Returns the original + rewritten text so the LLM can show a diff.

Args:
    accountId:  Optional.
    workspaceId: Workspace id (required).
    text: Original post body to rewrite.
    style: How to rewrite. 'shorten' tightens, 'expand' adds detail, 'rephrase' rewords without changing length. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "text": text, "style": style}
    return await _get_client().call_tool(
        "rewrite", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def generate_image(
    workspaceId: str,
    prompt: str,
    accountId: str | None = None,
    style: str = 'generic',
    count: int = 4,
) -> Any:
    """Generate up to 4 images for a post. Use when the user says 'make me an image of...', 'I need a hero shot for...', 'create some visuals for the launch'. Counts against the user's monthly image-generation quota (same meter the AI Wizard uses).

Args:
    accountId:  Optional.
    workspaceId: Workspace id (required).
    prompt: What the image should depict, plain English. e.g. 'launch hero for our new pricing page, minimal flat illustration with our brand orange'.
    style: Visual style. Optional.
    count: How many image variants to generate. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "prompt": prompt, "style": style, "count": count}
    return await _get_client().call_tool(
        "generate_image", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def queue_pause(
    accountId: str | None = None,
    workspaceId: str | None = None,
    channelIds: list | None = None,
) -> Any:
    """Pause publishing on one or more channels. Future posts can't be scheduled on a paused channel, and any upcoming posts already in the queue will be held without firing. Use 'queue_resume' to bring the channel back online. When channelIds is omitted, every channel in the resolved workspace is paused.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account. Optional.
    workspaceId: Workspace id used as the fallback scope when channelIds isn't provided. Discover via 'get_workspaces'. Optional.
    channelIds: Specific channel ids to pause. Omit to pause every channel in the resolved workspace. Discover via 'get_channels'. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "channelIds": channelIds}
    return await _get_client().call_tool(
        "queue_pause", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def queue_resume(
    accountId: str | None = None,
    workspaceId: str | None = None,
    channelIds: list | None = None,
) -> Any:
    """Resume a previously-paused channel. Lifts the per-channel user-pause flag and releases held posts back to their original slots - except on channels where billing has independently locked publishing, which stay frozen. The response reports billingLockedChannels separately so you can tell the user when a billing issue is what's still blocking publishes.

Args:
    accountId: SocialChamp account id. Optional.
    workspaceId: Fallback workspace scope when channelIds isn't provided. Optional.
    channelIds: Specific channel ids to resume. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "channelIds": channelIds}
    return await _get_client().call_tool(
        "queue_resume", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=DESTRUCTIVE)
async def queue_clear(
    accountId: str | None = None,
    channelIds: list | None = None,
    fromDate: str | None = None,
    toDate: str | None = None,
    dryRun: bool = False,
) -> Any:
    """Bulk-delete upcoming scheduled posts in a date range, optionally filtered by channels. Defaults to fromDate=now (past posts are out of scope). Always call once with dryRun=true first to surface the count, then again with dryRun=false (or omitted) to actually delete - this is irreversible. Each delete also cancels its publish job.

Args:
    accountId: SocialChamp account id. Optional.
    channelIds: Optional channel-id filter. Omit to clear scheduled posts across every channel under the account. Optional.
    fromDate: ISO 8601 datetime. Defaults to now. Posts with dateTime >= fromDate are candidates. Optional.
    toDate: Optional ISO 8601 datetime. When set, only posts with dateTime <= toDate are candidates. Optional.
    dryRun: When true, count matching posts without deleting. Always start with this - the operation is destructive. Optional.
    """
    _args = {"accountId": accountId, "channelIds": channelIds, "fromDate": fromDate, "toDate": toDate, "dryRun": dryRun}
    return await _get_client().call_tool(
        "queue_clear", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def list_collections(
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """List the user's recycle collections. Each entry includes id, title, postCount and workspaceId. Use this before 'recycle_post' so the LLM can choose a target collection (or confirm the auto-resolved fallback).

Args:
    accountId: SocialChamp account id. Omit if the user has only one account. Optional.
    workspaceId: Optional workspace filter. When omitted, all of the account's collections are returned across workspaces. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId}
    return await _get_client().call_tool(
        "list_collections", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def recycle_post(
    postId: str,
    accountId: str | None = None,
    workspaceId: str | None = None,
    collectionId: str | None = None,
) -> Any:
    """Copy an existing post into a recycle collection so it re-publishes on the collection's recycle schedule. The original post is left untouched. If collectionId is omitted, the user's oldest collection in the resolved workspace is used; if the user has no collections, the response is a structured NEEDS_COLLECTION error so you can suggest creating one in the dashboard.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account. Optional.
    workspaceId: Optional workspace id to scope the fallback collection lookup. Ignored when collectionId is supplied. Optional.
    postId: Source post id to copy from (an existing PostSchedule). Get this via 'get_paginated_posts' / 'get_scheduled_posts'.
    collectionId: Optional target collection id. Omit to use the user's oldest collection in the resolved workspace. Discover ids via 'list_collections'. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "postId": postId, "collectionId": collectionId}
    return await _get_client().call_tool(
        "recycle_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def bulk_schedule(
    posts: list,
    accountId: str | None = None,
) -> Any:
    """Schedule many posts in one call (up to 100). Each entry has its own text, channels, image/video URLs, and optional schedule time - useful for rolling out a content calendar, importing a CSV, or filling a queue. After successful scheduling, ask whether to view the calendar or check the queue.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    posts: Array of post specs. Each entry is treated independently - a validation failure on one post stops the whole batch (atomic semantics).
    """
    _args = {"accountId": accountId, "posts": posts}
    return await _get_client().call_tool(
        "bulk_schedule", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def label_list(
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """List the post labels available in the user's workspace. Use this before applying a label to a post so the label exists. After listing, ask whether to create a new label, apply one to a post, or filter posts by label.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id to scope the label list. When omitted, the account's currently-selected workspace is used. Discover via 'get_workspaces' if the user has more than one. Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId}
    return await _get_client().call_tool(
        "label_list", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def label_create(
    title: str,
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """Create a new post label in the user's workspace. Returns the new label including its id, which can be used immediately with 'label_apply'. Errors with code DUPLICATE if a label with the same title (case-insensitive) already exists.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id where the label should be created. When omitted, the account's currently-selected workspace is used. Optional.
    title: Label title as the user wants it displayed. 1-40 characters; trimmed automatically.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "title": title}
    return await _get_client().call_tool(
        "label_create", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def label_apply(
    postId: str,
    labelIds: list,
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """Replace the labels on an existing post with the supplied list. Pass an empty `labelIds` to clear all labels from a post. The post must belong to the user's workspace.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id the post belongs to. When omitted, the account's currently-selected workspace is used. Optional.
    postId: Target post id. Get this from 'get_paginated_posts', 'get_scheduled_posts', or other read tools.
    labelIds: Label id values to attach to the post. Pass an empty array to clear all labels. Discover ids via 'label_list'.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "postId": postId, "labelIds": labelIds}
    return await _get_client().call_tool(
        "label_apply", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def label_remove(
    postId: str,
    labelIds: list,
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """Remove specific labels from a post (without touching the rest). Use when the user says 'unlabel this post', 'remove the X tag', 'drop the label'. Different from 'label_apply' which REPLACES the full label set; this tool subtracts the named ids from whatever is already on the post. Pass empty `labelIds` to clear all labels.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id the post belongs to. When omitted, the account's currently-selected workspace is used. Optional.
    postId: Target post id. Get this from 'get_paginated_posts', 'get_scheduled_posts', or other read tools.
    labelIds: Label ids to remove from the post. Empty array clears all labels. Discover ids via 'label_list'.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "postId": postId, "labelIds": labelIds}
    return await _get_client().call_tool(
        "label_remove", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def instagram_first_comment(
    postId: str,
    firstComment: str,
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """Set or update the first-comment text on a scheduled or published Instagram post. Common pattern: keep the caption clean and put hashtags + CTA + tracked link in the first comment. Only works on Instagram posts (FB_PAGE / TW / LinkedIn use captions directly). Replaces the existing first-comment if one is already set.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    workspaceId: Workspace id the post belongs to. When omitted, the account's currently-selected workspace is used. Optional.
    postId: Target IG post id (scheduled or published). The post's social_type MUST be IG_BUSINESS - anything else is rejected.
    firstComment: The first-comment body. ≤2200 chars per IG limits. Plain text + emoji + hashtags allowed; URLs become non-clickable in IG comments but still trigger linkified preview cards on some surfaces.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "postId": postId, "firstComment": firstComment}
    return await _get_client().call_tool(
        "instagram_first_comment", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=DESTRUCTIVE)
async def delete_shareable_calendar(
    calendarId: str,
    accountId: str | None = None,
    workspaceId: str | None = None,
) -> Any:
    """Delete a shareable calendar by calendarId.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    calendarId: Shareable calendar id to delete.
    workspaceId: Optional workspace id fallback for APIs that require workspace-scoped delete. Optional.
    """
    _args = {"accountId": accountId, "calendarId": calendarId, "workspaceId": workspaceId}
    return await _get_client().call_tool(
        "delete_shareable_calendar", {k: v for k, v in _args.items() if v is not None}
    )


def main() -> None:
    """Console entry point. Runs the server over the configured transport."""
    settings = load_settings()
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
