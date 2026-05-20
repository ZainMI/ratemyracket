import csv
import uuid
from pathlib import Path

from app.core.config import settings

# Use settings to define paths
ADDED_DATA_FILE = settings.ml_data_dir / "added_data.csv"
TOURNAMENT_MAPPING_FILE = settings.ml_data_dir / "tournament_mapping.csv"

HEADERS = [
    "mode",
    "tournament_id",
    "match_date",
    "match_time",
    "draw",
    "draw_id",
    "round",
    "duration",
    "location",
    "team1_players",
    "team2_players",
    "team1_player_ids",
    "team2_player_ids",
    "team1_nationalities",
    "team2_nationalities",
    "team1_club_ids",
    "team2_club_ids",
    "winner_side",
    "status_message",
    "TT_p1",
    "TT_p2",
    "BD_p1",
    "BD_p2",
    "SQ_p1",
    "SQ_p2",
    "TN_p1",
    "TN_p2",
    "raw_points",
    "h2h_url",
]

TOURNAMENT_MAPPING_HEADERS = ["tournament_id", "tournament_name"]


def ensure_csv_exists(file_path, headers):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists() or file_path.stat().st_size == 0:
        with file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()


def normalize_match_date(match_date: str) -> str:
    """Converts 'YYYY-MM-DD' to 'YYYYMMDD.0' format."""
    return f"{match_date.replace('-', '').replace('/', '')}.0"


def build_raw_points(tt_p1, tt_p2, bd_p1, bd_p2, sq_p1, sq_p2, tn_p1, tn_p2):
    scores = [(tt_p1, tt_p2), (bd_p1, bd_p2), (sq_p1, sq_p2), (tn_p1, tn_p2)]
    parts = []
    for p1, p2 in scores:
        if p1 is not None or p2 is not None:
            parts.append(
                f"{p1 if p1 is not None else ''}-{p2 if p2 is not None else ''}"
            )
    return "|".join(parts)


def load_tournament_mapping():
    ensure_csv_exists(TOURNAMENT_MAPPING_FILE, TOURNAMENT_MAPPING_HEADERS)
    mapping = {}
    if (
        TOURNAMENT_MAPPING_FILE.exists()
        and TOURNAMENT_MAPPING_FILE.stat().st_size > 0
    ):
        with TOURNAMENT_MAPPING_FILE.open(
            "r", newline="", encoding="utf-8"
        ) as f:
            reader = csv.DictReader(f)
            for row in reader:
                tournament_id = row.get("tournament_id")
                tournament_name = row.get("tournament_name")
                if tournament_id and tournament_name:
                    mapping[tournament_name] = tournament_id
    return mapping


def append_tournament_mapping(tournament_name, tournament_id):
    ensure_csv_exists(TOURNAMENT_MAPPING_FILE, TOURNAMENT_MAPPING_HEADERS)
    with TOURNAMENT_MAPPING_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TOURNAMENT_MAPPING_HEADERS)
        writer.writerow(
            {
                "tournament_id": tournament_id,
                "tournament_name": tournament_name,
            }
        )


def get_or_create_tournament_id(tournament_name):
    mapping = load_tournament_mapping()
    if tournament_name in mapping:
        return mapping[tournament_name]
    tournament_id = str(uuid.uuid4()).upper()
    append_tournament_mapping(tournament_name, tournament_id)
    return tournament_id


def build_match_row(
    tournament_name,
    match_date,
    match_time,
    draw,
    draw_id,
    round_name,
    p1_first_name,
    p1_last_name,
    p1_country,
    p2_first_name,
    p2_last_name,
    p2_country,
    tt_p1,
    tt_p2,
    bd_p1,
    bd_p2,
    sq_p1,
    sq_p2,
    tn_p1,
    tn_p2,
    winner_side,
    duration="",
    location="",
    status_message="",
    h2h_url="",
    team1_player_ids="",
    team2_player_ids="",
    team1_club_ids="",
    team2_club_ids="",
):
    tournament_id = get_or_create_tournament_id(tournament_name)
    return {
        "mode": "new",
        "tournament_id": tournament_id,
        "match_date": normalize_match_date(match_date),
        "match_time": match_time,
        "draw": draw,
        "draw_id": draw_id,
        "round": round_name,
        "duration": duration,
        "location": location,
        "team1_players": f"{p1_first_name} {p1_last_name}",
        "team2_players": f"{p2_first_name} {p2_last_name}",
        "team1_player_ids": team1_player_ids,
        "team2_player_ids": team2_player_ids,
        "team1_nationalities": p1_country,
        "team2_nationalities": p2_country,
        "team1_club_ids": team1_club_ids,
        "team2_club_ids": team2_club_ids,
        "winner_side": winner_side,
        "status_message": status_message,
        "TT_p1": tt_p1,
        "TT_p2": tt_p2,
        "BD_p1": bd_p1,
        "BD_p2": bd_p2,
        "SQ_p1": sq_p1,
        "SQ_p2": sq_p2,
        "TN_p1": tn_p1,
        "TN_p2": tn_p2,
        "raw_points": build_raw_points(
            tt_p1, tt_p2, bd_p1, bd_p2, sq_p1, sq_p2, tn_p1, tn_p2
        ),
        "h2h_url": h2h_url,
    }


def append_match_row(row):
    # The csv writer will write empty strings for None values, which is what we want.
    ensure_csv_exists(ADDED_DATA_FILE, HEADERS)
    with ADDED_DATA_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(row)


def add_match(**kwargs):
    row = build_match_row(**kwargs)
    append_match_row(row)
    return row
