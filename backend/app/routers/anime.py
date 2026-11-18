from fastapi import APIRouter, Query, HTTPException, status, Path
from app.services.anime_service import search_anime, get_anime_detail, AnimeNotFoundError
from app.external_apis.anilist import AniListError
from app.schemas.anime import AnimeSearchResponse, AnimeResponse

router = APIRouter(prefix="/anime", tags=["Anime"])

@router.get("/search", response_model=AnimeSearchResponse)
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

@router.get("/{anime_id}", response_model=AnimeResponse)
async def get_anime_by_id(anime_id: int = Path(..., ge=1)):
    try:
        result = await get_anime_detail(anime_id)

    except AnimeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        ) from exc

    except AniListError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Anime service is temporarily unavailable"
        ) from exc

    return result