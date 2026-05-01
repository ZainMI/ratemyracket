"use client";

import { useEffect, useState } from "react";
import { searchPlayers } from "@/lib/api";
import type { Player } from "@/lib/types";

export default function PlayerSearch({
  label,
  onSelect,
}: {
  label: string;
  onSelect: (player: Player) => void;
}) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<Player | null>(null);

  useEffect(() => {
    const query = q.trim();

    if (selected && query === selected.player_name) {
      setResults([]);
      return;
    }

    if (query.length < 2) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      const data = await searchPlayers(query);
      setResults(data);
      setLoading(false);
    }, 250);

    return () => clearTimeout(timer);
  }, [q, selected]);

  function choosePlayer(player: Player) {
    setSelected(player);
    setQ(player.player_name);
    setResults([]);
    onSelect(player);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && results.length > 0) {
      e.preventDefault();
      choosePlayer(results[0]);
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <label className="mb-2 block text-sm font-semibold text-gray-800">
        {label}
      </label>

      <input
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setSelected(null);
        }}
        onKeyDown={handleKeyDown}
        placeholder="Search player..."
        className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-950 placeholder:text-gray-400 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
      />

      {selected && (
        <div className="mt-4 rounded-xl border border-emerald-500 bg-emerald-50 p-3">
          <div className="font-semibold capitalize text-gray-950">
            {selected.player_name}
          </div>
          <div className="text-sm text-gray-600">
            {selected.country || "Unknown country"}
          </div>
        </div>
      )}

      {!selected && (
        <div className="mt-4 max-h-72 space-y-2 overflow-auto">
          {loading && <p className="text-sm text-gray-500">Searching...</p>}

          {results.map((player) => (
            <button
              key={player.player_key}
              onClick={() => choosePlayer(player)}
              className="w-full rounded-xl border border-gray-200 bg-white p-3 text-left transition hover:border-emerald-400 hover:bg-gray-50"
            >
              <div className="font-semibold capitalize text-gray-950">
                {player.player_name}
              </div>
              <div className="text-sm text-gray-600">
                {player.country || "Unknown country"}
              </div>
            </button>
          ))}

          {!loading && q.trim().length >= 2 && results.length === 0 && (
            <p className="text-sm text-gray-500">No players found.</p>
          )}
        </div>
      )}
    </div>
  );
}
