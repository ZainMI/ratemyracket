export const SPORT_META = {
  TT: {
    key: "TT",
    name: "Table Tennis",
    shortName: "TT",
    badge: "bg-blue-50 text-blue-700 border-blue-100",
    text: "text-blue-700",
    bg: "bg-blue-50",
    border: "border-blue-100",
    dot: "bg-blue-400",
  },
  BD: {
    key: "BD",
    name: "Badminton",
    shortName: "BD",
    badge: "bg-rose-50 text-rose-700 border-rose-100",
    text: "text-rose-700",
    bg: "bg-rose-50",
    border: "border-rose-100",
    dot: "bg-rose-400",
  },
  SQ: {
    key: "SQ",
    name: "Squash",
    shortName: "SQ",
    badge: "bg-orange-100 text-orange-800 border-orange-200",
    text: "text-orange-800",
    bg: "bg-orange-100",
    border: "border-orange-200",
    dot: "bg-orange-500",
  },
  TN: {
    key: "TN",
    name: "Tennis",
    shortName: "TN",
    badge: "bg-emerald-50 text-emerald-700 border-emerald-100",
    text: "text-emerald-700",
    bg: "bg-emerald-50",
    border: "border-emerald-100",
    dot: "bg-emerald-400",
  },
} as const;

export const SPORTS = ["TT", "BD", "SQ", "TN"] as const;
export type SportKey = keyof typeof SPORT_META;
