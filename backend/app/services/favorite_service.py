from sqlalchemy.orm import Session

from app.db.models import UserFavoritePlayer


def normalize(name: str) -> str:
    return name.strip().lower()


def make_player_key(name: str, country: str):
    return f"{normalize(name)}__{normalize(country)}"


def list_favorites(db: Session, user_id: str):
    return (
        db.query(UserFavoritePlayer)
        .filter(UserFavoritePlayer.user_id == user_id)
        .all()
    )


def add_favorite(db: Session, user_id: str, player_name: str, country: str):
    key = make_player_key(player_name, country)

    existing = (
        db.query(UserFavoritePlayer)
        .filter(
            UserFavoritePlayer.user_id == user_id,
            UserFavoritePlayer.player_key == key,
        )
        .first()
    )

    if existing:
        return existing

    fav = UserFavoritePlayer(
        user_id=user_id,
        player_key=key,
        player_name=normalize(player_name),
        country=normalize(country),
    )

    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def remove_favorite(db: Session, user_id: str, player_key: str):
    fav = (
        db.query(UserFavoritePlayer)
        .filter(
            UserFavoritePlayer.user_id == user_id,
            UserFavoritePlayer.player_key == player_key,
        )
        .first()
    )

    if fav:
        db.delete(fav)
        db.commit()

    return {"removed": bool(fav)}
