#!/usr/bin/env python3
"""Scrape public French Racketlon matches from Jacketlon's JSON API.

The output deliberately matches ``match_scraper.py`` so Jacketlon data can
enter the existing cleaner, feature builder, model trainer, and R2 workflow
without a separate downstream path.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from .tournament_id_scraper import save_tournament_mapping
except ImportError:  # Direct execution with backend/ml on sys.path.
    from scrapers.tournament_id_scraper import save_tournament_mapping

API_BASE = "https://jacketlon.fr/api/v1"
SITE_BASE = "https://jacketlon.fr"
PAGE_SIZE = 256
CLASSIC_SPORTS = {"table_tennis", "badminton", "squash", "tennis"}

FIELDNAMES = [
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

# Jacketlon supplies ISO alpha-2 country codes. The existing dataset mostly
# uses TournamentSoftware/IOC-style three-letter codes, so normalize common
# Jacketlon countries before player identity construction.
COUNTRY_TO_EXISTING = {
    "AT": "aut",
    "AU": "aus",
    "BE": "bel",
    "CA": "can",
    "CH": "sui",
    "CZ": "cze",
    "DE": "ger",
    "DK": "den",
    "ES": "esp",
    "FI": "fin",
    "FR": "fra",
    "GB": "gbr",
    "HU": "hun",
    "IE": "irl",
    "IN": "ind",
    "IT": "ita",
    "NL": "ned",
    "NO": "nor",
    "PL": "pol",
    "PT": "por",
    "SE": "swe",
    "SK": "svk",
    "US": "usa",
}


def make_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "RacketRating/1.0 (+mailto:zainmagdon@gmail.com)",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return session


def get_json(
    session: requests.Session,
    path: str,
    params: dict | None = None,
) -> dict | list:
    response = session.get(
        f"{API_BASE}{path}",
        params=params,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def paginated_results(
    session: requests.Session,
    path: str,
    params: dict | None = None,
) -> list[dict]:
    page = 1
    rows: list[dict] = []
    base_params = dict(params or {})

    while True:
        payload = get_json(
            session,
            path,
            params={**base_params, "page": page, "page_size": PAGE_SIZE},
        )

        if isinstance(payload, list):
            rows.extend(payload)
            break

        page_rows = payload.get("results", [])
        if not isinstance(page_rows, list):
            break
        rows.extend(page_rows)

        if not payload.get("next") or not page_rows:
            break
        page += 1
        time.sleep(0.1)

    return rows


def prefixed_tournament_id(value) -> str:
    return f"JACKETLON:{value}"


def fetch_jacketlon_tournaments(
    start_date: str,
    end_date: str,
    mapping_csv: str | None = None,
    session: requests.Session | None = None,
) -> list[dict]:
    owns_session = session is None
    session = session or make_session()
    try:
        tournaments = paginated_results(
            session,
            "/tournaments/",
            params={
                "ordering": "start_date",
                "start_date_from": start_date,
                "start_date_to": end_date,
            },
        )
    finally:
        if owns_session:
            session.close()

    tournaments = [
        tournament
        for tournament in tournaments
        if CLASSIC_SPORTS.issubset(set(tournament.get("sports") or []))
    ]

    if mapping_csv:
        records = {
            prefixed_tournament_id(tournament["id"]): {
                "tournament_id": prefixed_tournament_id(tournament["id"]),
                "tournament_name": str(tournament.get("name") or "").strip(),
            }
            for tournament in tournaments
            if tournament.get("id") is not None
        }
        save_tournament_mapping(records, mapping_csv)

    return tournaments


def load_state(path: str, fresh: bool) -> dict:
    if fresh:
        return {"done": {}}
    state_path = Path(path)
    if not state_path.exists():
        return {"done": {}}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {"done": {}}


def save_state(state: dict, path: str) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def player_name(player: dict) -> str:
    return " ".join(
        part
        for part in [player.get("first_name"), player.get("last_name")]
        if part
    ).strip()


def player_country(player: dict) -> str:
    country = str(player.get("country") or "").strip().upper()
    return COUNTRY_TO_EXISTING.get(country, country.lower())


def player_id(player: dict) -> str:
    value = player.get("id")
    return f"jacketlon:{value}" if value is not None else ""


def score_pair(match: dict, prefix: str) -> tuple[int | None, int | None]:
    return match.get(f"{prefix}_p1"), match.get(f"{prefix}_p2")


def raw_points(match: dict) -> str:
    values = []
    for prefix in ("table_tennis", "badminton", "squash", "tennis"):
        p1, p2 = score_pair(match, prefix)
        values.append(
            f"{'' if p1 is None else p1}-{'' if p2 is None else p2}"
        )
    return "|".join(values)


def winner_side(match: dict, p1: dict, p2: dict) -> int | str:
    winner = match.get("winner") or {}
    winner_id = winner.get("id")
    if winner_id is not None and winner_id == p1.get("id"):
        return 1
    if winner_id is not None and winner_id == p2.get("id"):
        return 2
    return ""


def bracket_labels(
    session: requests.Session,
    tournament_id,
) -> dict[int, str]:
    try:
        payload = get_json(session, f"/tournaments/{tournament_id}/results/")
    except requests.RequestException:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {
        int(bracket["id"]): str(bracket.get("name") or "").strip()
        for bracket in payload.get("brackets", [])
        if bracket.get("id") is not None
    }


def match_to_row(
    match: dict,
    tournament: dict,
    brackets: dict[int, str],
) -> dict | None:
    p1 = match.get("player1")
    p2 = match.get("player2")
    sport_keys = set(match.get("sport_keys") or [])

    if (
        not match.get("played")
        or not isinstance(p1, dict)
        or not isinstance(p2, dict)
        or match.get("team1") is not None
        or match.get("team2") is not None
        or match.get("is_bye")
        or match.get("is_walkover")
        or match.get("is_tie")
        or not CLASSIC_SPORTS.issubset(sport_keys)
    ):
        return None

    tt = score_pair(match, "table_tennis")
    bd = score_pair(match, "badminton")
    sq = score_pair(match, "squash")
    tn = score_pair(match, "tennis")

    # The current cleaner requires the first three sports. Tennis may be null
    # when the overall result was already decided.
    if any(value is None for pair in (tt, bd, sq) for value in pair):
        return None

    genders = {
        str(p1.get("gender") or "").upper(),
        str(p2.get("gender") or "").upper(),
    }
    if genders == {"F"}:
        division = "Women"
    elif genders and genders.issubset({"H", "M"}):
        # Jacketlon uses French "H" (homme); some API records use "M".
        division = "Men"
    else:
        division = "Mixed"
    bracket_id = match.get("bracket")
    bracket_name = brackets.get(int(bracket_id), "") if bracket_id is not None else ""
    draw = " ".join(part for part in [division, bracket_name] if part)
    date = str(tournament.get("start_date") or "").replace("-", "")
    tid = prefixed_tournament_id(tournament.get("id"))

    return {
        "mode": "jacketlon",
        "tournament_id": tid,
        "match_date": date,
        "match_time": "",
        "draw": draw,
        "draw_id": f"jacketlon:{bracket_id}" if bracket_id is not None else "",
        "round": str(match.get("round") or ""),
        "duration": "",
        "location": str(tournament.get("city") or "").strip(),
        "team1_players": player_name(p1),
        "team2_players": player_name(p2),
        "team1_player_ids": player_id(p1),
        "team2_player_ids": player_id(p2),
        "team1_nationalities": player_country(p1),
        "team2_nationalities": player_country(p2),
        "team1_club_ids": "",
        "team2_club_ids": "",
        "winner_side": winner_side(match, p1, p2),
        "status_message": f"Jacketlon match {match.get('id', '')}".strip(),
        "TT_p1": tt[0],
        "TT_p2": tt[1],
        "BD_p1": bd[0],
        "BD_p2": bd[1],
        "SQ_p1": sq[0],
        "SQ_p2": sq[1],
        "TN_p1": tn[0],
        "TN_p2": tn[1],
        "raw_points": raw_points(match),
        "h2h_url": f"{SITE_BASE}/tournaments/{tournament.get('id')}/results",
    }


def append_rows(path: str, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output.exists() or output.stat().st_size == 0
    with output.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def fetch_jacketlon_matches(
    tournaments: list[dict],
    out_csv: str,
    state_json: str,
    fresh: bool = False,
    verbose: bool = True,
) -> dict:
    state = load_state(state_json, fresh=fresh)
    written = 0
    processed = 0
    errors: list[dict] = []

    with make_session() as session:
        for index, tournament in enumerate(tournaments, start=1):
            raw_id = tournament.get("id")
            tid = prefixed_tournament_id(raw_id)
            if state.setdefault("done", {}).get(tid):
                continue

            if verbose:
                print(
                    f"  Jacketlon [{index:03d}/{len(tournaments):03d}] "
                    f"{tournament.get('name', tid)}"
                )

            try:
                matches = paginated_results(
                    session,
                    "/matches/",
                    params={"tournament": raw_id},
                )
                brackets = bracket_labels(session, raw_id)
                rows = [
                    row
                    for match in matches
                    if (
                        row := match_to_row(match, tournament, brackets)
                    )
                    is not None
                ]
            except Exception as exc:
                errors.append({"tournament_id": tid, "error": str(exc)})
                if verbose:
                    print(f"    Warning: Jacketlon scrape failed: {exc}")
                continue
            append_rows(out_csv, rows)
            written += len(rows)
            processed += 1

            state["done"][tid] = True
            save_state(state, state_json)

            if verbose:
                print(f"    Wrote {len(rows)} usable singles matches")

    return {
        "processed_tournaments": processed,
        "matches_written": written,
        "errors": errors,
    }
