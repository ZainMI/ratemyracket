import "./globals.css";
import Navbar from "@/components/Navbar";
import PageTransition from "@/components/PageTransition";

export const metadata = {
  title: {
    default: "Rate My Racket",
    template: "%s | RateMyRacket",
  },
  description: "Compare, predict, and explore Racketlon player ratings.",
  icons: {
    icon: "/logo-icon-white.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />

        <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
          <PageTransition>{children}</PageTransition>
        </main>
      </body>
    </html>
  );
}
