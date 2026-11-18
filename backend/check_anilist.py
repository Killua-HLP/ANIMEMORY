import asyncio
from app.services.anime_service import search_anime

async def main():
    anime_list = await search_anime("Naruto")

    for anime in anime_list:
        print(anime["title"])
        print("Episodes:", anime["episodes"])
        print("-" * 30)


asyncio.run(main())