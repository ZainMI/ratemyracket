"use client";

import { useEffect, useState } from "react";
import {
  addFavorite,
  isFavorite,
  removeFavorite,
  type FavoritePlayer,
} from "@/lib/favorites";

export default function FavoriteButton({ player }: { player: FavoritePlayer }) {
  const [favorite, setFavorite] = useState(false);

  useEffect(() => {
    setFavorite(isFavorite(player.player_key));
  }, [player.player_key]);

  function toggle() {
    if (favorite) {
      removeFavorite(player.player_key);
      setFavorite(false);
    } else {
      addFavorite(player);
      setFavorite(true);
    }
  }

  return (
    <button
      onClick={toggle}
      className={`rounded-xl px-3 py-2 text-sm font-black transition ${
        favorite
          ? "bg-amber-100 text-amber-800 hover:bg-amber-200"
          : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
      }`}
    >
      {favorite ? "★ Favorited" : "☆ Favorite"}
    </button>
  );
}
