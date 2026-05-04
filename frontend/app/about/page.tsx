import Link from "next/link";

const SPORTS = [
  {
    code: "TT",
    name: "Table Tennis",
    mae: "±6 pts",
    color: "bg-blue-50 text-blue-700",
  },
  {
    code: "BD",
    name: "Badminton",
    mae: "±6 pts",
    color: "bg-red-50 text-red-700",
  },
  {
    code: "SQ",
    name: "Squash",
    mae: "±7 pts",
    color: "bg-amber-50 text-amber-700",
  },
  {
    code: "TN",
    name: "Tennis",
    mae: "±5 pts",
    color: "bg-emerald-50 text-emerald-700",
  },
];

export default function AboutPage() {
  return (
    <div className="space-y-8">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-emerald-100 blur-3xl opacity-60" />
        <div className="pointer-events-none absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-blue-100 blur-3xl opacity-60" />

        <div className="relative max-w-3xl">
          <p className="mb-3 w-fit rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-black uppercase tracking-wide text-slate-500">
            About the project
          </p>

          <h1 className="text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">
            Racketlon match prediction, built from real data.
          </h1>

          <p className="mt-5 text-base leading-7 text-slate-600 sm:text-lg">
            RateMyRacket is based on a full machine learning pipeline that
            predicts Racketlon matches across table tennis, badminton, squash,
            and tennis. It combines player ratings, recent form, and historical
            performance to estimate both match scores and winners.
          </p>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link href="/predict" className="primary-button text-center">
              Try a Prediction
            </Link>
            <Link href="/leaderboards" className="secondary-button text-center">
              View Leaderboards
            </Link>
          </div>
        </div>
      </section>

      {/* WHAT IT DOES */}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <h2 className="text-2xl font-black text-slate-950">
          What the model actually predicts
        </h2>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
          Instead of just predicting a winner, the model predicts the score
          difference in each sport, then combines them into a full match result.
          This makes predictions more realistic and more informative than a
          simple win/loss guess.
        </p>
      </section>

      {/* PERFORMANCE */}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <p className="text-xs font-black uppercase tracking-wide text-slate-500">
          Model performance
        </p>

        <h2 className="mt-1 text-2xl font-black text-slate-950">
          How accurate is it?
        </h2>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-3xl font-black text-slate-950">73.4%</p>
            <p className="mt-1 text-sm font-semibold text-slate-600">
              Winner accuracy
            </p>
            <p className="mt-2 text-xs text-slate-500">
              The model correctly predicts the winner about 3 out of 4 times.
            </p>
          </div>

          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-3xl font-black text-slate-950">±14 pts</p>
            <p className="mt-1 text-sm font-semibold text-slate-600">
              Match error (MAE)
            </p>
            <p className="mt-2 text-xs text-slate-500">
              Predictions are off by about 14 total points on average.
            </p>
          </div>
        </div>

        <p className="mt-6 max-w-2xl text-sm leading-6 text-slate-600">
          For example, if a match ends 80–70, the model might predict something
          like 75–68. It captures the overall margin well, even if it’s not
          exact down to every point.
        </p>
      </section>

      {/* Disclaimer */}
      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5 shadow-sm sm:p-6">
        <h2 className="text-lg font-black text-amber-900">
          Interpreting the results
        </h2>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-amber-800">
          These ratings and predictions are data-driven estimates, not official
          rankings. Their accuracy depends on the amount of available match
          data, how recently a player has competed, and the level of opponents
          they typically face.
        </p>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-amber-800">
          Players with fewer matches or highly uneven competition histories may
          have less stable ratings, and predictions for those matchups may be
          less reliable.
        </p>
      </section>

      {/* SPORT LEVEL */}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <p className="text-xs font-black uppercase tracking-wide text-slate-500">
          Sport-level accuracy
        </p>

        <h2 className="mt-1 text-2xl font-black text-slate-950">
          Per-sport predictions
        </h2>

        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {SPORTS.map((sport) => (
            <div
              key={sport.code}
              className={`rounded-2xl p-4 text-center ${sport.color}`}
            >
              <p className="text-xs font-black">{sport.code}</p>
              <p className="mt-1 text-lg font-black">{sport.mae}</p>
              <p className="text-xs">{sport.name}</p>
            </div>
          ))}
        </div>

        <p className="mt-4 max-w-2xl text-sm text-slate-600">
          Each sport is predicted within about 5–7 points on average. These
          errors accumulate across the four sports, leading to the overall match
          error.
        </p>
      </section>

      {/* PDF PREVIEW */}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-slate-500">
              Research paper
            </p>
            <h2 className="mt-1 text-2xl font-black text-slate-950">
              Full methodology & results
            </h2>
          </div>

          <a
            href="/paper.pdf"
            target="_blank"
            className="secondary-button text-center"
          >
            Open PDF
          </a>
        </div>

        <div className="mt-5 overflow-hidden rounded-2xl border border-slate-200">
          <iframe src="/paper.pdf" className="h-[400px] sm:h-[500px] w-full" />
        </div>
      </section>

      {/* KEY IDEA */}
      <section className="rounded-[2rem] border border-slate-200 bg-slate-950 p-6 text-white shadow-sm sm:p-8">
        <h2 className="text-2xl font-black">Key idea</h2>

        <p className="mt-4 text-lg font-semibold">
          Good features matter more than complex models.
        </p>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
          The biggest improvement comes from how player performance is
          represented — ratings, recent form, and matchup history — not from
          using more complex machine learning models.
        </p>
      </section>

      {/* AUTHOR */}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <h2 className="text-2xl font-black text-slate-950">About the author</h2>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
          Built by Zain Magdon-Ismail as a Racketlon analytics and prediction
          project.
        </p>
      </section>
    </div>
  );
}
