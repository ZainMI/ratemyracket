import Link from "next/link";

export default function HomePage() {
  return (
    <section className="grid gap-10 py-16 md:grid-cols-2 md:items-center">
      <div>
        <p className="mb-3 text-sm font-semibold text-emerald-700">
          Racketlon prediction engine
        </p>

        <h1 className="text-5xl font-bold tracking-tight text-gray-950">
          Predict Racketlon matches across all four sports.
        </h1>

        <p className="mt-5 text-lg leading-8 text-gray-700">
          RacketRating uses sport-specific ratings, recent form, head-to-head
          history, and machine learning to predict match outcomes.
        </p>

        <div className="mt-8 flex gap-3">
          <Link
            href="/predict"
            className="rounded-xl bg-emerald-600 px-5 py-3 font-semibold text-white hover:bg-emerald-500"
          >
            Predict a Match
          </Link>

          <Link
            href="/players"
            className="rounded-xl border border-gray-300 bg-white px-5 py-3 font-semibold text-gray-900 hover:bg-gray-50"
          >
            Search Players
          </Link>
        </div>
      </div>

      <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-bold text-gray-950">Model Pipeline</h2>

        <div className="space-y-3">
          {[
            "Dynamic sport ratings",
            "Recent form and momentum",
            "Head-to-head history",
            "CatBoost match prediction",
          ].map((item) => (
            <div
              key={item}
              className="rounded-xl border border-gray-200 bg-gray-50 p-4 font-medium text-gray-800"
            >
              {item}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
