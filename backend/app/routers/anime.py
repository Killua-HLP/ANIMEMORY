from fastapi import APIRouter, Query, HTTPException, status
from app.services.anime_service import search_anime
from app.external_apis.anilist import AniListError

router = APIRouter(prefix="/anime", tags=["Anime"])

@router.get("/search")
async def anime_search(
    search: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20)
):
    try:
        result = await search_anime(
            search,
            page,
            per_page
        )
    except AniListError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Anime search service is temporarily unavailable"
        ) from exc
    return result