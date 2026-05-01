from fastapi import APIRouter, HTTPException

from app.services.player_service import (
    search_players,
    get_player,
    get_player_ratings,
    get_player_matches,
    get_leaderboard,
)

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/search")
def search(q: str, limit: int = 20):
    return search_players(q=q, limit=limit)


@router.get("/leaderboard")
def leaderboard(sport: str = "overall", limit: int = 10000):
    return get_leaderboard(sport=sport, limit=limit)


@router.get("/{player_key}/ratings")
def ratings(player_key: str):
    try:
        return get_player_ratings(player_key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{player_key}/matches")
def matches(player_key: str, limit: int = 50):
    return get_player_matches(player_key, limit=limit)


@router.get("/{player_key}")
def player(player_key: str):
    try:
        return get_player(player_key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
