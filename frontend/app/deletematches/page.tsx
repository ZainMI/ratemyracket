"use client";

import { useState } from "react";
import PlayerSearch from "@/components/PlayerSearch";
import type { Player } from "@/lib/types";

interface Match {
  id: string;
  match_date: string;
  tournament_id: string;
  team1_players: string;
  team2_players: string;
}

export default function DeleteMatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const searchMatches = async (name: string) => {
    if (!name.trim()) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(
        `${API_URL}/admin/matches/search?player_name=${encodeURIComponent(name)}`,
        {
          headers: {
            // Replace with your actual admin secret or use an env variable
            "x-admin-secret":
              process.env.NEXT_PUBLIC_ADMIN_SECRET || "your_admin_secret",
          },
        },
      );

      if (!res.ok) throw new Error("Failed to fetch matches");

      const data = await res.json();
      setMatches(data);
      if (data.length === 0) {
        setError(`No matches found for "${name}".`);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred while searching.");
    } finally {
      setLoading(false);
    }
  };

  const deleteMatch = async (matchId: string) => {
    if (
      !window.confirm("Are you sure you want to permanently delete this match?")
    ) {
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/admin/matches/${matchId}`, {
        method: "DELETE",
        headers: {
          "x-admin-secret":
            process.env.NEXT_PUBLIC_ADMIN_SECRET || "your_admin_secret",
        },
      });

      if (!res.ok) throw new Error("Failed to delete the match");

      setSuccess("Match deleted successfully.");
      setMatches((prev) => prev.filter((m) => m.id !== matchId));
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred while deleting.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 md:p-10 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">
          Delete Matches
        </h1>
        <p className="text-gray-500">
          Lookup a player to find and manage their match history.
        </p>
      </div>

      <div className="mb-8 max-w-md">
        <PlayerSearch
          label="Select a Player"
          onSelect={(player: Player) => searchMatches(player.player_name)}
        />
      </div>

      {loading && (
        <p className="mb-6 text-gray-600 text-sm">Loading matches...</p>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-6 p-4 bg-green-50 text-green-700 rounded-lg border border-green-200">
          {success}
        </div>
      )}

      {matches.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600">
              <thead className="bg-gray-50 text-gray-700 uppercase border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 font-semibold">Date</th>
                  <th className="px-6 py-4 font-semibold">Tournament</th>
                  <th className="px-6 py-4 font-semibold">Team 1</th>
                  <th className="px-6 py-4 font-semibold">Team 2</th>
                  <th className="px-6 py-4 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {matches.map((match) => (
                  <tr
                    key={match.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                      {match.match_date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {match.tournament_id}
                    </td>
                    <td className="px-6 py-4">{match.team1_players}</td>
                    <td className="px-6 py-4">{match.team2_players}</td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => deleteMatch(match.id)}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
