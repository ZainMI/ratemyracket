from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class UserFavoritePlayer(Base):
    __tablename__ = "user_favorite_players"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, index=True, nullable=False)

    # Player identity = normalized name + country
    player_key = Column(String, index=True, nullable=False)
    player_name = Column(String, nullable=False)
    country = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "player_key",
            name="uq_user_favorite_player",
        ),
    )
