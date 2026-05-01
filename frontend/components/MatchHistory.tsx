import Link from "next/link";

const SPORTS = ["TT", "BD", "SQ", "TN"];

function scoreForPlayer(score: any[], playerIsP1: boolean) {
  if (!score) return "-";
  return playerIsP1 ? (score[0] ?? "-") : (score[1] ?? "-");
}

function scoreForOpponent(score: any[], playerIsP1: boolean) {
  if (!score) return "-";
  return playerIsP1 ? (score[1] ?? "-") : (score[0] ?? "-");
}

function totalClass(won: boolean) {
  return won ? "text-emerald-700 font-extrabold" : "text-gray-400 font-bold";
}

function nameClass(won: boolean) {
  return won ? "text-gray-950 font-bold" : "text-gray-500 font-semibold";
}

function scoreClass(won: boolean) {
  return won ? "text-gray-950 font-bold" : "text-gray-400 font-semibold";
}

function winnerBadge(won: boolean) {
  if (!won) return null;

  return <span className="text-emerald-600 text-sm font-bold">✓</span>;
}

export default function MatchHistory({ matches }: { matches: any[] }) {
  if (!matches || matches.length === 0) {
    return (
      <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="text-xl font-bold text-gray-950">Match History</h3>
        <p className="mt-2 text-gray-600">No matches found.</p>
      </section>
    );
  }

  const sortedMatches = [...matches].sort((a, b) => {
    const av = a.datetime || `${a.date || ""} ${a.match_time || ""}`;
    const bv = b.datetime || `${b.date || ""} ${b.match_time || ""}`;

    const at = new Date(av).getTime();
    const bt = new Date(bv).getTime();

    return (Number.isNaN(bt) ? 0 : bt) - (Number.isNaN(at) ? 0 : at);
  });

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-xl font-bold text-gray-950">Match History</h3>

      <div className="space-y-3">
        {sortedMatches.map((m, i) => {
          const playerWon = m.match_result === "win";
          const opponentWon = m.match_result === "loss";

          return (
            <div
              key={i}
              className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-4 flex flex-wrap items-center gap-2 text-sm text-gray-500">
                <span className="font-medium">{m.date || "Unknown date"}</span>

                {m.match_time && (
                  <>
                    <span>·</span>
                    <span>{m.match_time}</span>
                  </>
                )}

                {m.tournament_name && (
                  <>
                    <span>·</span>
                    <span className="font-semibold text-gray-700">
                      {m.tournament_name}
                    </span>
                  </>
                )}

                {(m.draw || m.round) && (
                  <>
                    <span>·</span>
                    <span>{[m.draw, m.round].filter(Boolean).join(" · ")}</span>
                  </>
                )}
              </div>

              <div className="rounded-xl bg-gray-50 p-3">
                <div className="grid grid-cols-[minmax(180px,1fr)_repeat(4,48px)_70px] items-center gap-2 border-b border-gray-200 pb-2 text-xs font-bold uppercase tracking-wide text-gray-500">
                  <div>Player</div>
                  {SPORTS.map((sport) => (
                    <div key={sport} className="text-center">
                      {sport}
                    </div>
                  ))}
                  <div className="text-center">Total</div>
                </div>

                <div className="grid grid-cols-[minmax(180px,1fr)_repeat(4,48px)_70px] items-center gap-2 border-b border-gray-100 py-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`capitalize ${nameClass(playerWon)}`}>
                        {m.player_name}
                      </span>
                      {winnerBadge(playerWon)}
                    </div>
                    <div className="text-xs font-medium uppercase text-gray-400">
                      {m.player_country}
                    </div>
                  </div>

                  {SPORTS.map((sport) => {
                    const wonSport = m.sport_results?.[sport] === "win";

                    return (
                      <div
                        key={sport}
                        className={`text-center text-lg ${scoreClass(wonSport)}`}
                      >
                        {scoreForPlayer(m.scores?.[sport], m.player_is_p1)}
                      </div>
                    );
                  })}

                  <div
                    className={`text-center text-2xl ${totalClass(playerWon)}`}
                  >
                    {m.player_total}
                  </div>
                </div>

                <div className="grid grid-cols-[minmax(180px,1fr)_repeat(4,48px)_70px] items-center gap-2 pt-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/players/${encodeURIComponent(m.opponent_key)}`}
                        className={`capitalize hover:underline ${nameClass(
                          opponentWon,
                        )}`}
                      >
                        {m.opponent_name}
                      </Link>
                      {winnerBadge(opponentWon)}
                    </div>
                    <div className="text-xs font-medium uppercase text-gray-400">
                      {m.opponent_country}
                    </div>
                  </div>

                  {SPORTS.map((sport) => {
                    const wonSport = m.sport_results?.[sport] === "loss";

                    return (
                      <div
                        key={sport}
                        className={`text-center text-lg ${scoreClass(wonSport)}`}
                      >
                        {scoreForOpponent(m.scores?.[sport], m.player_is_p1)}
                      </div>
                    );
                  })}

                  <div
                    className={`text-center text-2xl ${totalClass(opponentWon)}`}
                  >
                    {m.opponent_total}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
