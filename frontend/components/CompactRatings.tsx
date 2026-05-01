import { SPORT_META, SPORTS } from "@/lib/sportColors";

export default function CompactRatings({
  title,
  ratings,
}: {
  title: string;
  ratings: any;
}) {
  if (!ratings) return null;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3">
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

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {SPORTS.map((sport) => {
          const meta = SPORT_META[sport];
          const r = ratings.ratings?.[sport];

          return (
            <div key={sport} className={`rounded-xl border p-3 ${meta.badge}`}>
              <div className="flex items-center justify-between">
                <p className="text-xs font-black">{sport}</p>
                <p className="text-xs opacity-70">{r?.games ?? 0} games</p>
              </div>

              <p className="mt-1 text-2xl font-black">
                {r?.display_rating ?? "—"}
              </p>

              <p className="truncate text-xs opacity-70">{meta.name}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
