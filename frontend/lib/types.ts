export type Player = {
  player_key: string;
  player_name: string;
  country?: string;
};

export type RankedRating = {
  display_rating: number | null;
  games: number;
  rank: number | null;
  ranked_players: number;
};

export type SportRating = RankedRating & {
  raw_rating: number;
};

export type PlayerRatings = Player & {
  gender: "male" | "female";
  overall: RankedRating;
  ratings: Record<"TT" | "BD" | "SQ" | "TN", SportRating>;
};

export type SportPrediction = {
  score_p1: number;
  score_p2: number;
  base_pred_diff?: number;
  resid_pred_diff?: number;
  pred_diff: number;
  pred_total: number;
};

export type Prediction = {
  player1: string;
  player2: string;
  player1_key?: string;
  player2_key?: string;
  player1_name?: string;
  player2_name?: string;
  sports: Record<string, SportPrediction>;
  total_p1: number;
  total_p2: number;
  total_diff: number;
  winner: string;
};
