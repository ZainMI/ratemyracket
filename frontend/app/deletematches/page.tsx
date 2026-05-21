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
  const [deletePassword, setDeletePassword] = useState("");
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatchIds, setSelectedMatchIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const searchMatches = async (name: string) => {
    if (!name.trim()) return;
    if (!deletePassword.trim()) {
      setError("Please enter the Delete Password first.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setSelectedMatchIds([]);

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(
        `${API_URL}/admin/matches/search?player_name=${encodeURIComponent(name)}`,
        {
          headers: {
            "x-delete-password": deletePassword,
          },
        },
      );

      if (!res.ok) {
        let errMessage = "Failed to fetch matches";
        try {
          const errData = await res.json();
          if (errData.detail) errMessage = errData.detail;
        } catch (e) {}
        throw new Error(errMessage);
      }

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

  const toggleSelection = (id: string) => {
    setSelectedMatchIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const toggleSelectAll = () => {
    if (selectedMatchIds.length === matches.length) {
      setSelectedMatchIds([]);
    } else {
      setSelectedMatchIds(matches.map((m) => m.id));
    }
  };

  const deleteMatches = async (ids: string[]) => {
    if (!deletePassword.trim()) {
      setError("Please enter the Delete Password first.");
      return;
    }
    if (
      !window.confirm(
        `Are you sure you want to permanently delete ${ids.length} match(es)?`,
      )
    ) {
      return;
    }

    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      let deletedCount = 0;
      let failedCount = 0;
      let lastError = "";

      for (const matchId of ids) {
        try {
          const res = await fetch(`${API_URL}/admin/matches/${matchId}`, {
            method: "DELETE",
            headers: {
              "x-delete-password": deletePassword,
            },
          });

          if (!res.ok) {
            failedCount++;
            try {
              const errData = await res.json();
              if (errData.detail) lastError = errData.detail;
            } catch (e) {}
          } else {
            deletedCount++;
          }
        } catch (e) {
          failedCount++;
        }
      }

      if (failedCount > 0) {
        setError(`Failed to delete ${failedCount} match(es). ${lastError}`);
      }
      if (deletedCount > 0) {
        setSuccess(
          `${deletedCount} match(es) deleted successfully! ML Pipeline started in the background.`,
        );
        setMatches((prev) => prev.filter((m) => !ids.includes(m.id)));
        setSelectedMatchIds((prev) => prev.filter((id) => !ids.includes(id)));
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred while deleting.");
    } finally {
      setLoading(false);
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
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-800 mb-2">
            Delete Password
          </label>
          <input
            type="password"
            placeholder="Enter Delete Password"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-950 placeholder:text-gray-400 outline-none focus:border-red-500 focus:ring-2 focus:ring-red-100"
          />
        </div>

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
          <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
            <span className="text-sm font-medium text-gray-700">
              {matches.length} Matches Found
            </span>
            {selectedMatchIds.length > 0 && (
              <button
                onClick={() => deleteMatches(selectedMatchIds)}
                disabled={loading}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium shadow-sm transition-colors disabled:opacity-50"
              >
                Delete Selected ({selectedMatchIds.length})
              </button>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600">
              <thead className="bg-gray-100 text-gray-700 uppercase border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 font-semibold w-12 text-center">
                    <input
                      type="checkbox"
                      checked={
                        matches.length > 0 &&
                        selectedMatchIds.length === matches.length
                      }
                      onChange={toggleSelectAll}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                    />
                  </th>
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
                    className={`hover:bg-gray-50 transition-colors ${
                      selectedMatchIds.includes(match.id) ? "bg-blue-50" : ""
                    }`}
                  >
                    <td className="px-6 py-4 text-center">
                      <input
                        type="checkbox"
                        checked={selectedMatchIds.includes(match.id)}
                        onChange={() => toggleSelection(match.id)}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                      />
                    </td>
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
                        onClick={() => deleteMatches([match.id])}
                        disabled={loading}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors disabled:opacity-50"
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
