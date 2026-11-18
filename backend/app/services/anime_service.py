from app.external_apis.anilist import send_anilist_request
from app.external_apis.queries import SEARCH_ANIME_QUERY, ANIME_DETAIL_QUERY


class AnimeNotFoundError(Exception):
    pass
    """Raised when Anime is not found."""

async def search_anime(search: str, page: int = 1, per_page: int = 10):
    variables = {
        "search": search,
        "page": page,
        "perPage": per_page
    }

    result = await send_anilist_request(SEARCH_ANIME_QUERY, variables)

    page_data = result.get("Page") or {}
    page_info = page_data.get("pageInfo") or {}

    return {
        "items": page_data.get("media", []),
        "page": page_info.get("currentPage", page),
        "per_page": page_info.get("perPage", per_page),
        "has_next_page": page_info.get("hasNextPage", False),
        "total": page_info.get("total", 0),
    }

async def get_anime_detail(anime_id: int):
    variables = {
        "id": anime_id
    }

    result = await send_anilist_request(ANIME_DETAIL_QUERY, variables)

    anime = result.get("Media")

    if anime is None:
        raise AnimeNotFoundError()
    return anime