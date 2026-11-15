import httpx
import logging

ANILIST_URL = "https://graphql.anilist.co"
logger = logging.getLogger(__name__)


class AniListError(Exception):
    """Raised when AniList is unreachable or returns an error."""

async def send_anilist_request(query: str, variables: dict | None = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    ANILIST_URL,
                    json={"query": query, "variables": variables or {}},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            logger.warning("AniList request timed out")
            raise AniListError("AniList request timed out") from exc
        except httpx.HTTPStatusError as exc:
            logger.warning("AniList returned HTTP %s", exc.response.status_code)
            raise AniListError("AniList returned an error") from exc
        except httpx.HTTPError as exc:
            logger.warning("AniList network error: %s", type(exc).__name__)
            raise AniListError("Could not reach AniList") from exc

        if data.get("errors"):
            logger.warning("AniList GraphQL errors: %s", data["errors"])
            raise AniListError("AniList query failed")

        if not isinstance(data.get("data"), dict):
            raise AniListError("Invalid response from AniList")

        return data["data"]