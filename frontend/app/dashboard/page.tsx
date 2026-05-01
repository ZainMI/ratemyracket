export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold text-gray-950">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Your favorite players will appear here once accounts are connected.
        </p>
      </header>

      <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-bold text-gray-950">Favorite Players</h2>
        <p className="mt-2 text-gray-600">
          Account login and favorite-player saving will be added next.
        </p>
      </section>
    </div>
  );
}
