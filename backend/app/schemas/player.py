from pydantic import BaseModel


class PlayerSearchResult(BaseModel):
    player_key: str
    player_name: str
    country: str


class PlayerDetail(BaseModel):
    player_key: str
    player_name: str
    country: str


class PlayerRatings(BaseModel):
    player_key: str
    ratings: dict  # { "TT": {...}, "BD": {...}, ... }
