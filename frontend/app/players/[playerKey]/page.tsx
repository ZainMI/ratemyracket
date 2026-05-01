"use client";

import { use, useEffect, useState } from "react";
import { getPlayerRatings, getPlayerMatches } from "@/lib/api";
import CompactRatings from "@/components/CompactRatings";
import MatchHistory from "@/components/MatchHistory";

export default function PlayerPage({
  params,
}: {
  params: Promise<{ playerKey: string }>;
}) {
  const { playerKey: rawPlayerKey } = use(params);
  const playerKey = decodeURIComponent(rawPlayerKey);

  const [ratings, setRatings] = useState<any>(null);
  const [matches, setMatches] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      const r = await getPlayerRatings(playerKey);
      const m = await getPlayerMatches(playerKey);
      setRatings(r);
      setMatches(m);
    }

    load();
  }, [playerKey]);

  return (
    <div className="space-y-8">
      {ratings && <CompactRatings title="Player Ratings" ratings={ratings} />}
      <MatchHistory matches={matches} />
    </div>
  );
}
