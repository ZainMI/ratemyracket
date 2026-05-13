import Image from "next/image";
import Link from "next/link";

const FEATURES = [
  {
    title: "Predict",
    text: "Compare two players and get a full four-sport score prediction.",
    color: "bg-blue-50 text-blue-700 border-blue-100",
  },
  {
    title: "Ratings",
    text: "See player strength across table tennis, badminton, squash, and tennis.",
    color: "bg-rose-50 text-rose-700 border-rose-100",
  },
  {
    title: "History",
    text: "Review match results, tournaments, rounds, and score breakdowns.",
    color: "bg-orange-50 text-orange-700 border-orange-100",
  },
  {
    title: "Rankings",
    text: "Browse leaderboards overall or by individual sport.",
    color: "bg-green-50 text-green-700 border-green-100",
  },
];

const SPORTS = [
  { code: "TT", label: "Table Tennis", color: "bg-blue-50 text-blue-700" },
  { code: "BD", label: "Badminton", color: "bg-rose-50 text-rose-700" },
  { code: "SQ", label: "Squash", color: "bg-orange-50 text-orange-700" },
  { code: "TN", label: "Tennis", color: "bg-green-50 text-green-700" },
];

export default function HomePage() {
  return (
    <div className="space-y-8 pb-8">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-8 lg:grid lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-8">
        {/* Background glow */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-16 right-10 h-40 w-40 rounded-full bg-blue-100 blur-3xl opacity-40" />
          <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-green-100 blur-3xl opacity-40" />
        </div>

        {/* LEFT CONTENT */}
        <div className="relative z-10 text-center sm:text-left">
          {/* LOGO MOBILE */}
          <div className="relative mx-auto mt-2 mb-3 flex h-48 items-center justify-center lg:hidden">
            <div className="absolute h-48 w-48 rounded-full bg-slate-200 blur-3xl opacity-45" />

            <div className="relative h-80 w-80 -translate-y-2">
              <Image
                src="/logo-icon.png"
                alt="RateMyRacket logo"
                fill
                sizes="320px"
                priority
                className="object-contain drop-shadow-[0_24px_45px_rgba(15,23,42,0.20)]"
              />
            </div>
          </div>

          <p className="mx-auto mb-3 w-fit rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-black uppercase tracking-wide text-slate-500 sm:mx-0">
            Racketlon analytics
          </p>

          <h1 className="text-4xl font-black tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
            Rate.
            <br className="sm:hidden" /> Compare.
            <br className="sm:hidden" /> Predict.
          </h1>

          <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-slate-600 sm:mx-0 sm:text-lg">
            Explore Racketlon ratings, compare players, predict matchups, and
            review performance across all four sports.
          </p>

          <div className="mt-6 grid gap-3 sm:flex">
            <Link href="/predict" className="primary-button text-center">
              Predict a Match
            </Link>

            <Link href="/leaderboards" className="secondary-button text-center">
              View Leaderboards
            </Link>
          </div>
        </div>

        {/* LOGO DESKTOP */}
        <div className="relative z-10 mt-8 hidden justify-center lg:flex">
          <div className="absolute h-64 w-64 rounded-full bg-slate-200 blur-3xl opacity-45" />

          <div className="relative h-80 w-80 -translate-y-2">
            <Image
              src="/logo-icon.png"
              alt="RateMyRacket logo"
              fill
              sizes="320px"
              priority
              className="object-contain drop-shadow-[0_28px_55px_rgba(15,23,42,0.20)]"
            />
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {FEATURES.map((feature) => (
          <div
            key={feature.title}
            className={`rounded-2xl border p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md ${feature.color}`}
          >
            <h3 className="text-base font-black">{feature.title}</h3>
            <p className="mt-1 text-sm leading-5 opacity-80">{feature.text}</p>
          </div>
        ))}
      </section>

      {/* ORGANIZATIONS */}
      <section className="rounded-[2rem] border border-slate-200 bg-white px-6 py-8 shadow-sm">
        <div className="flex flex-col items-center justify-center text-center">
          <p className="text-xs font-black uppercase tracking-[0.25em] text-slate-500">
            Used by players & organizations
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-10">
            <Image
              src="/usa_racketlon.png"
              alt="USA Racketlon"
              width={420}
              height={160}
              className="h-24 w-auto object-contain opacity-90 transition hover:opacity-100"
            />
          </div>
        </div>
      </section>

      {/* SPORTS */}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="mb-4">
          <p className="text-xs font-black uppercase tracking-wide text-slate-500">
            Four sports. One score.
          </p>

          <h2 className="mt-1 text-2xl font-black text-slate-950">
            Built for the full Racketlon format.
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {SPORTS.map((sport) => (
            <div key={sport.code} className={`rounded-2xl p-4 ${sport.color}`}>
              <p className="text-xs font-black">{sport.code}</p>
              <p className="mt-1 text-sm font-black">{sport.label}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
