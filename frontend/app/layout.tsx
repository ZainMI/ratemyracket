import "./globals.css";
import Navbar from "@/components/Navbar";
import PageTransition from "@/components/PageTransition";
import { Analytics } from "@vercel/analytics/next";

export const metadata = {
  title: {
    default: "RateMyRacket",
    template: "%s | RateMyRacket",
  },
  description: "Compare, predict, and explore Racketlon player ratings.",
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <Navbar />

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
          <PageTransition>{children}</PageTransition>
        </main>

        <footer className="border-t border-slate-200 bg-white">
          <div className="mx-auto max-w-6xl px-4 py-6 text-sm text-slate-600 sm:px-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              {/* Left */}
              <div>
                <p className="font-semibold text-slate-900">RateMyRacket</p>
                <p className="mt-1 text-xs text-slate-500">
                  Racketlon ratings, predictions, and player analytics.
                </p>
              </div>

              {/* Right */}
              <div className="text-xs text-slate-500 sm:text-right">
                <p>© {new Date().getFullYear()} RateMyRacket</p>

                <p className="mt-1">
                  Built by{" "}
                  <span className="font-semibold text-slate-700">
                    Zain Magdon-Ismail
                  </span>
                </p>

                <p className="mt-1">
                  Contact:{" "}
                  <a
                    href="mailto:zain@ratemyracket.com"
                    className="text-emerald-600 hover:underline"
                  >
                    zain@ratemyracket.com
                  </a>
                </p>
                <p className="mt-1">
                  <a
                    href="https://docs.google.com/forms/d/e/1FAIpQLSf3xff7KwTyutMr08EZgTEJuSGOlOQzsaqu36qXIleq5qg4Og/viewform?usp=publish-editor"
                    target="_blank"
                    className="text-slate-500 hover:text-slate-900 hover:underline"
                  >
                    Report a bug / Leave feedback
                  </a>
                </p>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="mt-5 border-t border-slate-100 pt-4 text-xs leading-5 text-slate-400">
              Ratings and predictions are data-driven estimates, not official
              rankings. They may be influenced by match volume, recent activity,
              opponent strength, and the level of competition a player typically
              faces.
            </div>
          </div>
        </footer>
        <Analytics />
      </body>
    </html>
  );
}
