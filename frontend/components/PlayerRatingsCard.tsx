import FavoriteButton from "@/components/FavoriteButton";

const SPORTS = [
  { key: "TT", label: "Table Tennis" },
  { key: "BD", label: "Badminton" },
  { key: "SQ", label: "Squash" },
  { key: "TN", label: "Tennis" },
];

export default function PlayerRatingsCard({
  title,
  ratings,
}: {
  title: string;
  ratings: any;
}) {
  if (!ratings) return null;

  const favoritePlayer = {
    player_key: ratings.player_key,
    player_name: ratings.player_name,
    country: ratings.country || "",
  };

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <h3 className="text-xl font-bold capitalize text-gray-950">
            {ratings.player_name}
          </h3>
          <p className="text-sm text-gray-600">
            {ratings.country || "Unknown country"}
          </p>
        </div>

        {ratings.player_key && <FavoriteButton player={favoritePlayer} />}
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        {SPORTS.map((sport) => {
          const r = ratings.ratings?.[sport.key];

          return (
            <div
              key={sport.key}
              className="rounded-xl border border-gray-200 bg-gray-50 p-4"
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                {sport.key}
              </p>
              <p className="text-sm text-gray-600">{sport.label}</p>

              <p className="mt-2 text-3xl font-bold text-gray-950">
                {r?.display_rating ?? "—"}
              </p>

              <p className="mt-1 text-sm text-gray-600">
                {r?.games ?? 0} games
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
