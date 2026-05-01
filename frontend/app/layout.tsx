import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "RacketRating",
  description: "Racketlon predictions and player ratings",
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
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
