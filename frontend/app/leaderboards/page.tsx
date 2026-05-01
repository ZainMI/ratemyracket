"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { getLeaderboard } from "@/lib/api";

const TABS = [
  { key: "overall", label: "Overall" },
  { key: "TT", label: "Table Tennis" },
  { key: "BD", label: "Badminton" },
  { key: "SQ", label: "Squash" },
  { key: "TN", label: "Tennis" },
];

const PAGE_SIZE = 50;

const DESKTOP_GRID =
  "sm:grid sm:grid-cols-[64px_minmax(0,1fr)_90px_110px_80px] sm:items-center sm:gap-4";

export default function LeaderboardsPage() {
  const [sport, setSport] = useState("overall");
  const [rows, setRows] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [pageInput, setPageInput] = useState<number | string>(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setPage(1);
      setPageInput(1);

      const data = await getLeaderboard(sport, 10000);

      if (!cancelled) {
        setRows(data);
        setLoading(false);
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [sport]);

  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));

  const visibleRows = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return rows.slice(start, start + PAGE_SIZE);
  }, [rows, page]);

  function setSafePage(next: number) {
    const clamped = Math.max(1, Math.min(totalPages, next));
    setPage(clamped);
    setPageInput(clamped);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function applyPageChange() {
    let num = Number(pageInput);
    if (!num) num = 1;
    setSafePage(num);
  }

  return (
    <div className="space-y-6">
      <header className="animate-fade-in">
        <h1 className="page-title">Leaderboards</h1>
        <p className="page-subtitle">
          Explore the highest-rated players overall or by individual sport.
        </p>
      </header>

      <div className="rounded-2xl border border-slate-200 bg-white/80 p-1.5 shadow-sm">
        <div className="grid grid-cols-3 gap-2 sm:flex sm:flex-wrap">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSport(tab.key)}
              className={`rounded-xl px-3 py-2 text-sm font-bold transition-all duration-200 ${
                sport === tab.key
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <section
        key={sport}
        className="glass-card animate-fade-in rounded-3xl p-4 sm:p-6"
      >
        {loading ? (
          <Skeleton />
        ) : (
          <>
            <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-bold uppercase tracking-wide text-gray-500">
                  {TABS.find((t) => t.key === sport)?.label}
                </p>
                <h2 className="text-xl font-black text-gray-950">
                  Top Players
                </h2>
              </div>

              <p className="text-sm font-medium text-gray-500">
                Showing {(page - 1) * PAGE_SIZE + 1}–
                {Math.min(page * PAGE_SIZE, rows.length)} of {rows.length}
              </p>
            </div>

            <div
              className={`${DESKTOP_GRID} hidden border-b border-gray-200 px-4 pb-3 text-xs font-black uppercase tracking-wide text-gray-500 sm:grid`}
            >
              <div>Rank</div>
              <div>Name</div>
              <div className="text-center">Country</div>
              <div className="text-right">Rating</div>
              <div className="text-right">Games</div>
            </div>

            <div className="mt-2 space-y-2">
              {visibleRows.map((row, index) => (
                <LeaderboardRow key={row.player_key} row={row} index={index} />
              ))}
            </div>

            {rows.length === 0 && (
              <p className="py-8 text-gray-600">No leaderboard data found.</p>
            )}

            {rows.length > PAGE_SIZE && (
              <div className="mt-5 flex flex-col gap-3 border-t border-gray-200 pt-4 sm:flex-row sm:items-center sm:justify-between">
                <button
                  onClick={() => setSafePage(page - 1)}
                  disabled={page === 1}
                  className="rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-bold text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>

                <div className="flex items-center justify-center gap-2">
                  <span className="text-sm font-semibold text-gray-500">
                    Page
                  </span>

                  <input
                    type="number"
                    value={pageInput}
                    onChange={(e) => {
                      const val = e.target.value;

                      if (val === "") {
                        setPageInput("");
                        return;
                      }

                      const num = Number(val);
                      if (!Number.isNaN(num)) setPageInput(num);
                    }}
                    onBlur={applyPageChange}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") applyPageChange();
                    }}
                    className="w-16 rounded-xl border border-gray-300 bg-white px-2 py-1 text-center text-sm font-bold text-gray-900 outline-none focus:border-emerald-500"
                  />

                  <span className="text-sm font-semibold text-gray-500">
                    of {totalPages}
                  </span>
                </div>

                <button
                  onClick={() => setSafePage(page + 1)}
                  disabled={page === totalPages}
                  className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}

function LeaderboardRow({ row, index }: { row: any; index: number }) {
  return (
    <div
      className={`${DESKTOP_GRID} rounded-2xl border border-gray-100 bg-white p-4 transition hover:bg-emerald-50/40 sm:px-4 sm:py-3`}
      style={{
        animation: `fadeIn 0.25s ease-out ${index * 0.01}s both`,
      }}
    >
      {/* Mobile layout */}
      <div className="sm:hidden">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-sm font-black text-gray-500">#{row.rank}</p>

            <Link
              href={`/players/${encodeURIComponent(row.player_key)}`}
              className="mt-1 block truncate text-lg font-black capitalize text-gray-950 hover:text-emerald-700 hover:underline"
            >
              {row.player_name}
            </Link>

            <p className="mt-1 text-xs font-bold uppercase text-gray-500">
              {row.country || "—"} · {row.games} games
            </p>
          </div>

          <div className="shrink-0 text-right">
            <p className="text-xs font-black uppercase text-gray-400">Rating</p>
            <p className="text-2xl font-black text-gray-950">{row.rating}</p>
          </div>
        </div>
      </div>

      {/* Desktop layout */}
      <div className="hidden font-black text-gray-500 sm:block">
        #{row.rank}
      </div>

      <div className="hidden min-w-0 sm:block">
        <Link
          href={`/players/${encodeURIComponent(row.player_key)}`}
          className="block truncate font-black capitalize text-gray-950 hover:text-emerald-700 hover:underline"
        >
          {row.player_name}
        </Link>
      </div>

      <div className="hidden text-center font-bold uppercase text-gray-600 sm:block">
        {row.country || "—"}
      </div>

      <div className="hidden text-right text-xl font-black text-gray-950 sm:block">
        {row.rating}
      </div>

      <div className="hidden text-right text-gray-600 sm:block">
        {row.games}
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="h-20 animate-pulse rounded-2xl bg-gray-100 sm:h-14"
        />
      ))}
    </div>
  );
}
