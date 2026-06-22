"""HTTP client for the Social Champ API.

This is the only module that makes HTTP calls. Tools in ``server.py`` call
methods here and never touch httpx directly, so changing an endpoint never
touches a tool definition.

Reconciling with the real API
-----------------------------
The base URL and Bearer authentication are confirmed from the Social Champ
authentication guide (https://developers.socialchamp.com/docs/authentication).
The endpoint paths, request body field names, and query parameters below are
representative and marked with ``TODO`` where they need to be reconciled against
the OpenAPI reference (https://developers.socialchamp.com/api-reference). Every
such assumption is isolated to this file. When you confirm a path or field,
update it here and the tools keep working unchanged.
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
                "SOCIALCHAMP_API_KEY is not set. Provide it in the environment "
                "before making API requests."
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
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    # ------------------------------------------------------------------
    # Read-only endpoints
    # ------------------------------------------------------------------

    async def list_social_accounts(self) -> Any:
        # TODO: confirm path against the OpenAPI reference (assumed GET /accounts).
        return await self._request("GET", "/accounts")

    async def get_best_time_to_post(self, account_id: str) -> Any:
        # TODO: confirm path (assumed GET /accounts/{account_id}/best-time).
        return await self._request("GET", f"/accounts/{account_id}/best-time")

    async def get_account_analytics(
        self,
        account_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Any:
        # TODO: confirm path and query parameter names
        # (assumed GET /accounts/{account_id}/analytics?start_date=&end_date=).
        params: dict[str, str] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        return await self._request(
            "GET", f"/accounts/{account_id}/analytics", params=params
        )

    async def list_scheduled_posts(
        self,
        account_id: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> Any:
        # TODO: confirm path and query parameter names (assumed GET /posts).
        params: dict[str, Any] = {"limit": limit}
        if account_id is not None:
            params["account_id"] = account_id
        if status is not None:
            params["status"] = status
        return await self._request("GET", "/posts", params=params)

    async def get_post(self, post_id: str) -> Any:
        # TODO: confirm path (assumed GET /posts/{post_id}).
        return await self._request("GET", f"/posts/{post_id}")

    async def get_post_analytics(self, post_id: str) -> Any:
        # TODO: confirm path (assumed GET /posts/{post_id}/analytics).
        return await self._request("GET", f"/posts/{post_id}/analytics")

    # ------------------------------------------------------------------
    # Write endpoints
    # ------------------------------------------------------------------

    async def schedule_post(
        self,
        content: str,
        account_ids: list[str],
        scheduled_time: str | None = None,
        media_urls: list[str] | None = None,
    ) -> Any:
        # TODO: confirm path and body field names (assumed POST /posts with
        # fields content, account_ids, scheduled_time, media_urls). When
        # scheduled_time is omitted the API is expected to queue the post.
        body: dict[str, Any] = {
            "content": content,
            "account_ids": account_ids,
        }
        if scheduled_time is not None:
            body["scheduled_time"] = scheduled_time
        if media_urls is not None:
            body["media_urls"] = media_urls
        return await self._request("POST", "/posts", json=body)

    async def update_post(
        self,
        post_id: str,
        content: str | None = None,
        scheduled_time: str | None = None,
    ) -> Any:
        # TODO: confirm path and method (assumed PATCH /posts/{post_id}).
        body: dict[str, Any] = {}
        if content is not None:
            body["content"] = content
        if scheduled_time is not None:
            body["scheduled_time"] = scheduled_time
        return await self._request("PATCH", f"/posts/{post_id}", json=body)

    # ------------------------------------------------------------------
    # Destructive endpoints
    # ------------------------------------------------------------------

    async def delete_post(self, post_id: str) -> Any:
        # TODO: confirm path (assumed DELETE /posts/{post_id}).
        return await self._request("DELETE", f"/posts/{post_id}")
