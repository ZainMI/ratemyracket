export default function MatchHistorySkeleton() {
  return (
    <section className="glass-card rounded-3xl p-4 sm:p-6">
      <div className="mb-4 h-7 w-40 animate-pulse rounded-lg bg-slate-200" />

      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <article
            key={i}
            className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="mb-4 space-y-2">
              <div className="h-4 w-28 animate-pulse rounded bg-slate-200" />
              <div className="h-4 w-64 max-w-full animate-pulse rounded bg-slate-100" />
              <div className="h-4 w-44 animate-pulse rounded bg-slate-100" />
            </div>

            <div className="rounded-2xl bg-slate-50 p-3">
              <div className="mb-3 grid grid-cols-[minmax(0,1fr)_44px] gap-2 sm:grid-cols-[minmax(0,1fr)_52px_52px_52px_52px_64px]">
                <div className="h-4 animate-pulse rounded bg-slate-200" />
                <div className="h-4 animate-pulse rounded bg-slate-200" />
                <div className="hidden h-4 animate-pulse rounded bg-slate-200 sm:block" />
                <div className="hidden h-4 animate-pulse rounded bg-slate-200 sm:block" />
                <div className="hidden h-4 animate-pulse rounded bg-slate-200 sm:block" />
                <div className="hidden h-4 animate-pulse rounded bg-slate-200 sm:block" />
              </div>

              <div className="mb-3 h-16 animate-pulse rounded-xl bg-white" />
              <div className="h-16 animate-pulse rounded-xl bg-white" />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
