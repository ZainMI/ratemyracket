import Link from "next/link";
import { SPORT_META, SPORTS } from "@/lib/sportColors";
import type { PlayerRatings } from "@/lib/types";
import FavoriteButton from "@/components/FavoriteButton";

export default function CompactRatings({
  title,
  ratings,
}: {
  title: string;
  ratings: PlayerRatings;
}) {
  if (!ratings) return null;

  const favoritePlayer = {
    player_key: ratings.player_key || ratings.player_name,
    player_name: ratings.player_name,
    country: ratings.country || "",
  };
  const overall = ratings.overall;
  const division = ratings.gender === "female" ? "Women" : "Men";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      {/* HEADER */}
      <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
            {title}
          </p>

          <h3 className="text-lg font-black capitalize text-slate-950">
            {ratings.player_name}
          </h3>

          <p className="text-xs font-bold uppercase text-slate-500">
            {ratings.country || "Unknown"}
          </p>
        </div>

        {/* ⭐ Favorite button */}
        <FavoriteButton player={favoritePlayer} />
      </div>

      {/* OVERALL RANKING */}
      <div className="mb-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-slate-500">
              Overall rating
            </p>
            <p className="mt-1 text-3xl font-black tracking-tight text-slate-950">
              {overall?.display_rating ?? "—"}
            </p>
            <p className="mt-1 text-xs font-semibold text-slate-500">
              Across all four sports · {overall?.games ?? 0} games
            </p>
          </div>

          <div className="text-right">
            <p className="text-lg font-black text-slate-950">
              {overall?.rank ? `Rank ${overall.rank}` : "Unranked"}
            </p>
            <p className="text-xs font-semibold text-slate-500">
              {overall?.ranked_players
                ? `${division} · ${overall.ranked_players.toLocaleString()} players`
                : "Needs 3 games in a sport"}
            </p>
          </div>
        </div>
      </div>

      {/* SPORT RATINGS GRID */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {SPORTS.map((sport) => {
          const meta = SPORT_META[sport];
          const r = ratings.ratings?.[sport];

          return (
            <div key={sport} className={`rounded-xl border p-3 ${meta.badge}`}>
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-black">{sport}</p>
                <p className="text-xs font-black">
                  {r?.rank ? `Rank ${r.rank}` : "Unranked"}
                </p>
              </div>

              <p className="mt-1 text-2xl font-black">
                {r?.display_rating ?? "—"}
              </p>

              <div className="mt-0.5 flex items-center justify-between gap-2 text-xs opacity-70">
                <p className="truncate">{meta.name}</p>
                <p className="shrink-0">{r?.games ?? 0} games</p>
              </div>

            </div>
          );
        })}
      </div>

      <div className="mt-3 text-right">
        <Link
          href="/leaderboards"
          className="text-xs font-black text-emerald-700 transition hover:text-emerald-600 hover:underline"
        >
          View full leaderboards →
        </Link>
      </div>
    </div>
  );
}
