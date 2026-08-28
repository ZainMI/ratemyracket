import pickle
from pathlib import Path

import numpy as np
import pandas as pd

INFERENCE_STATE_PATH = Path("ml/data/inference_state.pkl")
MATCHES_PATH = Path("ml/data/matches_cleaned.csv")
TOURNAMENT_MAPPING_PATH = Path("ml/data/tournament_mapping.csv")

SPORTS = ["TT", "BD", "SQ", "TN"]

DISPLAY_RATING_MIN = 100
DISPLAY_RATING_MAX = 2400
MIN_GAMES_FOR_RATING_SCALE = 3

_state_cache = None
_rating_scale_cache = None
_leaderboard_cache = {}


# -----------------------------
# General helpers
# -----------------------------
def clean_country(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip().upper()


def clean_text_value(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()


def clean_gender(x) -> str:
    g = str(x).strip().lower()
    return "female" if g == "female" else "male"


def clean_score(x):
    if pd.isna(x):
        return None
    return int(float(x))


def format_match_date(x) -> str:
    if pd.isna(x):
        return ""

    s = str(x).split(".")[0].strip()

    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"

    try:
        return str(pd.to_datetime(s).date())
    except Exception:
        return s


def make_player_key(name: str, country: str) -> str:
    name = str(name).strip().lower()
    country = str(country).strip().lower()
    return f"{name}__{country}" if country and country != "nan" else name


# -----------------------------
# Inference state
# -----------------------------
def load_inference_state():
    global _state_cache

    if _state_cache is None:
        with open(INFERENCE_STATE_PATH, "rb") as f:
            _state_cache = pickle.load(f)

    return _state_cache


def get_players_dict(state: dict):
    if "player_states_by_key" in state:
        return state["player_states_by_key"]
    if "player_states_by_name" in state:
        return state["player_states_by_name"]
    return {}


def get_display_info(state: dict, player_key: str, record: dict):
    display = state.get("player_display_info", {}).get(player_key, {})

    return {
        "player_name": display.get(
            "name",
            record.get("player_name", player_key),
        ),
        "country": clean_country(
            display.get(
                "country",
                record.get("player_country", record.get("country", "")),
            )
        ),
        "gender": clean_gender(
            display.get(
                "gender",
                record.get("player_gender", record.get("gender", "male")),
            )
        ),
    }


# -----------------------------
# Display rating scale
# -----------------------------
def build_rating_scale(players: dict) -> dict:
    scale = {
        "male": {sport: [] for sport in SPORTS},
        "female": {sport: [] for sport in SPORTS},
    }

    for record in players.values():
        gender = clean_gender(
            record.get("player_gender", record.get("gender", "male"))
        )

        for sport in SPORTS:
            games = int(float(record.get(f"{sport}_games_p1", 0)))
            raw = float(record.get(f"{sport}_rating_p1", 0.0))

            if games >= MIN_GAMES_FOR_RATING_SCALE:
                scale[gender][sport].append(raw)

    for gender in ["male", "female"]:
        for sport in SPORTS:
            scale[gender][sport] = sorted(scale[gender][sport])

    return scale


def get_rating_scale(players: dict) -> dict:
    global _rating_scale_cache

    if _rating_scale_cache is None:
        _rating_scale_cache = build_rating_scale(players)

    return _rating_scale_cache


def display_rating(
    raw_rating: float,
    sport: str,
    players: dict,
    gender: str,
) -> int:
    gender = clean_gender(gender)
    vals = get_rating_scale(players).get(gender, {}).get(sport, [])

    if len(vals) < 2:
        return 1200

    raw = float(raw_rating)

    below = sum(v < raw for v in vals)
    equal = sum(v == raw for v in vals)

    percentile = (below + 0.5 * equal) / len(vals)

    rating = DISPLAY_RATING_MIN + percentile * (
        DISPLAY_RATING_MAX - DISPLAY_RATING_MIN
    )

    return int(round(rating))


# -----------------------------
# Player search / profile
# -----------------------------
def search_players(q: str, limit: int = 20):
    state = load_inference_state()
    players = get_players_dict(state)

    q = q.strip().lower()
    results = []

    for player_key, record in players.items():
        info = get_display_info(state, player_key, record)
        name = info["player_name"]
        country = info["country"]

        if q in name.lower() or q in str(player_key).lower():
            results.append(
                {
                    "player_key": player_key,
                    "player_name": name,
                    "country": country,
                    "gender": info["gender"],
                }
            )

        if len(results) >= limit:
            break

    return results


def get_player(player_key: str):
    state = load_inference_state()
    players = get_players_dict(state)

    if player_key not in players:
        raise ValueError("Player not found")

    record = players[player_key]
    info = get_display_info(state, player_key, record)

    return {
        "player_key": player_key,
        "player_name": info["player_name"],
        "country": info["country"],
        "gender": info["gender"],
    }


def get_player_ratings(player_key: str):
    state = load_inference_state()
    players = get_players_dict(state)

    if player_key not in players:
        raise ValueError("Player not found")

    record = players[player_key]
    info = get_display_info(state, player_key, record)

    ratings = {}

    for sport in SPORTS:
        raw = float(record.get(f"{sport}_rating_p1", 0.0))
        games = int(float(record.get(f"{sport}_games_p1", 0)))

        ratings[sport] = {
            "raw_rating": raw,
            "display_rating": display_rating(
                raw_rating=raw,
                sport=sport,
                players=players,
                gender=info["gender"],
            ),
            "games": games,
        }

    return {
        "player_key": player_key,
        "player_name": info["player_name"],
        "country": info["country"],
        "gender": info["gender"],
        "ratings": ratings,
    }


# -----------------------------
# Tournament mapping
# -----------------------------
def clean_tournament_name(name: str) -> str:
    if pd.isna(name) or not name:
        return ""

    name = str(name).strip()

    if "|" in name:
        name = name.split("|", 1)[0].strip()

    return name


def load_tournament_mapping() -> dict:
    if not TOURNAMENT_MAPPING_PATH.exists():
        return {}

    df = pd.read_csv(TOURNAMENT_MAPPING_PATH, low_memory=False)

    mapping = {}
    for _, row in df.iterrows():
        tid = str(row.get("tournament_id", "")).strip().upper()
        name = clean_tournament_name(row.get("tournament_name", ""))

        if tid:
            mapping[tid] = name

    return mapping


# -----------------------------
# Match history helpers
# -----------------------------
def sport_result(score, player_is_p1: bool) -> str:
    p1, p2 = score

    if p1 is None or p2 is None:
        return "unknown"

    player_score = p1 if player_is_p1 else p2
    opponent_score = p2 if player_is_p1 else p1

    if player_score > opponent_score:
        return "win"
    if player_score < opponent_score:
        return "loss"
    return "draw"


def overall_result(winner_side, player_is_p1: bool) -> str:
    try:
        winner_side = int(float(winner_side))
    except Exception:
        return "unknown"

    if winner_side == 1 and player_is_p1:
        return "win"
    if winner_side == 2 and not player_is_p1:
        return "win"
    if winner_side in [1, 2]:
        return "loss"

    return "unknown"


def total_score(scores: dict, side_index: int) -> int:
    total = 0

    for score in scores.values():
        val = score[side_index]
        if val is not None:
            total += val

    return int(total)


# -----------------------------
# Match history
# -----------------------------
def get_player_matches(
    player_key: str,
    limit: int = 50,
    opponent_player_key: str | None = None,
):
    if not MATCHES_PATH.exists():
        return []

    df = pd.read_csv(MATCHES_PATH, low_memory=False)
    tournament_mapping = load_tournament_mapping()

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    else:
        df["datetime"] = pd.to_datetime(
            df["match_date"],
            format="%Y%m%d",
            errors="coerce",
        )

    if "match_time" in df.columns:
        time_text = df["match_time"].astype(str).replace("nan", "")
        combined = (
            df["match_date"].astype(str).str.split(".").str[0] + " " + time_text
        )
        df["sort_datetime"] = pd.to_datetime(combined, errors="coerce")
        df["sort_datetime"] = df["sort_datetime"].fillna(df["datetime"])
    else:
        df["sort_datetime"] = df["datetime"]

    df = df.sort_values("sort_datetime", ascending=False)

    def row_key(row, side: int):
        return make_player_key(
            row.get(f"team{side}_players", ""),
            row.get(f"team{side}_nationalities", ""),
        )

    matches = []

    for _, row in df.iterrows():
        p1_key = row_key(row, 1)
        p2_key = row_key(row, 2)

        if player_key not in [p1_key, p2_key]:
            continue

        player_is_p1 = player_key == p1_key
        row_opponent_key = p2_key if player_is_p1 else p1_key

        if (
            opponent_player_key
            and row_opponent_key != opponent_player_key
        ):
            continue

        player_name = (
            row.get("team1_players")
            if player_is_p1
            else row.get("team2_players")
        )
        player_country = (
            row.get("team1_nationalities")
            if player_is_p1
            else row.get("team2_nationalities")
        )

        opponent_key = row_opponent_key
        opponent_name = (
            row.get("team2_players")
            if player_is_p1
            else row.get("team1_players")
        )
        opponent_country = (
            row.get("team2_nationalities")
            if player_is_p1
            else row.get("team1_nationalities")
        )

        scores = {
            "TT": [
                clean_score(row.get("TT_p1")),
                clean_score(row.get("TT_p2")),
            ],
            "BD": [
                clean_score(row.get("BD_p1")),
                clean_score(row.get("BD_p2")),
            ],
            "SQ": [
                clean_score(row.get("SQ_p1")),
                clean_score(row.get("SQ_p2")),
            ],
            "TN": [
                clean_score(row.get("TN_p1")),
                clean_score(row.get("TN_p2")),
            ],
        }

        sport_results = {
            sport: sport_result(score, player_is_p1)
            for sport, score in scores.items()
        }

        tournament_id = clean_text_value(row.get("tournament_id", "")).upper()
        tournament_name = tournament_mapping.get(tournament_id, "")
        match_result = overall_result(row.get("winner_side", ""), player_is_p1)

        p1_total = total_score(scores, 0)
        p2_total = total_score(scores, 1)

        player_total = p1_total if player_is_p1 else p2_total
        opponent_total = p2_total if player_is_p1 else p1_total

        sort_dt = row.get("sort_datetime")
        datetime_value = ""
        if not pd.isna(sort_dt):
            datetime_value = pd.to_datetime(sort_dt).isoformat()

        matches.append(
            {
                "date": format_match_date(row.get("match_date", "")),
                "match_time": clean_text_value(row.get("match_time", "")),
                "datetime": datetime_value,
                "tournament_id": tournament_id,
                "tournament_name": tournament_name,
                "draw": clean_text_value(row.get("draw", "")),
                "round": clean_text_value(row.get("round", "")),
                "player_key": player_key,
                "player_name": clean_text_value(player_name),
                "player_country": clean_country(player_country),
                "opponent_key": opponent_key,
                "opponent_name": clean_text_value(opponent_name),
                "opponent_country": clean_country(opponent_country),
                "player_is_p1": bool(player_is_p1),
                "scores": scores,
                "sport_results": sport_results,
                "winner_side": clean_text_value(row.get("winner_side", "")),
                "match_result": match_result,
                "player_total": player_total,
                "opponent_total": opponent_total,
            }
        )

        if len(matches) >= limit:
            break

    return matches


# -----------------------------
# Leaderboard
# -----------------------------
def get_leaderboard(
    sport: str = "overall",
    limit: int = 100,
    gender: str = "male",
):
    sport_key = sport.upper() if sport.lower() != "overall" else "OVERALL"

    gender_key = str(gender).strip().lower()
    if gender_key not in ["male", "female"]:
        gender_key = "male"

    cache_key = f"{sport_key}:{gender_key}"

    if cache_key in _leaderboard_cache:
        return _leaderboard_cache[cache_key][:limit]

    state = load_inference_state()
    players = get_players_dict(state)

    rows = []

    for player_key, record in players.items():
        info = get_display_info(state, player_key, record)
        player_gender = info["gender"]

        if player_gender != gender_key:
            continue

        if sport_key in SPORTS:
            raw = float(record.get(f"{sport_key}_rating_p1", 0.0))
            games = int(float(record.get(f"{sport_key}_games_p1", 0)))

            if games < MIN_GAMES_FOR_RATING_SCALE:
                continue

            rating = display_rating(
                raw_rating=raw,
                sport=sport_key,
                players=players,
                gender=player_gender,
            )

        else:
            sport_ratings = []
            total_games = 0

            for s in SPORTS:
                games_s = int(float(record.get(f"{s}_games_p1", 0)))
                raw_s = float(record.get(f"{s}_rating_p1", 0.0))

                if games_s >= MIN_GAMES_FOR_RATING_SCALE:
                    sport_ratings.append(
                        display_rating(
                            raw_rating=raw_s,
                            sport=s,
                            players=players,
                            gender=player_gender,
                        )
                    )
                    total_games += games_s

            if not sport_ratings:
                continue

            rating = int(round(sum(sport_ratings) / len(sport_ratings)))
            games = total_games

        rows.append(
            {
                "rank": 0,
                "player_key": player_key,
                "player_name": info["player_name"],
                "country": info["country"],
                "gender": player_gender,
                "rating": rating,
                "games": games,
            }
        )

    rows.sort(key=lambda x: x["rating"], reverse=True)

    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    _leaderboard_cache[cache_key] = rows

    return rows[:limit]


def clear_player_service_cache():
    global _state_cache, _rating_scale_cache, _leaderboard_cache

    _state_cache = None
    _rating_scale_cache = None
    _leaderboard_cache = {}
