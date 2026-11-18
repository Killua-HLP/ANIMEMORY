from pydantic import BaseModel, ConfigDict

class AnimeTitle(BaseModel):
    romaji : str | None = None
    english : str | None = None
    native : str | None = None

class AnimeCoverImage(BaseModel):
    large : str | None = None

class AnimeResponse(BaseModel):
    id : int
    title : AnimeTitle
    coverImage : AnimeCoverImage | None = None
    episodes : int | None = None
    status : str | None = None
    averageScore : int | None = None

class AnimeSearchResponse(BaseModel):
    items : list[AnimeResponse]
    page : int
    per_page : int
    has_next_page : bool 
    total : int

    model_config = ConfigDict(from_attributes=True)