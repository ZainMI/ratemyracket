import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-xl font-bold text-gray-950">
          Racket<span className="text-emerald-600">Rating</span>
        </Link>

        <div className="flex gap-5 text-sm font-medium text-gray-700">
          <Link href="/" className="hover:text-emerald-600">
            Home
          </Link>
          <Link href="/predict" className="hover:text-emerald-600">
            Predict
          </Link>
          <Link href="/players" className="hover:text-emerald-600">
            Players
          </Link>
          <Link href="/dashboard" className="hover:text-emerald-600">
            Dashboard
          </Link>
          <Link href="/leaderboards" className="hover:text-emerald-600">
            Leaderboards
          </Link>
        </div>
      </div>
    </nav>
  );
}
