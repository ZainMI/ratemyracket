from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    player_name: str
    country: str


class FavoriteResponse(BaseModel):
    player_key: str
    player_name: str
    country: str
