"use client";

import { useEffect, useState } from "react";
import PlayerSearch from "@/components/PlayerSearch";
import PredictionResult from "@/components/PredictionResult";
import CompactRatings from "@/components/CompactRatings";
import MatchHistory from "@/components/MatchHistory";
import {
  predictMatch,
  getPlayerRatings,
  getHeadToHeadMatches,
} from "@/lib/api";
import type { Player, Prediction } from "@/lib/types";

export default function PredictPage() {
  const [p1, setP1] = useState<Player | null>(null);
  const [p2, setP2] = useState<Player | null>(null);

  const [p1Ratings, setP1Ratings] = useState<any>(null);
  const [p2Ratings, setP2Ratings] = useState<any>(null);
  const [showRatings, setShowRatings] = useState(false);

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [headToHeadMatches, setHeadToHeadMatches] = useState<
    Record<string, unknown>[]
  >([]);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [loadingHeadToHead, setLoadingHeadToHead] = useState(false);
  const [error, setError] = useState("");

  async function selectP1(player: Player) {
    setP1(player);
    setPrediction(null);
    setHeadToHeadMatches([]);
    setLoadingPrediction(false);
    setLoadingHeadToHead(false);
    setP1Ratings(await getPlayerRatings(player.player_key));
  }

  async function selectP2(player: Player) {
    setP2(player);
    setPrediction(null);
    setHeadToHeadMatches([]);
    setLoadingPrediction(false);
    setLoadingHeadToHead(false);
    setP2Ratings(await getPlayerRatings(player.player_key));
  }

  useEffect(() => {
    if (!p1 || !p2) return;
    if (p1.player_key === p2.player_key) return;

    let cancelled = false;

    async function runPrediction() {
      setLoadingPrediction(true);
      setLoadingHeadToHead(true);
      setError("");
      setPrediction(null);
      setHeadToHeadMatches([]);

      const [predictionResult, headToHeadResult] = await Promise.allSettled([
        predictMatch(p1!.player_key, p2!.player_key),
        getHeadToHeadMatches(p1!.player_key, p2!.player_key),
      ]);

      if (cancelled) return;

      if (predictionResult.status === "fulfilled") {
        setPrediction(predictionResult.value);
      } else {
        const reason = predictionResult.reason;
        setError(reason?.message || "Prediction failed");
      }

      if (headToHeadResult.status === "fulfilled") {
        setHeadToHeadMatches(headToHeadResult.value);
      }

      setLoadingPrediction(false);
      setLoadingHeadToHead(false);
    }

    runPrediction();

    return () => {
      cancelled = true;
    };
  }, [p1, p2]);

  return (
    <div className="space-y-5">
      <header>
        <h1 className="page-title">Predict a Match</h1>
        <p className="page-subtitle">
          Search two players and get an automatic Racketlon score prediction.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <PlayerSearch label="Player 1" onSelect={selectP1} />
        <PlayerSearch label="Player 2" onSelect={selectP2} />
      </div>

      {(p1Ratings || p2Ratings) && (
        <section className="glass-card rounded-3xl p-4">
          <button
            onClick={() => setShowRatings((v) => !v)}
            className="flex w-full items-center justify-between font-bold text-gray-950"
          >
            <span>Player Ratings</span>
            <span className="text-emerald-600">
              {showRatings ? "Hide" : "Show"}
            </span>
          </button>

          {showRatings && (
            <div className="mt-4 grid gap-4 animate-fade-in">
              {p1Ratings && (
                <CompactRatings title="Player 1" ratings={p1Ratings} />
              )}
              {p2Ratings && (
                <CompactRatings title="Player 2" ratings={p2Ratings} />
              )}
            </div>
          )}
        </section>
      )}

      {p1 && p2 && p1.player_key === p2.player_key && (
        <p className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          Choose two different players.
        </p>
      )}

      {loadingPrediction && (
        <section className="glass-card rounded-3xl p-6">
          <p className="font-semibold text-gray-950">
            Generating prediction...
          </p>
        </section>
      )}

      {error && <p className="text-red-600">{error}</p>}

      <PredictionResult prediction={prediction} />

      {p1 && p2 && p1.player_key !== p2.player_key && (
        loadingHeadToHead ? (
          <section className="glass-card rounded-3xl p-4 sm:p-6">
            <div className="h-6 w-64 animate-pulse rounded bg-slate-200" />
            <div className="mt-4 h-32 animate-pulse rounded-2xl bg-slate-100" />
          </section>
        ) : (
          <MatchHistory
            matches={headToHeadMatches}
            title="Past Head-to-Head Matches"
            emptyMessage="These players have no recorded matches against each other."
          />
        )
      )}
    </div>
  );
}
