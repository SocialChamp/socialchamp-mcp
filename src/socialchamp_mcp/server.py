"""FastMCP server exposing the Social Champ MCP tool catalog.

GENERATED FILE. Do not edit by hand. Regenerate with:

    python scripts/generate_server.py

The tool catalog, names, argument names, and descriptions are generated from
tools.schema.json, a snapshot of the live server's api/mcp/tools.ts. Tools call
SocialChampClient.call_tool, which forwards the call to the hosted Social Champ
MCP server over JSON-RPC. The client is created lazily on first use and cached.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from .client import SocialChampClient
from .config import load_settings

mcp = FastMCP("socialchamp")

_client: SocialChampClient | None = None


def _validate_json_schema(value: object, schema: dict, path: str = "value") -> None:
    """Validate nested dictionary values that Pydantic otherwise treats as Any."""
    expected = schema.get("type")
    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        raise ValueError(f"{path} must be one of {enum}")

    if expected == "object":
        if not isinstance(value, dict):
            raise ValueError(f"{path} must be an object")
        properties = schema.get("properties") or {}
        for key in schema.get("required") or []:
            if key not in value:
                raise ValueError(f"{path}.{key} is required")
        if schema.get("additionalProperties") is False:
            unknown = next((key for key in value if key not in properties), None)
            if unknown is not None:
                raise ValueError(f"{path}.{unknown} is not supported")
        for key, nested in value.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                _validate_json_schema(nested, child_schema, f"{path}.{key}")
        return

    if expected == "array":
        if not isinstance(value, list):
            raise ValueError(f"{path} must be an array")
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ValueError(f"{path} must contain at least {minimum} items")
        if isinstance(maximum, int) and len(value) > maximum:
            raise ValueError(f"{path} must contain at most {maximum} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_json_schema(item, item_schema, f"{path}[{index}]")
        return

    if expected == "string":
        if not isinstance(value, str):
            raise ValueError(f"{path} must be a string")
        minimum = schema.get("minLength")
        maximum = schema.get("maxLength")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ValueError(f"{path} is too short")
        if isinstance(maximum, int) and len(value) > maximum:
            raise ValueError(f"{path} is too long")
        return

    if expected == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{path} must be a boolean")
    if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise ValueError(f"{path} must be an integer")
    if expected == "number" and (
        not isinstance(value, (int, float)) or isinstance(value, bool)
    ):
        raise ValueError(f"{path} must be a number")
    if expected in {"integer", "number"} and isinstance(value, (int, float)):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            raise ValueError(f"{path} is below the minimum")
        if isinstance(maximum, (int, float)) and value > maximum:
            raise ValueError(f"{path} is above the maximum")


def _json_schema_validator(schema: dict):
    def validate(value: object) -> object:
        _validate_json_schema(value, schema)
        return value

    return validate


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
    imageUrls: list[str],
    channelIds: list[str],
    accountId: str | None = None,
    videoUrls: list[str] | None = None,
    dateTime: str | None = None,
    saveAsDraft: bool = False,
    isScheduled: bool = False,
    location: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': "Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts. Resolve it FIRST via the 'location_search' tool and pass the returned object — only the `id` is applied when publishing; a bare name/place without a valid platform `id` is stored but NOT tagged on the post. Other platforms ignore this field.", 'properties': {'id': {'type': 'string', 'description': 'Platform location/place id.'}, 'name': {'type': 'string', 'description': 'Human-readable location name.'}, 'place': {'type': 'string', 'description': 'Optional platform-specific place payload/name when available.'}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'id': {'type': 'string', 'description': 'Platform location/place id.'}, 'name': {'type': 'string', 'description': 'Human-readable location name.'}, 'place': {'type': 'string', 'description': 'Optional platform-specific place payload/name when available.'}}, 'additionalProperties': False})] | None = None,
    firstComment: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': 'Optional auto-first-comment. Lights up on every channel in this post that supports it: Instagram, LinkedIn (page + personal), Facebook page, YouTube, TikTok. Other platforms (X, BlueSky, Mastodon, Pinterest, Threads, Google Business) silently ignore the field. Each platform enforces its own char limit at publish time (IG 2200, FB 2000, LI 1250, TikTok 150).', 'properties': {'text': {'type': 'string', 'description': 'First-comment body. Same text is used on every supporting platform.'}, 'media': {'type': 'string', 'description': 'Optional publicly-accessible URL to attach to the first comment. Honoured only on LinkedIn and Facebook; ignored on Instagram, YouTube, TikTok.'}, 'delayMinutes': {'type': 'integer', 'minimum': 0, 'description': 'Optional delay in minutes after the main post is published before the first comment fires. Honoured on LinkedIn, Facebook, YouTube, TikTok (and Instagram via igExtras.commentDelay where supported).'}}, 'required': ['text'], 'additionalProperties': False})), Field(json_schema_extra={'properties': {'text': {'type': 'string', 'description': 'First-comment body. Same text is used on every supporting platform.'}, 'media': {'type': 'string', 'description': 'Optional publicly-accessible URL to attach to the first comment. Honoured only on LinkedIn and Facebook; ignored on Instagram, YouTube, TikTok.'}, 'delayMinutes': {'type': 'integer', 'minimum': 0, 'description': 'Optional delay in minutes after the main post is published before the first comment fires. Honoured on LinkedIn, Facebook, YouTube, TikTok (and Instagram via igExtras.commentDelay where supported).'}}, 'required': ['text'], 'additionalProperties': False})] | None = None,
    instaFirstComment: str | None = None,
    contentType: Literal['POST', 'REEL', 'REEL_FEED', 'STORY'] | None = None,
    channelOptions: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': 'Optional platform-specific Reel and Short settings. These values override the legacy global contentType for their platform. Omit global contentType when every target platform is configured here.', 'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'required': ['contentType', 'title', 'madeForKids'], 'additionalProperties': False}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'required': ['contentType', 'title', 'madeForKids'], 'additionalProperties': False}}, 'additionalProperties': False})] | None = None,
) -> Any:
    """Create and optionally schedule an image post to one or more channels. To save it for later review instead of publishing, set saveAsDraft=true; the draft lands in Publish > Drafts and never publishes on its own. After successful scheduling, ask whether to view posting calendar, check scheduled posts, or create another post.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    text: Caption or post text to publish with the images; provide plain text as entered by the user.
    imageUrls: Publicly accessible image URL strings to attach to the post (e.g. 'https://example.com/image.jpg').
    videoUrls: Publicly accessible video URL strings. Required for Facebook Reels, YouTube videos/Shorts, global REEL/REEL_FEED, and Instagram cover-frame selection. An Instagram-only Reel may instead use one image for image-to-Reel conversion. Optional.
    channelIds: Target channel id values where the post should be published; obtain these from 'get_channels' or 'get_filtered_channels'.
    dateTime: ISO 8601 date-time with a timezone for when to publish (e.g. '2026-04-10T14:00:00Z' or '2026-04-10T19:00:00+05:00'). Required when isScheduled is true. Omit to post immediately. With saveAsDraft=true it is optional and records the draft's intended date without scheduling anything. Optional.
    saveAsDraft: Set to true to save the post as an editable draft instead of publishing or scheduling it. The draft appears in Publish > Drafts and can be opened in the composer to add media or edit the text before it goes out. Nothing publishes a draft on its own. Cannot be combined with isScheduled=true; pass dateTime on its own to record an intended date on the draft. Optional.
    isScheduled: Set to true to schedule the post for a future dateTime. Set to false or omit to post immediately. When true, dateTime is required. Optional.
    location: Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts. Resolve it FIRST via the 'location_search' tool and pass the returned object - only the `id` is applied when publishing; a bare name/place without a valid platform `id` is stored but NOT tagged on the post. Other platforms ignore this field. Optional.
    firstComment: Optional auto-first-comment. Lights up on every channel in this post that supports it: Instagram, LinkedIn (page + personal), Facebook page, YouTube, TikTok. Other platforms (X, BlueSky, Mastodon, Pinterest, Threads, Google Business) silently ignore the field. Each platform enforces its own char limit at publish time (IG 2200, FB 2000, LI 1250, TikTok 150). Optional.
    instaFirstComment: DEPRECATED - pass `firstComment: { text }` instead. Kept for backwards compatibility; if both are present, `firstComment` wins. Optional.
    contentType: Legacy cross-platform fallback. REEL maps to Instagram/Facebook Reels and YouTube Shorts; REEL_FEED also shows the Instagram Reel in feed. Use channelOptions for platform-specific choices and omit this fallback when each target platform is configured there. If neither field is supplied, the request creates a regular feed post. REEL and REEL_FEED require videoUrls. Optional.
    channelOptions: Optional platform-specific Reel and Short settings. These values override the legacy global contentType for their platform. Omit global contentType when every target platform is configured here. Optional.
    """
    _args = {"accountId": accountId, "text": text, "imageUrls": imageUrls, "videoUrls": videoUrls, "channelIds": channelIds, "dateTime": dateTime, "saveAsDraft": saveAsDraft, "isScheduled": isScheduled, "location": location, "firstComment": firstComment, "instaFirstComment": instaFirstComment, "contentType": contentType, "channelOptions": channelOptions}
    return await _get_client().call_tool(
        "create_image_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def create_text_post(
    text: str,
    channelIds: list[str],
    accountId: str | None = None,
    videoUrls: list[str] | None = None,
    dateTime: str | None = None,
    saveAsDraft: bool = False,
    isScheduled: bool = False,
    location: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': "Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts. Resolve it FIRST via the 'location_search' tool and pass the returned object — only the `id` is applied when publishing; a bare name/place without a valid platform `id` is stored but NOT tagged on the post. Other platforms ignore this field.", 'properties': {'id': {'type': 'string', 'description': 'Platform location/place id.'}, 'name': {'type': 'string', 'description': 'Human-readable location name.'}, 'place': {'type': 'string', 'description': 'Optional platform-specific place payload/name when available.'}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'id': {'type': 'string', 'description': 'Platform location/place id.'}, 'name': {'type': 'string', 'description': 'Human-readable location name.'}, 'place': {'type': 'string', 'description': 'Optional platform-specific place payload/name when available.'}}, 'additionalProperties': False})] | None = None,
    firstComment: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': 'Optional auto-first-comment. Lights up on every channel in this post that supports it: Instagram, LinkedIn, Facebook page, YouTube, TikTok. Other platforms silently ignore the field. Per-platform char limits enforced at publish time.', 'properties': {'text': {'type': 'string'}, 'media': {'type': 'string', 'description': 'Optional URL to attach. Honoured on LinkedIn and Facebook only.'}, 'delayMinutes': {'type': 'integer', 'minimum': 0}}, 'required': ['text'], 'additionalProperties': False})), Field(json_schema_extra={'properties': {'text': {'type': 'string'}, 'media': {'type': 'string', 'description': 'Optional URL to attach. Honoured on LinkedIn and Facebook only.'}, 'delayMinutes': {'type': 'integer', 'minimum': 0}}, 'required': ['text'], 'additionalProperties': False})] | None = None,
    instaFirstComment: str | None = None,
    contentType: Literal['POST', 'REEL', 'REEL_FEED', 'STORY'] | None = None,
    coverMediaId: str | None = None,
    channelOptions: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': 'Optional platform-specific Reel and Short settings. These values override the legacy global contentType for their platform. Omit global contentType when every target platform is configured here.', 'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'required': ['contentType', 'title', 'madeForKids'], 'additionalProperties': False}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'required': ['contentType', 'title', 'madeForKids'], 'additionalProperties': False}}, 'additionalProperties': False})] | None = None,
) -> Any:
    """Create and optionally schedule a text post to one or more channels. Select channelIds from get_channels or get_filtered_channels in the requested workspace. This tool does not accept workspaceId; do not pass it or substitute a workspace id for accountId. To schedule, set isScheduled=true and dateTime to the confirmed future ISO 8601 timestamp with timezone. To save it for later review instead of publishing, set saveAsDraft=true; the draft lands in Publish > Drafts and never publishes on its own. After successful scheduling, verify with get_scheduled_posts. Do not blindly retry an uncertain creation result; check for the created post first.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    text: Post text content to publish exactly as the user wants it posted.
    channelIds: Target channel id values where the post should be published; obtain these from 'get_channels' or 'get_filtered_channels'.
    videoUrls: Publicly accessible video URL strings. Required for Facebook Reels, YouTube videos/Shorts, global REEL/REEL_FEED, and Instagram cover-frame selection. An Instagram-only Reel may instead use one image for image-to-Reel conversion. Optional.
    dateTime: ISO 8601 date-time with a timezone for when to publish (e.g. '2026-04-10T14:00:00Z' or '2026-04-10T19:00:00+05:00'). Required when isScheduled is true. Omit to post immediately. With saveAsDraft=true it is optional and records the draft's intended date without scheduling anything. Optional.
    saveAsDraft: Set to true to save the post as an editable draft instead of publishing or scheduling it. The draft appears in Publish > Drafts and can be opened in the composer to add media or edit the text before it goes out. Nothing publishes a draft on its own. Cannot be combined with isScheduled=true; pass dateTime on its own to record an intended date on the draft. Optional.
    isScheduled: Set to true to schedule the post for a future dateTime. Set to false or omit to post immediately. When true, dateTime is required. Optional.
    location: Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts. Resolve it FIRST via the 'location_search' tool and pass the returned object - only the `id` is applied when publishing; a bare name/place without a valid platform `id` is stored but NOT tagged on the post. Other platforms ignore this field. Optional.
    firstComment: Optional auto-first-comment. Lights up on every channel in this post that supports it: Instagram, LinkedIn, Facebook page, YouTube, TikTok. Other platforms silently ignore the field. Per-platform char limits enforced at publish time. Optional.
    instaFirstComment: DEPRECATED - pass `firstComment: { text }` instead. Kept for backwards compatibility. Optional.
    contentType: Legacy cross-platform fallback. REEL maps to Instagram/Facebook Reels and YouTube Shorts; REEL_FEED also shows the Instagram Reel in feed. Use channelOptions for platform-specific choices and omit this fallback when each target platform is configured there. If neither field is supplied, the request creates a regular feed post. REEL and REEL_FEED require videoUrls. Optional.
    coverMediaId: Optional custom cover for a video post. Pass the media id returned by complete_media_upload or import_media_from_url; a plain image URL is not accepted. The image must already have been uploaded through those tools. Only valid with exactly one videoUrl and no imageUrls. Must be a JPG or PNG of 2 MB or less. Applied as the cover on Instagram reels, TikTok, YouTube, Facebook reels, LinkedIn and Pinterest; channels with no cover concept ignore it. On TikTok, LinkedIn and Facebook feed video, an unusable cover fails the post. On YouTube and Facebook reels, a cover failure is silent and the post still publishes without it. Omit it to let the platform pick a frame automatically. Optional.
    channelOptions: Optional platform-specific Reel and Short settings. These values override the legacy global contentType for their platform. Omit global contentType when every target platform is configured here. Optional.
    """
    _args = {"accountId": accountId, "text": text, "channelIds": channelIds, "videoUrls": videoUrls, "dateTime": dateTime, "saveAsDraft": saveAsDraft, "isScheduled": isScheduled, "location": location, "firstComment": firstComment, "instaFirstComment": instaFirstComment, "contentType": contentType, "coverMediaId": coverMediaId, "channelOptions": channelOptions}
    return await _get_client().call_tool(
        "create_text_post", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=UPDATE)
async def update_post(
    postId: str,
    accountId: str | None = None,
    text: str | None = None,
    dateTime: str | None = None,
    channelId: str | None = None,
    channelIds: Annotated[list[str], Field(max_length=1)] | None = None,
    imageUrls: list[str] | None = None,
    videoUrls: list[str] | None = None,
    coverMediaId: str | None = None,
    channelOptions: Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'description': 'Optional platform-specific Reel and Short settings to update. Supply only the fields that should change.', 'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'additionalProperties': False}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'additionalProperties': False}}, 'additionalProperties': False})] | None = None,
) -> Any:
    """Update an existing post by postId. Text maps to upstream message, and the post profile is auto-resolved from the existing post unless one channelId override is provided. Changing an approval-managed post can return it to pending approval.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    postId: Post id to update.
    text: Updated text/caption for the post. Optional.
    dateTime: Updated ISO 8601 schedule date-time with a timezone (e.g. '2026-04-18T14:00:00Z'). Optional.
    channelId: Optional target channel override. Omit to keep the channel already attached to the post. Optional.
    channelIds: Deprecated compatibility field. Pass at most one channel id; prefer channelId. Optional.
    imageUrls: Updated image URL list for media posts. Optional.
    videoUrls: Updated video URL list for video posts. Optional.
    coverMediaId: Updated custom video cover. Pass the media id returned by complete_media_upload or import_media_from_url. Requires exactly one video and no images. Optional.
    channelOptions: Optional platform-specific Reel and Short settings to update. Supply only the fields that should change. Optional.
    """
    _args = {"accountId": accountId, "postId": postId, "text": text, "dateTime": dateTime, "channelId": channelId, "channelIds": channelIds, "imageUrls": imageUrls, "videoUrls": videoUrls, "coverMediaId": coverMediaId, "channelOptions": channelOptions}
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
    types: list[str] | None = None,
    search: str | None = None,
) -> Any:
    """List channels filtered by platform types and/or text search. After results, suggest creating a post or viewing posts for those channels.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    types: Filter by platform names ('twitter','facebook','linkedin','instagram','tiktok','youtube','pinterest','bluesky','threads','mastodon','google','telegram') or internal codes ('TW','FB_PAGE','IN', etc.). Names are case-insensitive. Optional.
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
    channelIds: Annotated[list[str], Field(min_length=1, max_length=100)] | None = None,
    status: Literal['POSTED', 'FAILED', 'PENDING_APPROVAL', 'HELD', 'MANUAL_NOTIFICATION', 'SCHEDULED', 'IN_PROGRESS'] | None = None,
    hasError: bool | None = None,
    labelIds: Annotated[list[str], Field(min_length=1, max_length=100)] | None = None,
    approvalStatus: Literal['PENDING', 'APPROVED', 'DECLINED'] | None = None,
    slim: bool = False,
    page: float = 1,
    pageSize: float = 20,
    fromDate: str | None = None,
    toDate: str | None = None,
) -> Any:
    """Browse post history with channel, status, error, label and approval filters applied before pagination. Statuses are mutually exclusive. Drafts are separate: use get_drafts. Use get_calendar_summary for daily counts in one call.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    channelIds: Narrow to these Social Champ channel ids. Optional.
    status:  Optional.
    hasError:  Optional.
    labelIds: Match any of these label ids. Optional.
    approvalStatus:  Optional.
    slim: Omit channelOptions and media URL arrays. Optional.
    page: 1-based page number to fetch. Omit to use the first page. Optional.
    pageSize: Maximum number of posts to return per page. Omit to use the default page size. Optional.
    fromDate: Optional ISO 8601 start date-time filter (inclusive), e.g. '2026-04-01T00:00:00Z'. Optional.
    toDate: Optional ISO 8601 end date-time filter (inclusive), e.g. '2026-04-30T23:59:59Z'. Optional.
    """
    _args = {"accountId": accountId, "channelIds": channelIds, "status": status, "hasError": hasError, "labelIds": labelIds, "approvalStatus": approvalStatus, "slim": slim, "page": page, "pageSize": pageSize, "fromDate": fromDate, "toDate": toDate}
    return await _get_client().call_tool(
        "get_paginated_posts", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_posts_for_channels(
    channelIds: list[str],
    accountId: str | None = None,
    limit: float = 50,
    fromDate: str | None = None,
    toDate: str | None = None,
    livePosts: bool = False,
) -> Any:
    """Fetch posts scoped to specific channelIds with an optional limit. Returns posts scheduled through Social Champ only; set livePosts to true to also include content the customer published straight to the network. If a user says posts are missing here but visible in their Social Champ calendar or live on the network, retry with livePosts set to true. After results, suggest creating a post or checking scheduled posts.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    channelIds: Channel id values to scope results to; obtain these from 'get_channels' or 'get_filtered_channels'.
    limit: Maximum number of posts to return across the selected channels. Omit to use the default limit. Optional.
    fromDate: Optional ISO 8601 start date-time filter (inclusive), e.g. '2026-04-01T00:00:00Z'. Optional.
    toDate: Optional ISO 8601 end date-time filter (inclusive), e.g. '2026-04-30T23:59:59Z'. Optional.
    livePosts: Include content published straight to the network rather than through Social Champ - posts made from the Instagram app, Meta Business Suite, or another scheduler. Off by default. These posts cannot be edited or deleted, and their ids are prefixed with 'live_'. Optional.
    """
    _args = {"accountId": accountId, "channelIds": channelIds, "limit": limit, "fromDate": fromDate, "toDate": toDate, "livePosts": livePosts}
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
    """Fetch upcoming scheduled posts, soonest first with a stable id tie-break. Past dates do not widen the upcoming window.

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
async def get_calendar_summary(
    fromDate: str,
    toDate: str,
    accountId: str | None = None,
    channelIds: Annotated[list[str], Field(min_length=1, max_length=100)] | None = None,
    timezone: str | None = None,
) -> Any:
    """Read sparse counts by calendar day, channel and mutually exclusive status in one call. Date range is required and limited to 93 days. Missing combinations mean zero. Excludes deleted posts and drafts. Held, manual-notification and overdue in-progress posts are separate from scheduled and failed posts.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    fromDate: Inclusive ISO 8601 date-time with timezone.
    toDate: Inclusive ISO 8601 date-time with timezone.
    channelIds: Narrow to these Social Champ channel ids. Optional.
    timezone: IANA timezone for day boundaries; defaults to UTC. Optional.
    """
    _args = {"accountId": accountId, "fromDate": fromDate, "toDate": toDate, "channelIds": channelIds, "timezone": timezone}
    return await _get_client().call_tool(
        "get_calendar_summary", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_post_metrics(
    postIds: Annotated[list[str], Field(min_length=1, max_length=20)],
    accountId: str | None = None,
) -> Any:
    """Read cached engagement metrics for up to 20 Social Champ scheduled-post ids. Uses existing analytics plan and profile access gates. Missing metrics are unavailable, never zero; this does not refresh provider data. Currently available to owner connections only; delegated Admin connections are rejected because the Publisher HTTP bridge does not preserve team visibility.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    postIds: PostSchedule ids from get_paginated_posts; provider ids and live_ ids are not accepted.
    """
    _args = {"accountId": accountId, "postIds": postIds}
    return await _get_client().call_tool(
        "get_post_metrics", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_drafts(
    workspaceId: str,
    accountId: str | None = None,
    channelIds: Annotated[list[str], Field(min_length=1, max_length=100)] | None = None,
    page: Annotated[int, Field(ge=1, le=10000)] = 1,
    pageSize: Annotated[int, Field(ge=1, le=100)] = 20,
) -> Any:
    """List saved Publish drafts in a workspace with existing creator/privacy visibility rules. Excludes rolling composer autosaves. Drafts are not returned by get_paginated_posts. Currently available to owner connections only; delegated Admin connections are rejected because the Publisher HTTP bridge does not preserve team visibility.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    workspaceId: Workspace id from get_workspaces.
    channelIds: Narrow to these Social Champ channel ids. Optional.
    page:  Optional.
    pageSize:  Optional.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "channelIds": channelIds, "page": page, "pageSize": pageSize}
    return await _get_client().call_tool(
        "get_drafts", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_queue_slots(
    channelId: str,
    accountId: str | None = None,
) -> Any:
    """Read the channel queue timetable, weekday enabled flags and timezone. A null timetable means none is configured; stored slots are recurring local-time templates, not reserved future publish dates.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    channelId: Social Champ channel id.
    """
    _args = {"accountId": accountId, "channelId": channelId}
    return await _get_client().call_tool(
        "get_queue_slots", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_best_times(
    channelId: str,
    fromDate: str,
    toDate: str,
    accountId: str | None = None,
    timezone: str | None = None,
) -> Any:
    """Read the existing analytics best-time heat map for a channel over at most 93 days. This is historical engagement data, not a guarantee or an available queue slot. Unsupported or insufficient history may return no data. Currently available to owner connections only; delegated Admin connections are rejected because the Publisher HTTP bridge does not preserve team visibility.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    channelId: Social Champ channel id.
    fromDate: Inclusive ISO 8601 date-time with timezone.
    toDate: Inclusive ISO 8601 date-time with timezone.
    timezone: IANA timezone; defaults to UTC. Optional.
    """
    _args = {"accountId": accountId, "channelId": channelId, "fromDate": fromDate, "toDate": toDate, "timezone": timezone}
    return await _get_client().call_tool(
        "get_best_times", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_calendar_events(
    workspaceId: str,
    fromDate: str,
    toDate: str,
    accountId: str | None = None,
) -> Any:
    """Read public holidays configured for an owned workspace over at most 93 days. This returns the web calendar holiday markers, not calendar notes. An empty list means holidays are disabled or none match.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    workspaceId: Workspace id.
    fromDate: Inclusive ISO 8601 date-time with timezone.
    toDate: Inclusive ISO 8601 date-time with timezone.
    """
    _args = {"accountId": accountId, "workspaceId": workspaceId, "fromDate": fromDate, "toDate": toDate}
    return await _get_client().call_tool(
        "get_calendar_events", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=READ)
async def get_post_comments(
    postId: str,
    accountId: str | None = None,
    page: Annotated[int, Field(ge=1, le=10000)] = 1,
    pageSize: Annotated[int, Field(ge=1, le=100)] = 20,
) -> Any:
    """Read a bounded page of already-ingested Engage comments for a published Social Champ post. Uses existing profile and X Suite gates. An empty list does not prove the network has no comments; this never refreshes or replies. Currently available to owner connections only; delegated Admin connections are rejected because the Publisher HTTP bridge does not preserve team visibility.

Args:
    accountId: Optional account id. Defaults to the connected account. Optional.
    postId: PostSchedule id from get_paginated_posts.
    page:  Optional.
    pageSize:  Optional.
    """
    _args = {"accountId": accountId, "postId": postId, "page": page, "pageSize": pageSize}
    return await _get_client().call_tool(
        "get_post_comments", {k: v for k, v in _args.items() if v is not None}
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
    """List existing shareable calendars for a workspace. Each record includes _id (database identifier for update/delete) and calendarId (public-link UUID, not a mutation identifier). Pass the record's _id as the calendarId argument to update_shareable_calendar or delete_shareable_calendar. After results, suggest creating a new link or opening calendar views.

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
    profileIds: list[str],
    fromDate: str,
    toDate: str,
    accountId: str | None = None,
    password: str | None = None,
    permissionRoles: list[Literal['EDIT', 'DELETE', 'APPROVE']] | None = None,
    isActive: bool = True,
) -> Any:
    """Create a shareable public calendar link for selected channels and date range. Returns _id for update/delete and calendarId for the public link; these identifiers are not interchangeable. Before creating, ask whether the link should be password protected or open; if protected, collect an 8-20 character password.

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
async def get_post_app_url(
    postId: str,
    accountId: str | None = None,
) -> Any:
    """Return an authenticated Social Champ preview link for a scheduled, failed, pending or published Social Champ post. Native live_ posts and drafts are not supported. Sign in to the connected account before opening the link.

Args:
    accountId:  Optional.
    postId:
    """
    _args = {"accountId": accountId, "postId": postId}
    return await _get_client().call_tool(
        "get_post_app_url", {k: v for k, v in _args.items() if v is not None}
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
    permissionRoles: list[Literal['EDIT', 'DELETE', 'APPROVE']] | None = None,
    isActive: bool | None = None,
) -> Any:
    """Update a shareable calendar using its database _id as the calendarId argument, not its public-link UUID, including name, date range, password, isActive, or permissionRoles.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    calendarId: Database _id returned by create_public_calendar_link or get_shareable_calendars. Do not use the public calendarId UUID or the id query parameter from the shareable link.
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
    status: Literal['PENDING', 'APPROVED', 'DECLINED'] = 'PENDING',
    profileIds: list[str] | None = None,
    teamMemberIds: list[str] | None = None,
    start: Annotated[int, Field(ge=0)] = 0,
    limit: Annotated[int, Field(ge=1, le=50)] = 25,
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
    postIds: list[str] | None = None,
    channelIds: list[str] | None = None,
    fromDate: str | None = None,
    toDate: str | None = None,
    status: Literal['DRAFT', 'SCHEDULED', 'POSTED', 'FAILED'] | None = None,
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
    items: Annotated[list[Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'required': ['postId', 'dateTime'], 'properties': {'postId': {'type': 'string'}, 'dateTime': {'type': 'string', 'description': 'ISO 8601 datetime to reschedule to.'}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'postId': {'type': 'string'}, 'dateTime': {'type': 'string', 'description': 'ISO 8601 datetime to reschedule to.'}}, 'required': ['postId', 'dateTime'], 'additionalProperties': False})]], Field(min_length=1, max_length=100)],
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
    postIds: Annotated[list[str], Field(min_length=1, max_length=200)],
    labelIds: list[str],
    accountId: str | None = None,
    mode: Literal['replace', 'add'] = 'replace',
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
    channels: list[str] | None = None,
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
    count: Annotated[int, Field(ge=1, le=30)] = 10,
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
    style: Literal['shorten', 'expand', 'rephrase'] = 'rephrase',
) -> Any:
    """Rewrite an existing post body - shorten, expand, or rephrase. Use for user-provided text or a draft returned by generate_post earlier in the conversation when the user requests Social Champ AI rewriting. Pass that draft as text and its workspaceId; use style='shorten' for a shorter version. Returns the original + rewritten text. Show the returned rewrite rather than substituting your own copy. Does not create, schedule or publish a post.

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
    style: Literal['generic', 'art', 'photo', 'abstract'] = 'generic',
    count: Annotated[int, Field(ge=1, le=4)] = 4,
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
    channelIds: list[str] | None = None,
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
    channelIds: list[str] | None = None,
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
    channelIds: list[str] | None = None,
    fromDate: str | None = None,
    toDate: str | None = None,
    dryRun: bool = True,
) -> Any:
    """Bulk-delete upcoming scheduled posts in a date range, optionally filtered by channels. Defaults to fromDate=now (past posts are out of scope). DESTRUCTIVE: defaults to dryRun=true, which surfaces the count without deleting; the LLM MUST explicitly pass dryRun=false to actually delete after the user confirms. A real delete must also be bounded - pass channelIds, or both fromDate and toDate - so re-send the dry run's filters alongside dryRun=false rather than dryRun=false on its own. This is irreversible, and each delete also cancels its publish job.

Args:
    accountId: SocialChamp account id. Optional.
    channelIds: Channel-id filter. Omitting it means every channel under the account, which is allowed only for a dry run: a real clear needs either channelIds or a fromDate+toDate window. Optional.
    fromDate: ISO 8601 datetime. Defaults to now. Posts with dateTime >= fromDate are candidates. Optional.
    toDate: Optional ISO 8601 datetime. When set, only posts with dateTime <= toDate are candidates. Optional.
    dryRun: When true (default), returns the count without deleting. Pass false to actually clear the queue - irreversible. Optional.
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
    posts: Annotated[list[Annotated[dict[str, object], BeforeValidator(_json_schema_validator({'type': 'object', 'required': ['text', 'channelIds'], 'properties': {'text': {'type': 'string', 'description': 'Post body. Per-platform limits are enforced server-side.'}, 'channelIds': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'description': "Channel ids to publish on; obtain via 'get_channels'. The scheduler creates one post per channel."}, 'imageUrls': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Optional publicly-accessible image URLs to attach.'}, 'videoUrls': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Publicly accessible video URL strings. Required for Facebook Reels, YouTube videos/Shorts, global REEL/REEL_FEED, and Instagram cover-frame selection. An Instagram-only Reel may instead use one image for image-to-Reel conversion.'}, 'dateTime': {'type': 'string', 'minLength': 1, 'description': 'ISO 8601 datetime with a timezone to publish at. Required when isScheduled is true.'}, 'isScheduled': {'type': 'boolean', 'description': 'When true, the post is scheduled at dateTime. When false or omitted, the post is published immediately.', 'default': False}, 'location': {'type': 'object', 'description': "Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts in this entry. Resolve via the 'location_search' tool and pass the returned object — only the `id` is applied at publish; a bare name/place is ignored. Other platforms ignore this field.", 'properties': {'id': {'type': 'string', 'description': 'Platform location/place id.'}, 'name': {'type': 'string', 'description': 'Human-readable location name.'}, 'place': {'type': 'string', 'description': 'Optional platform-specific place payload/name when available.'}}, 'additionalProperties': False}, 'firstComment': {'type': 'object', 'description': "Optional auto-first-comment. Lights up on every supporting platform in this entry's channels (IG, LinkedIn, Facebook, YouTube, TikTok).", 'properties': {'text': {'type': 'string'}, 'media': {'type': 'string'}, 'delayMinutes': {'type': 'integer', 'minimum': 0}}, 'required': ['text'], 'additionalProperties': False}, 'instaFirstComment': {'type': 'string', 'description': 'DEPRECATED — pass `firstComment: { text }` instead.'}, 'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Legacy cross-platform fallback for this entry. Use channelOptions for platform-specific choices and omit this fallback when each target platform is configured there. If neither field is supplied, the entry creates a regular feed post. REEL and REEL_FEED require videoUrls.'}, 'coverMediaId': {'type': 'string', 'description': "Optional custom cover for this entry's video. Pass the media id returned by complete_media_upload or import_media_from_url; a plain image URL is not accepted. Only valid with exactly one videoUrl and no imageUrls. Must be a JPG or PNG of 2 MB or less. One id per entry, so a batch can give every video its own cover. See create_text_post's coverMediaId for per-platform behaviour."}, 'channelOptions': {'type': 'object', 'description': 'Optional platform-specific Reel and Short settings. These values override the legacy global contentType for their platform. Omit global contentType when every target platform is configured here.', 'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'required': ['contentType', 'title', 'madeForKids'], 'additionalProperties': False}}, 'additionalProperties': False}}, 'additionalProperties': False})), Field(json_schema_extra={'properties': {'text': {'type': 'string', 'description': 'Post body. Per-platform limits are enforced server-side.'}, 'channelIds': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'description': "Channel ids to publish on; obtain via 'get_channels'. The scheduler creates one post per channel."}, 'imageUrls': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Optional publicly-accessible image URLs to attach.'}, 'videoUrls': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Publicly accessible video URL strings. Required for Facebook Reels, YouTube videos/Shorts, global REEL/REEL_FEED, and Instagram cover-frame selection. An Instagram-only Reel may instead use one image for image-to-Reel conversion.'}, 'dateTime': {'type': 'string', 'minLength': 1, 'description': 'ISO 8601 datetime with a timezone to publish at. Required when isScheduled is true.'}, 'isScheduled': {'type': 'boolean', 'description': 'When true, the post is scheduled at dateTime. When false or omitted, the post is published immediately.', 'default': False}, 'location': {'type': 'object', 'description': "Optional location tag for FB_PAGE, IG_BUSINESS, and IG_DIRECT posts in this entry. Resolve via the 'location_search' tool and pass the returned object — only the `id` is applied at publish; a bare name/place is ignored. Other platforms ignore this field.", 'properties': {'id': {'type': 'string', 'description': 'Platform location/place id.'}, 'name': {'type': 'string', 'description': 'Human-readable location name.'}, 'place': {'type': 'string', 'description': 'Optional platform-specific place payload/name when available.'}}, 'additionalProperties': False}, 'firstComment': {'type': 'object', 'description': "Optional auto-first-comment. Lights up on every supporting platform in this entry's channels (IG, LinkedIn, Facebook, YouTube, TikTok).", 'properties': {'text': {'type': 'string'}, 'media': {'type': 'string'}, 'delayMinutes': {'type': 'integer', 'minimum': 0}}, 'required': ['text'], 'additionalProperties': False}, 'instaFirstComment': {'type': 'string', 'description': 'DEPRECATED — pass `firstComment: { text }` instead.'}, 'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Legacy cross-platform fallback for this entry. Use channelOptions for platform-specific choices and omit this fallback when each target platform is configured there. If neither field is supplied, the entry creates a regular feed post. REEL and REEL_FEED require videoUrls.'}, 'coverMediaId': {'type': 'string', 'description': "Optional custom cover for this entry's video. Pass the media id returned by complete_media_upload or import_media_from_url; a plain image URL is not accepted. Only valid with exactly one videoUrl and no imageUrls. Must be a JPG or PNG of 2 MB or less. One id per entry, so a batch can give every video its own cover. See create_text_post's coverMediaId for per-platform behaviour."}, 'channelOptions': {'type': 'object', 'description': 'Optional platform-specific Reel and Short settings. These values override the legacy global contentType for their platform. Omit global contentType when every target platform is configured here.', 'properties': {'instagram': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'REEL_FEED', 'STORY'], 'description': 'Instagram post type.'}, 'placement': {'type': 'string', 'enum': ['REEL_ONLY', 'REEL_AND_FEED'], 'description': 'Where an Instagram Reel appears. REEL_AND_FEED also shows it in the Instagram feed.'}, 'coverFrameTimeSeconds': {'type': 'number', 'minimum': 0, 'description': 'Video timestamp, in seconds, used for the Instagram Reel cover frame.'}, 'collaborators': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}, 'description': 'Up to five Instagram collaborator usernames. Set Instagram contentType to REEL or REEL_FEED (or use Reel placement). A leading @ is optional.'}}, 'additionalProperties': False}, 'facebook': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['POST', 'REEL', 'STORY'], 'description': 'Facebook Page post type.'}, 'collaborators': {'type': 'array', 'maxItems': 1, 'items': {'type': 'string'}, 'description': 'One Facebook Page collaborator identifier. Set Facebook contentType to REEL.'}}, 'additionalProperties': False}, 'youtube': {'type': 'object', 'properties': {'contentType': {'type': 'string', 'enum': ['VIDEO', 'SHORT'], 'description': 'Publish as a standard YouTube video or a Short.'}, 'title': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'description': 'YouTube video title. Ask the user if they have not provided one; do not invent it.'}, 'thumbnailUrl': {'type': 'string', 'description': 'Publicly accessible custom YouTube thumbnail URL.'}, 'privacyStatus': {'type': 'string', 'enum': ['PUBLIC', 'PRIVATE', 'UNLISTED'], 'description': 'YouTube visibility.'}, 'madeForKids': {'type': 'boolean', 'description': 'Whether the YouTube video or Short is made for kids. Ask the user when unknown; never guess this value.'}, 'notifySubscribers': {'type': 'boolean', 'description': 'Whether YouTube should notify subscribers when the video publishes.'}}, 'required': ['contentType', 'title', 'madeForKids'], 'additionalProperties': False}}, 'additionalProperties': False}}, 'required': ['text', 'channelIds'], 'additionalProperties': False})]], Field(min_length=1, max_length=100)],
    accountId: str | None = None,
) -> Any:
    """Schedule many posts in one call (up to 100). Each entry has its own text, channels, image/video URLs, and optional schedule time - useful for rolling out a content calendar, importing a CSV, or filling a queue. After successful scheduling, ask whether to view the calendar or check the queue. Drafts are not supported here: to save posts as drafts, call create_text_post or create_image_post with saveAsDraft=true, one per post. If this tool rejects saveAsDraft, do NOT retry without it -- that would publish or schedule every post in the batch.

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
    labelIds: list[str],
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
    labelIds: list[str],
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
async def create_media_upload(
    fileName: str,
    contentType: Literal['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/quicktime'],
    sizeBytes: Annotated[int, Field(ge=1, le=209715200)],
    accountId: str | None = None,
) -> Any:
    """Create a short-lived, size-constrained upload for a local JPG, PNG, GIF, MP4, or MOV file up to 200 MB. Submit multipart/form-data to upload.url with every returned upload.fields entry plus the file, then call complete_media_upload with uploadId and uploadToken. This flow requires an MCP host that can read the local file and submit multipart form data; otherwise use import_media_from_url with a public URL. The staging object is private and is not usable until completion succeeds.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the authenticated account is used automatically. Optional.
    fileName: Original file name including its extension.
    contentType: MIME type matching the file extension.
    sizeBytes: Exact file size in bytes.
    """
    _args = {"accountId": accountId, "fileName": fileName, "contentType": contentType, "sizeBytes": sizeBytes}
    return await _get_client().call_tool(
        "create_media_upload", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=UPDATE)
async def complete_media_upload(
    uploadId: str,
    uploadToken: str,
    accountId: str | None = None,
    name: str | None = None,
    parentId: str | None = None,
) -> Any:
    """Verify a direct upload created by create_media_upload, promote it to an immutable final key, and save it to the account's Media Library. Completion is idempotent and checks the account-bound token, exact object size, MIME metadata, and file signature.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the authenticated account is used automatically. Optional.
    uploadId: Upload session id returned by create_media_upload.
    uploadToken: Account-bound upload token returned by create_media_upload.
    name: Optional display name in the Media Library. Optional.
    parentId: Optional Media Library folder id owned by this account. Optional.
    """
    _args = {"accountId": accountId, "uploadId": uploadId, "uploadToken": uploadToken, "name": name, "parentId": parentId}
    return await _get_client().call_tool(
        "complete_media_upload", {k: v for k, v in _args.items() if v is not None}
    )


@mcp.tool(annotations=WRITE)
async def import_media_from_url(
    url: str,
    accountId: str | None = None,
    name: str | None = None,
    parentId: str | None = None,
) -> Any:
    """Import a public JPG, PNG, GIF, MP4, or MOV URL into Social Champ storage and save it to the account's Media Library. Private and reserved network targets are blocked, redirect DNS is pinned, the complete transfer has a two-minute deadline, file signatures are verified, and the maximum file size is 200 MB.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the authenticated account is used automatically. Optional.
    url: Publicly reachable media URL.
    name: Optional display name in the Media Library. Optional.
    parentId: Optional Media Library folder id owned by this account. Optional.
    """
    _args = {"accountId": accountId, "url": url, "name": name, "parentId": parentId}
    return await _get_client().call_tool(
        "import_media_from_url", {k: v for k, v in _args.items() if v is not None}
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
    """Delete a shareable calendar using its database _id as the calendarId argument, not its public-link UUID.

Args:
    accountId: SocialChamp account id. Omit if the user has only one account - the default account is used automatically. Optional.
    calendarId: Database _id returned by create_public_calendar_link or get_shareable_calendars. Do not use the public calendarId UUID or the id query parameter from the shareable link.
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
