"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/predict", label: "Predict" },
  { href: "/players", label: "Players" },
  { href: "/leaderboards", label: "Leaderboards" },
  { href: "/about", label: "About" },
];

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-xl">
      <nav className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            href="/"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3"
          >
            <Image
              src="/logo-icon.png"
              alt="RateMyRacket"
              width={44}
              height={44}
              priority
              className="h-11 w-11 object-contain transition-transform duration-200 hover:scale-105"
            />

            <div className="leading-tight">
              <p className="text-lg font-black tracking-tight text-slate-950">
                Rate<span className="text-green-600">My</span>Racket
              </p>
              <p className="hidden text-xs font-semibold text-slate-500 sm:block">
                Compare. Predict. Improve.
              </p>
            </div>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden items-center gap-1 md:flex">
            {LINKS.map((link) => {
              const active = isActive(pathname, link.href);

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-full px-4 py-2 text-sm font-black transition ${
                    active
                      ? "bg-slate-950 text-white shadow-sm"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Mobile Toggle */}
          <button
            onClick={() => setOpen((v) => !v)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-900 shadow-sm md:hidden"
            aria-label="Toggle navigation"
          >
            <div className="space-y-1.5">
              <span
                className={`block h-0.5 w-5 rounded bg-slate-900 transition ${
                  open ? "translate-y-2 rotate-45" : ""
                }`}
              />
              <span
                className={`block h-0.5 w-5 rounded bg-slate-900 transition ${
                  open ? "opacity-0" : ""
                }`}
              />
              <span
                className={`block h-0.5 w-5 rounded bg-slate-900 transition ${
                  open ? "-translate-y-2 -rotate-45" : ""
                }`}
              />
            </div>
          </button>
        </div>

        {/* Mobile Menu */}
        {open && (
          <div className="animate-slide-down pb-4 md:hidden">
            <div className="glass-card rounded-3xl p-2">
              {LINKS.map((link) => {
                const active = isActive(pathname, link.href);

                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className={`flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-black transition ${
                      active
                        ? "bg-slate-950 text-white"
                        : "text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    <span>{link.label}</span>
                    {active && <span>✓</span>}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
