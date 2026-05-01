from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.services.favorite_service import (
    add_favorite,
    list_favorites,
    remove_favorite,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


class FavoriteCreate(BaseModel):
    player_name: str
    country: str


@router.get("")
def get_favorites(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return list_favorites(db, user_id)


@router.post("")
def create_favorite(
    req: FavoriteCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return add_favorite(db, user_id, req.player_name, req.country)


@router.delete("/{player_key}")
def delete_favorite(
    player_key: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return remove_favorite(db, user_id, player_key)
