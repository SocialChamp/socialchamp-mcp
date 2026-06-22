"""HTTP client for the Social Champ API.

This is the only module that makes HTTP calls. Tools in ``server.py`` call
methods here and never touch httpx directly, so changing an endpoint never
touches a tool definition.

Scope and source of truth
-------------------------
The tool catalog, argument names, and nouns (channels, workspaces, posts,
shareable calendars) mirror the published Social Champ MCP schema
(``mcp-submission/mcp-schema.md`` in the auth backend) and the tool definitions
in ``api/mcp/tools.ts``. The base URL and Bearer authentication are confirmed
from the authentication guide (https://developers.socialchamp.com/docs/authentication).

The REST paths, query parameter names, and request body field names below are
representative and marked with ``TODO`` where they still need to be reconciled
against the OpenAPI reference (https://developers.socialchamp.com/api-reference)
or the auth backend's MCP handlers. Every such assumption is isolated to this
file. When you confirm a path or field, update it here and the tools keep
working unchanged.

Authentication accepts either a Social Champ API key or an OAuth2 access token
(scopes ``read_profile`` and ``manage_post``). Both are sent as a Bearer token.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import Settings, load_settings


class SocialChampClient:
    """Thin async wrapper over the Social Champ REST API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()
        if not self._settings.api_key:
            raise RuntimeError(
                "SOCIALCHAMP_API_KEY is not set. Provide a Social Champ API key "
                "or OAuth2 access token in the environment before making API "
                "requests."
            )
        self._client = httpx.AsyncClient(
            base_url=self._settings.base_url,
            timeout=self._settings.timeout,
            headers={
                "Authorization": f"Bearer {self._settings.api_key}",
                "Accept": "application/json",
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        # accountId, when present, scopes the request. The real MCP transport
        # also forwards a workspace-id header for workspace-scoped tools.
        # TODO: confirm whether account scoping is a query param, header, or
        # path segment against the OpenAPI reference.
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    @staticmethod
    def _account_params(account_id: str | None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        params: dict[str, Any] = dict(extra or {})
        if account_id is not None:
            params["account_id"] = account_id
        return params

    # ------------------------------------------------------------------
    # Channels (read-only)
    # ------------------------------------------------------------------

    async def get_channels(self, account_id: str | None = None) -> Any:
        # TODO: confirm path (assumed GET /channels).
        return await self._request("GET", "/channels", params=self._account_params(account_id))

    async def get_channel(self, channel_id: str, account_id: str | None = None) -> Any:
        # TODO: confirm path (assumed GET /channels/{channel_id}).
        return await self._request(
            "GET", f"/channels/{channel_id}", params=self._account_params(account_id)
        )

    async def get_filtered_channels(
        self,
        types: list[str] | None = None,
        search: str | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and query parameter names (assumed GET /channels
        # with repeated `types` and a `search` term).
        extra: dict[str, Any] = {}
        if types:
            extra["types"] = types
        if search is not None:
            extra["search"] = search
        return await self._request(
            "GET", "/channels", params=self._account_params(account_id, extra)
        )

    # ------------------------------------------------------------------
    # Workspaces (read-only)
    # ------------------------------------------------------------------

    async def get_workspaces(self, account_id: str | None = None) -> Any:
        # TODO: confirm path (assumed GET /workspaces).
        return await self._request("GET", "/workspaces", params=self._account_params(account_id))

    # ------------------------------------------------------------------
    # Posts (read-only)
    # ------------------------------------------------------------------

    async def get_paginated_posts(
        self,
        page: int = 1,
        page_size: int = 20,
        from_date: str | None = None,
        to_date: str | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and query parameter names (assumed GET /posts).
        extra: dict[str, Any] = {"page": page, "pageSize": page_size}
        if from_date is not None:
            extra["fromDate"] = from_date
        if to_date is not None:
            extra["toDate"] = to_date
        return await self._request(
            "GET", "/posts", params=self._account_params(account_id, extra)
        )

    async def get_posts_for_channels(
        self,
        channel_ids: list[str],
        limit: int = 50,
        from_date: str | None = None,
        to_date: str | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and query parameter names (assumed GET /posts
        # scoped by repeated `channelIds`).
        extra: dict[str, Any] = {"channelIds": channel_ids, "limit": limit}
        if from_date is not None:
            extra["fromDate"] = from_date
        if to_date is not None:
            extra["toDate"] = to_date
        return await self._request(
            "GET", "/posts", params=self._account_params(account_id, extra)
        )

    async def get_posts_with_assets(
        self, limit: int = 50, account_id: str | None = None
    ) -> Any:
        # TODO: confirm path and filter (assumed GET /posts?hasAssets=true).
        extra = {"hasAssets": "true", "limit": limit}
        return await self._request(
            "GET", "/posts", params=self._account_params(account_id, extra)
        )

    async def get_scheduled_posts(
        self,
        limit: int = 50,
        from_date: str | None = None,
        to_date: str | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and filter (assumed GET /posts?status=scheduled).
        extra: dict[str, Any] = {"status": "scheduled", "limit": limit}
        if from_date is not None:
            extra["fromDate"] = from_date
        if to_date is not None:
            extra["toDate"] = to_date
        return await self._request(
            "GET", "/posts", params=self._account_params(account_id, extra)
        )

    # ------------------------------------------------------------------
    # Posts (write)
    # ------------------------------------------------------------------

    async def create_text_post(
        self,
        text: str,
        channel_ids: list[str],
        date_time: str | None = None,
        is_scheduled: bool = False,
        location: dict[str, Any] | None = None,
        first_comment: dict[str, Any] | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and body field names (assumed POST /posts).
        body: dict[str, Any] = {
            "text": text,
            "channelIds": channel_ids,
            "isScheduled": is_scheduled,
        }
        if date_time is not None:
            body["dateTime"] = date_time
        if location is not None:
            body["location"] = location
        if first_comment is not None:
            body["firstComment"] = first_comment
        if account_id is not None:
            body["accountId"] = account_id
        return await self._request("POST", "/posts", json=body)

    async def create_image_post(
        self,
        text: str,
        image_urls: list[str],
        channel_ids: list[str],
        date_time: str | None = None,
        is_scheduled: bool = False,
        location: dict[str, Any] | None = None,
        first_comment: dict[str, Any] | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and body field names (assumed POST /posts with imageUrls).
        body: dict[str, Any] = {
            "text": text,
            "imageUrls": image_urls,
            "channelIds": channel_ids,
            "isScheduled": is_scheduled,
        }
        if date_time is not None:
            body["dateTime"] = date_time
        if location is not None:
            body["location"] = location
        if first_comment is not None:
            body["firstComment"] = first_comment
        if account_id is not None:
            body["accountId"] = account_id
        return await self._request("POST", "/posts", json=body)

    async def update_post(
        self,
        post_id: str,
        text: str | None = None,
        date_time: str | None = None,
        channel_ids: list[str] | None = None,
        image_urls: list[str] | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and method (assumed PATCH /posts/{post_id}).
        body: dict[str, Any] = {}
        if text is not None:
            body["text"] = text
        if date_time is not None:
            body["dateTime"] = date_time
        if channel_ids is not None:
            body["channelIds"] = channel_ids
        if image_urls is not None:
            body["imageUrls"] = image_urls
        if account_id is not None:
            body["accountId"] = account_id
        return await self._request("PATCH", f"/posts/{post_id}", json=body)

    # ------------------------------------------------------------------
    # Posts (destructive)
    # ------------------------------------------------------------------

    async def delete_post(self, post_id: str, account_id: str | None = None) -> Any:
        # TODO: confirm path (assumed DELETE /posts/{post_id}).
        return await self._request(
            "DELETE", f"/posts/{post_id}", params=self._account_params(account_id)
        )

    # ------------------------------------------------------------------
    # Calendars (read-only)
    # ------------------------------------------------------------------

    async def get_calendar_view_options(self, account_id: str | None = None) -> Any:
        # TODO: confirm path (assumed GET /calendar/view-options).
        return await self._request(
            "GET", "/calendar/view-options", params=self._account_params(account_id)
        )

    async def get_shareable_calendars(
        self, workspace_id: str, account_id: str | None = None
    ) -> Any:
        # TODO: confirm path (assumed GET /workspaces/{workspace_id}/shareable-calendars).
        return await self._request(
            "GET",
            f"/workspaces/{workspace_id}/shareable-calendars",
            params=self._account_params(account_id),
        )

    async def get_in_app_calendar_url(
        self, calendar_token: str | None = None, account_id: str | None = None
    ) -> Any:
        # TODO: confirm path (assumed GET /calendar/in-app-url).
        extra: dict[str, Any] = {}
        if calendar_token is not None:
            extra["calendarToken"] = calendar_token
        return await self._request(
            "GET", "/calendar/in-app-url", params=self._account_params(account_id, extra)
        )

    # ------------------------------------------------------------------
    # Calendars (write)
    # ------------------------------------------------------------------

    async def create_public_calendar_link(
        self,
        workspace_id: str,
        name: str,
        profile_ids: list[str],
        from_date: str,
        to_date: str,
        password: str | None = None,
        permission_roles: list[str] | None = None,
        is_active: bool = True,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and body field names (assumed POST /shareable-calendars).
        body: dict[str, Any] = {
            "workspaceId": workspace_id,
            "name": name,
            "profileIds": profile_ids,
            "fromDate": from_date,
            "toDate": to_date,
            "isActive": is_active,
        }
        if password is not None:
            body["password"] = password
        if permission_roles is not None:
            body["permissionRoles"] = permission_roles
        if account_id is not None:
            body["accountId"] = account_id
        return await self._request("POST", "/shareable-calendars", json=body)

    async def update_shareable_calendar(
        self,
        calendar_id: str,
        workspace_id: str | None = None,
        name: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        password: str | None = None,
        permission_roles: list[str] | None = None,
        is_active: bool | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path and method (assumed PATCH /shareable-calendars/{calendar_id}).
        body: dict[str, Any] = {}
        if workspace_id is not None:
            body["workspaceId"] = workspace_id
        if name is not None:
            body["name"] = name
        if from_date is not None:
            body["fromDate"] = from_date
        if to_date is not None:
            body["toDate"] = to_date
        if password is not None:
            body["password"] = password
        if permission_roles is not None:
            body["permissionRoles"] = permission_roles
        if is_active is not None:
            body["isActive"] = is_active
        if account_id is not None:
            body["accountId"] = account_id
        return await self._request("PATCH", f"/shareable-calendars/{calendar_id}", json=body)

    # ------------------------------------------------------------------
    # Calendars (destructive)
    # ------------------------------------------------------------------

    async def delete_shareable_calendar(
        self,
        calendar_id: str,
        workspace_id: str | None = None,
        account_id: str | None = None,
    ) -> Any:
        # TODO: confirm path (assumed DELETE /shareable-calendars/{calendar_id}).
        extra: dict[str, Any] = {}
        if workspace_id is not None:
            extra["workspaceId"] = workspace_id
        return await self._request(
            "DELETE",
            f"/shareable-calendars/{calendar_id}",
            params=self._account_params(account_id, extra),
        )
