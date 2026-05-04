import type { Player } from "@/lib/types";

const FAVORITES_KEY = "ratemyracket:favorites";

export type FavoritePlayer = {
  player_key: string;
  player_name: string;
  country?: string;
};

export function getFavorites(): FavoritePlayer[] {
  if (typeof window === "undefined") return [];

  try {
    const raw = window.localStorage.getItem(FAVORITES_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export function saveFavorites(favorites: FavoritePlayer[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites));
}

export function isFavorite(playerKey: string) {
  return getFavorites().some((p) => p.player_key === playerKey);
}

export function addFavorite(player: Player | FavoritePlayer) {
  const favorites = getFavorites();

  if (favorites.some((p) => p.player_key === player.player_key)) {
    return favorites;
  }

  const next = [
    ...favorites,
    {
      player_key: player.player_key,
      player_name: player.player_name,
      country: player.country || "",
    },
  ];

  saveFavorites(next);
  return next;
}

export function removeFavorite(playerKey: string) {
  const next = getFavorites().filter((p) => p.player_key !== playerKey);
  saveFavorites(next);
  return next;
}

export function toggleFavorite(player: Player | FavoritePlayer) {
  return isFavorite(player.player_key)
    ? removeFavorite(player.player_key)
    : addFavorite(player);
}
