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

function scoreClass(won: boolean) {
  return won ? "font-black text-gray-950" : "font-semibold text-gray-400";
}

function totalClass(won: boolean) {
  return won ? "font-black text-emerald-700" : "font-bold text-gray-400";
}

function Check({ show }: { show: boolean }) {
  if (!show) return null;
  return <span className="ml-1 text-emerald-600">✓</span>;
}

export default function MatchHistory({ matches }: { matches: any[] }) {
  if (!matches || matches.length === 0) {
    return (
      <section className="glass-card rounded-3xl p-4 sm:p-6">
        <h3 className="text-xl font-bold text-gray-950">Match History</h3>
        <p className="mt-2 text-gray-600">No matches found.</p>
      </section>
    );
  }

  const sortedMatches = [...matches].sort((a, b) => {
    const av = a.datetime || `${a.date || ""} ${a.match_time || ""}`;
    const bv = b.datetime || `${b.date || ""} ${b.match_time || ""}`;
    return new Date(bv).getTime() - new Date(av).getTime();
  });

  return (
    <section className="glass-card rounded-3xl p-4 sm:p-6">
      <h3 className="mb-4 text-xl font-black text-gray-950">Match History</h3>

      <div className="space-y-3">
        {sortedMatches.map((m, i) => {
          const playerWon = m.match_result === "win";
          const opponentWon = m.match_result === "loss";

          return (
            <article
              key={i}
              className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-4 space-y-1 text-sm text-gray-500">
                <div className="flex flex-wrap gap-2">
                  <span className="font-bold">{m.date || "Unknown date"}</span>
                  {m.match_time && <span>· {m.match_time}</span>}
                </div>

                {m.tournament_name && (
                  <p className="font-bold leading-snug text-gray-700">
                    {m.tournament_name}
                  </p>
                )}

                {(m.draw || m.round) && (
                  <p className="leading-snug">
                    {[m.draw, m.round].filter(Boolean).join(" · ")}
                  </p>
                )}
              </div>

              <div className="rounded-2xl bg-gray-50 p-3">
                <div className="grid grid-cols-[minmax(0,1fr)_44px] gap-2 border-b border-gray-200 pb-2 text-xs font-black uppercase tracking-wide text-gray-500 sm:grid-cols-[minmax(0,1fr)_52px_52px_52px_52px_64px]">
                  <div>Player</div>

                  <div className="hidden text-center sm:block">TT</div>
                  <div className="hidden text-center sm:block">BD</div>
                  <div className="hidden text-center sm:block">SQ</div>
                  <div className="hidden text-center sm:block">TN</div>

                  <div className="text-center">Total</div>
                </div>

                <PlayerRow
                  name={m.player_name}
                  country={m.player_country}
                  won={playerWon}
                  total={m.player_total}
                  scores={SPORTS.map((sport) =>
                    scoreForPlayer(m.scores?.[sport], m.player_is_p1),
                  )}
                  sportWins={SPORTS.map(
                    (sport) => m.sport_results?.[sport] === "win",
                  )}
                  isLink={false}
                />

                <PlayerRow
                  name={m.opponent_name}
                  country={m.opponent_country}
                  won={opponentWon}
                  total={m.opponent_total}
                  scores={SPORTS.map((sport) =>
                    scoreForOpponent(m.scores?.[sport], m.player_is_p1),
                  )}
                  sportWins={SPORTS.map(
                    (sport) => m.sport_results?.[sport] === "loss",
                  )}
                  href={`/players/${encodeURIComponent(m.opponent_key)}`}
                  isLink
                />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function PlayerRow({
  name,
  country,
  won,
  total,
  scores,
  sportWins,
  href,
  isLink,
}: {
  name: string;
  country: string;
  won: boolean;
  total: number;
  scores: any[];
  sportWins: boolean[];
  href?: string;
  isLink: boolean;
}) {
  const NameBlock = (
    <div className="min-w-0">
      <div
        className={`truncate capitalize ${
          won ? "font-black text-gray-950" : "font-semibold text-gray-500"
        }`}
      >
        {name}
        <Check show={won} />
      </div>

      <div className="text-xs font-semibold uppercase text-gray-400">
        {country}
      </div>

      <div className="mt-2 grid grid-cols-4 gap-1 sm:hidden">
        {SPORTS.map((sport, idx) => (
          <div
            key={sport}
            className="rounded-lg bg-white px-2 py-1 text-center"
          >
            <p className="text-[10px] font-black text-gray-400">{sport}</p>
            <p className={`text-sm ${scoreClass(sportWins[idx])}`}>
              {scores[idx]}
            </p>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-[minmax(0,1fr)_44px] items-center gap-2 border-b border-gray-100 py-3 last:border-b-0 sm:grid-cols-[minmax(0,1fr)_52px_52px_52px_52px_64px]">
      {isLink && href ? (
        <Link
          href={href}
          className="min-w-0 hover:text-emerald-700 hover:underline"
        >
          {NameBlock}
        </Link>
      ) : (
        NameBlock
      )}

      {SPORTS.map((sport, idx) => (
        <div
          key={sport}
          className={`hidden text-center text-lg sm:block ${scoreClass(
            sportWins[idx],
          )}`}
        >
          {scores[idx]}
        </div>
      ))}

      <div className={`text-center text-xl ${totalClass(won)}`}>{total}</div>
    </div>
  );
}
