import csv
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent / "backend"

ADDED_DATA_FILE = PROJECT_ROOT / "ml" / "data" / "added_data.csv"
TOURNAMENT_MAPPING_FILE = (
    PROJECT_ROOT / "ml" / "data" / "tournament_mapping.csv"
)

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

    if not file_path.exists():
        with file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
        return

    if file_path.stat().st_size > 0:
        with file_path.open("rb+") as f:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                f.write(b"\n")


def normalize_match_date(match_date):
    return float(str(match_date).replace("-", "").replace("/", ""))


def normalize_float(value):
    if value == "" or value is None:
        return ""
    return float(value)


def build_raw_points(tt_p1, tt_p2, bd_p1, bd_p2, sq_p1, sq_p2, tn_p1, tn_p2):
    return f"{tt_p1}-{tt_p2}|{bd_p1}-{bd_p2}|{sq_p1}-{sq_p2}|{tn_p1}-{tn_p2}"


def load_tournament_mapping():
    ensure_csv_exists(TOURNAMENT_MAPPING_FILE, TOURNAMENT_MAPPING_HEADERS)

    mapping = {}

    with TOURNAMENT_MAPPING_FILE.open("r", newline="", encoding="utf-8") as f:
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
    duration,
    location,
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
        "draw_id": normalize_float(draw_id),
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
        "winner_side": normalize_float(winner_side),
        "status_message": status_message,
        "TT_p1": normalize_float(tt_p1),
        "TT_p2": normalize_float(tt_p2),
        "BD_p1": normalize_float(bd_p1),
        "BD_p2": normalize_float(bd_p2),
        "SQ_p1": normalize_float(sq_p1),
        "SQ_p2": normalize_float(sq_p2),
        "TN_p1": normalize_float(tn_p1),
        "TN_p2": normalize_float(tn_p2),
        "raw_points": build_raw_points(
            tt_p1, tt_p2, bd_p1, bd_p2, sq_p1, sq_p2, tn_p1, tn_p2
        ),
        "h2h_url": h2h_url,
    }


def append_match_row(row):
    ensure_csv_exists(ADDED_DATA_FILE, HEADERS)

    with ADDED_DATA_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(row)


def add_match(**kwargs):
    row = build_match_row(**kwargs)
    append_match_row(row)
    return row
