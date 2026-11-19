from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
from app.external_apis.anilist import AniListError
from app.routers.anime import AnimeNotFoundError

client = TestClient(app)

fake_response = {
    "Page": {
        "pageInfo": {
            "currentPage": 1,
            "perPage": 10,
            "hasNextPage": True,
            "total": 100
        },
        "media": [
            {
                "id": 20,
                "title": {
                    "romaji": "Naruto",
                    "english": "Naruto",
                    "native": "ナルト"
                },
                "coverImage": {
                    "large": "https://example.com/naruto.jpg"
                },
                "episodes": 220,
                "status": "FINISHED",
                "averageScore": 79
            }
        ]
    }
}


fake_detail_response = {
    "Media": {
        "id": 20,
        "title": {
            "romaji": "Naruto",
            "english": "Naruto",
            "native": "ナルト"
        },
        "coverImage": {
            "large": "https://example.com/naruto.jpg"
        },
        "episodes": 220,
        "status": "FINISHED",
        "averageScore": 79,
        "description": "GuGuGArGAr Naruto"
    }
}
def test_anime_search(client):
    with patch(
        "app.services.anime_service.send_anilist_request",
        new_callable=AsyncMock
    ) as mock_request:

        mock_request.return_value = fake_response

        response = client.get("/anime/search?search=Naruto")

        assert response.status_code == 200
        assert response.json()["items"][0]["title"]["romaji"] == "Naruto"
        assert response.json()["page"] == 1

        mock_request.assert_awaited_once()

def test_anime_search_service_unavailable(client):
    with patch(
        "app.services.anime_service.send_anilist_request",
        new_callable=AsyncMock
    ) as mock_request:

        mock_request.side_effect = AniListError("Anilist unavailable")

        response = client.get("/anime/search?search=Naruto")

        assert response.status_code == 503
        assert response.json()["detail"] == (
            "Anime search service is temporarily unavailable"
        )

def test_anime_search_invalid_input(client):
    response = client.get("/anime/search?search=")

    assert response.status_code == 422

def test_anime_detail(client):
    with patch(
        "app.services.anime_service.send_anilist_request",
        new_callable=AsyncMock
    ) as mock_request:

        mock_request.return_value = fake_detail_response

        response = client.get("/anime/20")

        assert response.status_code == 200
        assert response.json()["id"] == 20

        mock_request.assert_awaited_once()

def test_detail_service_unavailable(client):
    with patch(
        "app.services.anime_service.send_anilist_request",
        new_callable=AsyncMock
    ) as mock_request:

        mock_request.side_effect = AniListError("Anilist unavailable")

        response = client.get("/anime/20")

        assert response.status_code == 503
        assert response.json()["detail"] == (
            "Anime service is temporarily unavailable"
        )

def test_detail_anime_not_found(client):
    with patch(
        "app.services.anime_service.send_anilist_request",
        new_callable=AsyncMock
    ) as mock_reuqest:

        mock_reuqest.side_effect = AnimeNotFoundError("Anime not found")

        response = client.get("/anime/20")

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Anime not found"
        )
        