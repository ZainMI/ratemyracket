"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getLeaderboard } from "@/lib/api";

const TABS = [
  { key: "overall", label: "Overall" },
  { key: "TT", label: "Table Tennis" },
  { key: "BD", label: "Badminton" },
  { key: "SQ", label: "Squash" },
  { key: "TN", label: "Tennis" },
];

export default function LeaderboardsPage() {
  const [sport, setSport] = useState("overall");
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await getLeaderboard(sport);
      setRows(data);
      setLoading(false);
    }

    load();
  }, [sport]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-4xl font-bold text-gray-950">Leaderboards</h1>
        <p className="mt-2 text-gray-600">
          View the highest-rated Racketlon players by sport.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setSport(tab.key)}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              sport === tab.key
                ? "bg-emerald-600 text-white"
                : "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        {loading ? (
          <p className="text-gray-600">Loading leaderboard...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left">
              <thead>
                <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
                  <th className="py-3 pr-4">Rank</th>
                  <th className="py-3 pr-4">Player</th>
                  <th className="py-3 pr-4">Country</th>
                  <th className="py-3 pr-4 text-right">Rating</th>
                  <th className="py-3 pr-4 text-right">Games</th>
                </tr>
              </thead>

              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.player_key}
                    className="border-b border-gray-100 last:border-0"
                  >
                    <td className="py-3 pr-4 font-bold text-gray-500">
                      #{row.rank}
                    </td>

                    <td className="py-3 pr-4">
                      <Link
                        href={`/players/${encodeURIComponent(row.player_key)}`}
                        className="font-bold capitalize text-gray-950 hover:text-emerald-700 hover:underline"
                      >
                        {row.player_name}
                      </Link>
                    </td>

                    <td className="py-3 pr-4 font-semibold uppercase text-gray-600">
                      {row.country || "—"}
                    </td>

                    <td className="py-3 pr-4 text-right text-xl font-extrabold text-gray-950">
                      {row.rating}
                    </td>

                    <td className="py-3 pr-4 text-right text-gray-600">
                      {row.games}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {rows.length === 0 && (
              <p className="py-6 text-gray-600">No leaderboard data found.</p>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
