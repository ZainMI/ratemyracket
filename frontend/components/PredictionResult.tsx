import type { Prediction } from "@/lib/types";

const SPORTS = [
  { key: "TT", name: "Table Tennis" },
  { key: "BD", name: "Badminton" },
  { key: "SQ", name: "Squash" },
  { key: "TN", name: "Tennis" },
];

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
    <section className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
      {/* MAIN RESULT */}
      <div className="mb-6">
        <p className="text-sm font-medium text-gray-500">Match Result</p>

        <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto_1fr] md:items-center">
          <div
            className={`rounded-2xl border p-5 ${
              p1Wins
                ? "border-emerald-300 bg-emerald-50"
                : "border-gray-200 bg-gray-50"
            }`}
          >
            <h3 className="text-lg font-semibold capitalize text-gray-950">
              {p1}
            </h3>
            <p className="mt-2 text-5xl font-bold text-gray-950">
              {prediction.total_p1}
            </p>
          </div>

          <div className="text-center text-2xl font-bold text-gray-400">vs</div>

          <div
            className={`rounded-2xl border p-5 ${
              p2Wins
                ? "border-emerald-300 bg-emerald-50"
                : "border-gray-200 bg-gray-50"
            }`}
          >
            <h3 className="text-lg font-semibold capitalize text-gray-950">
              {p2}
            </h3>
            <p className="mt-2 text-5xl font-bold text-gray-950">
              {prediction.total_p2}
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-2xl bg-gray-50 p-5">
          <p className="text-sm text-gray-500">Winner</p>
          <p className="mt-1 text-3xl font-bold text-emerald-700 capitalize">
            {prediction.winner}
          </p>
          <p className="mt-1 text-gray-700">
            Margin:{" "}
            <span className="font-semibold text-gray-950">
              {marginText(prediction.total_diff)}
            </span>
          </p>
        </div>
      </div>

      {/* SPORT BREAKDOWN */}
      <div>
        <h3 className="mb-3 text-xl font-bold text-gray-950">
          Sport Breakdown
        </h3>

        <div className="grid gap-3 md:grid-cols-4">
          {SPORTS.map((sport) => {
            const result = prediction.sports?.[sport.key];
            if (!result) return null;

            const sportP1Wins = result.score_p1 > result.score_p2;
            const sportP2Wins = result.score_p2 > result.score_p1;

            return (
              <div
                key={sport.key}
                className="rounded-2xl border border-gray-200 bg-gray-50 p-4"
              >
                <div className="mb-3">
                  <p className="text-xs font-semibold text-gray-500">
                    {sport.name}
                  </p>
                </div>

                <div className="space-y-2">
                  <div
                    className={`flex justify-between rounded-xl px-3 py-2 ${
                      sportP1Wins ? "bg-emerald-100" : "bg-white"
                    }`}
                  >
                    <span className="text-sm capitalize text-gray-700">
                      {p1}
                    </span>
                    <span className="font-bold text-gray-950">
                      {result.score_p1}
                    </span>
                  </div>

                  <div
                    className={`flex justify-between rounded-xl px-3 py-2 ${
                      sportP2Wins ? "bg-emerald-100" : "bg-white"
                    }`}
                  >
                    <span className="text-sm capitalize text-gray-700">
                      {p2}
                    </span>
                    <span className="font-bold text-gray-950">
                      {result.score_p2}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
