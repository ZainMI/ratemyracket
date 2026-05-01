"use client";

import { useEffect, useState } from "react";
import PlayerSearch from "@/components/PlayerSearch";
import PredictionResult from "@/components/PredictionResult";
import PlayerRatingsCard from "@/components/PlayerRatingsCard";
import { predictMatch, getPlayerRatings } from "@/lib/api";
import type { Player, Prediction } from "@/lib/types";

export default function PredictPage() {
  const [p1, setP1] = useState<Player | null>(null);
  const [p2, setP2] = useState<Player | null>(null);

  const [p1Ratings, setP1Ratings] = useState<any>(null);
  const [p2Ratings, setP2Ratings] = useState<any>(null);

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [error, setError] = useState("");

  async function selectP1(player: Player) {
    setP1(player);
    setPrediction(null);
    const ratings = await getPlayerRatings(player.player_key);
    setP1Ratings(ratings);
  }

  async function selectP2(player: Player) {
    setP2(player);
    setPrediction(null);
    const ratings = await getPlayerRatings(player.player_key);
    setP2Ratings(ratings);
  }

  useEffect(() => {
    if (!p1 || !p2) return;
    if (p1.player_key === p2.player_key) return;

    let cancelled = false;

    async function runPrediction() {
      setLoadingPrediction(true);
      setError("");
      setPrediction(null);

      try {
        const data = await predictMatch(p1!.player_key, p2!.player_key);
        if (!cancelled) setPrediction(data);
      } catch (e: any) {
        if (!cancelled) setError(e.message || "Prediction failed");
      } finally {
        if (!cancelled) setLoadingPrediction(false);
      }
    }

    runPrediction();

    return () => {
      cancelled = true;
    };
  }, [p1, p2]);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold text-gray-950">Predict a Match</h1>
        <p className="mt-2 text-gray-600">
          Search two players. The prediction updates automatically.
        </p>
      </header>

      <div className="grid gap-5 md:grid-cols-2">
        <PlayerSearch label="Player 1" onSelect={selectP1} />
        <PlayerSearch label="Player 2" onSelect={selectP2} />
      </div>

      {(p1Ratings || p2Ratings) && (
        <div className="grid gap-5">
          {p1Ratings && (
            <PlayerRatingsCard title="Player 1 ratings" ratings={p1Ratings} />
          )}

          {p2Ratings && (
            <PlayerRatingsCard title="Player 2 ratings" ratings={p2Ratings} />
          )}
        </div>
      )}

      {p1 && p2 && p1.player_key === p2.player_key && (
        <p className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          Choose two different players.
        </p>
      )}

      {loadingPrediction && (
        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <p className="font-semibold text-gray-950">
            Generating prediction...
          </p>
        </section>
      )}

      {error && <p className="text-red-600">{error}</p>}

      <PredictionResult prediction={prediction} />
    </div>
  );
}
