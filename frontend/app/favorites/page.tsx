"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  getFavorites,
  removeFavorite,
  type FavoritePlayer,
} from "@/lib/favorites";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoritePlayer[]>([]);

  useEffect(() => {
    setFavorites(getFavorites());
  }, []);

  function remove(playerKey: string) {
    setFavorites(removeFavorite(playerKey));
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="page-title">Favorites</h1>
        <p className="page-subtitle">
          Saved players are stored on this device.
        </p>
      </header>

      <section className="glass-card rounded-3xl p-4 sm:p-6">
        {favorites.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 text-center">
            <h2 className="text-xl font-black text-slate-950">
              No favorites yet
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Add players to your favorites from their player page.
            </p>

            <Link
              href="/players"
              className="secondary-button mt-5 inline-block"
            >
              Find Players
            </Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {favorites.map((player) => (
              <div
                key={player.player_key}
                className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
              >
                <Link
                  href={`/players/${encodeURIComponent(player.player_key)}`}
                  className="block"
                >
                  <h2 className="truncate text-lg font-black capitalize text-slate-950 hover:text-emerald-700 hover:underline">
                    {player.player_name}
                  </h2>
                </Link>

                <p className="mt-1 text-sm font-bold uppercase text-slate-500">
                  {player.country || "Unknown country"}
                </p>

                <div className="mt-4 flex gap-2">
                  <Link
                    href={`/players/${encodeURIComponent(player.player_key)}`}
                    className="flex-1 rounded-xl bg-slate-950 px-3 py-2 text-center text-sm font-black text-white hover:bg-slate-800"
                  >
                    View
                  </Link>

                  <button
                    onClick={() => remove(player.player_key)}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-black text-slate-600 hover:bg-slate-50"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
