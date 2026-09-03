"use client";

import { use, useEffect, useState } from "react";
import { getPlayerRatings, getPlayerMatches } from "@/lib/api";
import CompactRatings from "@/components/CompactRatings";
import MatchHistory from "@/components/MatchHistory";
import MatchHistorySkeleton from "@/components/MatchHistorySkeleton";
import type { PlayerRatings } from "@/lib/types";

export default function PlayerPage({
  params,
}: {
  params: Promise<{ playerKey: string }>;
}) {
  const { playerKey: rawPlayerKey } = use(params);
  const playerKey = decodeURIComponent(rawPlayerKey);

  const [ratings, setRatings] = useState<PlayerRatings | null>(null);
  const [matches, setMatches] = useState<Array<Record<string, unknown>>>([]);
  const [ratingsLoading, setRatingsLoading] = useState(true);
  const [matchesLoading, setMatchesLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadPlayer() {
      setRatings(null);
      setMatches([]);
      setRatingsLoading(true);
      setMatchesLoading(true);

      try {
        const [ratingsData, matchesData] = await Promise.all([
          getPlayerRatings(playerKey),
          getPlayerMatches(playerKey),
        ]);

        if (!cancelled) {
          setRatings(ratingsData);
          setMatches(Array.isArray(matchesData) ? matchesData : []);
        }
      } finally {
        if (!cancelled) {
          setRatingsLoading(false);
          setMatchesLoading(false);
        }
      }
    }

    loadPlayer();

    return () => {
      cancelled = true;
    };
  }, [playerKey]);

  return (
    <div className="space-y-8">
      {ratingsLoading ? (
        <section className="glass-card rounded-3xl p-4 sm:p-6">
          <div className="mb-4 h-5 w-36 animate-pulse rounded bg-slate-200" />
          <div className="h-7 w-48 animate-pulse rounded bg-slate-200" />

          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="h-24 animate-pulse rounded-xl bg-slate-100"
              />
            ))}
          </div>
        </section>
      ) : (
        ratings && <CompactRatings title="Player Ratings" ratings={ratings} />
      )}

      {matchesLoading ? (
        <MatchHistorySkeleton />
      ) : (
        <MatchHistory matches={matches} />
      )}
    </div>
  );
}
