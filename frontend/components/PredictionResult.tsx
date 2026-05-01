import type { Prediction } from "@/lib/types";
import { SPORT_META, SPORTS } from "@/lib/sportColors";

function marginText(margin: number) {
  return margin > 0 ? `+${margin}` : `${margin}`;
}

export default function PredictionResult({
  prediction,
}: {
  prediction: Prediction | null;
}) {
  if (!prediction) return null;

  const p1 = prediction.player1_name || prediction.player1;
  const p2 = prediction.player2_name || prediction.player2;

  const p1Wins = prediction.total_diff > 0;
  const p2Wins = prediction.total_diff < 0;

  return (
    <section className="glass-card rounded-3xl p-4 sm:p-6">
      <div className="mb-6">
        <p className="text-sm font-bold uppercase tracking-wide text-slate-500">
          Predicted Result
        </p>

        <div className="mt-3 grid gap-3 lg:grid-cols-[1fr_auto_1fr] lg:items-center">
          <ScoreCard name={p1} total={prediction.total_p1} won={p1Wins} />
          <div className="text-center text-lg font-black text-slate-400 lg:text-2xl">
            vs
          </div>
          <ScoreCard name={p2} total={prediction.total_p2} won={p2Wins} />
        </div>

        <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-sm font-semibold text-slate-500">Winner</p>
          <p className="mt-1 text-3xl font-black capitalize text-slate-950">
            {prediction.winner}
          </p>
          <p className="mt-1 text-slate-600">
            Margin:{" "}
            <span className="font-black text-slate-950">
              {marginText(prediction.total_diff)}
            </span>
          </p>
        </div>
      </div>

      <div>
        <h3 className="mb-3 text-xl font-black text-slate-950">
          Sport Breakdown
        </h3>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {SPORTS.map((sport) => {
            const meta = SPORT_META[sport];
            const result = prediction.sports?.[sport];

            if (!result) return null;

            const sportP1Wins = result.score_p1 > result.score_p2;
            const sportP2Wins = result.score_p2 > result.score_p1;

            return (
              <div
                key={sport}
                className={`rounded-2xl border bg-white p-4 shadow-sm ${meta.border}`}
              >
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <p className={`text-xs font-black ${meta.text}`}>{sport}</p>
                    <h4 className="font-black text-slate-950">{meta.name}</h4>
                  </div>

                  <div className={`h-3 w-3 rounded-full ${meta.bg}`} />
                </div>

                <SportScoreRow
                  name={p1}
                  score={result.score_p1}
                  won={sportP1Wins}
                />
                <SportScoreRow
                  name={p2}
                  score={result.score_p2}
                  won={sportP2Wins}
                />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function ScoreCard({
  name,
  total,
  won,
}: {
  name: string;
  total: number;
  won: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border p-4 sm:p-5 ${
        won ? "border-emerald-200 bg-emerald-50" : "border-slate-200 bg-white"
      }`}
    >
      <h3 className="text-lg font-black capitalize text-slate-950">{name}</h3>

      <p
        className={`mt-2 text-4xl font-black sm:text-5xl ${
          won ? "text-emerald-700" : "text-slate-800"
        }`}
      >
        {total}
      </p>
    </div>
  );
}

function SportScoreRow({
  name,
  score,
  won,
}: {
  name: string;
  score: number;
  won: boolean;
}) {
  return (
    <div
      className={`mt-2 flex items-center justify-between rounded-xl px-3 py-2 ${
        won ? "bg-slate-100 text-slate-950" : "bg-white text-slate-500"
      }`}
    >
      <span className="truncate pr-2 text-sm capitalize">{name}</span>
      <span className="text-xl font-black">{score}</span>
    </div>
  );
}
