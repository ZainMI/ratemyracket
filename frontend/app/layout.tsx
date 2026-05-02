import "./globals.css";
import Navbar from "@/components/Navbar";
import PageTransition from "@/components/PageTransition";

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

        {/* Main content */}
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
          <PageTransition>{children}</PageTransition>
        </main>

        {/* Footer */}
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
                    href="mailto:your-email@example.com"
                    className="text-emerald-600 hover:underline"
                  >
                    zainmagdon@gmail.com
                  </a>
                </p>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
