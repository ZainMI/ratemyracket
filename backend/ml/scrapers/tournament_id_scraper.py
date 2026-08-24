#!/usr/bin/env python3
"""
backend/ml/scrapers/get_tournament_ids.py

Scrapes FIR tournament IDs from Tournament Software.

Also writes/appends a tournament mapping file:
  tournament_id,tournament_name

Can be used two ways:

1. CLI:
   python get_tournament_ids.py --start 2025-01-01 --end 2025-12-31

2. Python import:
   from get_tournament_ids import fetch_tournament_ids
   ids = fetch_tournament_ids("2025-01-01", "2025-12-31")
"""

import argparse
import csv
import re
import time
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

FIR_BASE = "https://fir.tournamentsoftware.com"
GLOBAL_BASE = "https://www.tournamentsoftware.com"
BASE = FIR_BASE
FIND_URL = f"{BASE}/find"
DOSEARCH_URL = f"{BASE}/find/tournament/DoSearch"

DEFAULT_OUTPUT_CSV = "data/tournament_ids.csv"
DEFAULT_MAPPING_CSV = "data/tournament_mapping.csv"

DEFAULT_POSTAL_CODE = "12211"
DEFAULT_MAX_PAGES = 300
DEFAULT_SLEEP_SECONDS = 0.4
DEFAULT_EMPTY_PAGE_PATIENCE = 3

GUID_ONLY_RE = re.compile(
    r"\b([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\b"
)

HEADERS_GET = {
    "User-Agent": "RacketlonScraper/1.0 (+mailto:zainmagdon@gmail.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

HEADERS_POST = {
    "User-Agent": "RacketlonScraper/1.0 (+mailto:zainmagdon@gmail.com)",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE,
    "Referer": FIND_URL,
}


def clean_text(x: str) -> str:
    return " ".join(str(x or "").split()).strip()


def build_filters(
    start_date: str,
    end_date: str,
    postal_code: str = DEFAULT_POSTAL_CODE,
    sport_id: str | int | None = None,
    distance: str | int | None = None,
) -> dict:
    filters = {
        "StartDate": start_date,
        "EndDate": end_date,
        "DateFilterType": "0",
        "PostalCode": postal_code,
    }
    if sport_id is not None:
        filters["SportID"] = str(sport_id)
    if distance is not None:
        filters["Distance"] = str(distance)
    return filters


def make_session() -> requests.Session:
    session = requests.Session()

    retries = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def set_basic_cookie_consent(session: requests.Session, base_url: str) -> None:
    """Avoid TournamentSoftware's cookie wall using basic cookies only."""
    hostname = urlparse(base_url).hostname
    if hostname:
        session.cookies.set(
            "st",
            "l=1033&c=1&cp=1",
            domain=hostname,
            path="/",
        )


def extract_form_fields(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    data = {}

    for inp in soup.select("input[name]"):
        name = inp.get("name")
        if name:
            data[name] = inp.get("value", "")

    return data


def guess_tournament_name(tag) -> str:
    """
    Best-effort name extraction from a tournament result item.
    Works with mixed TournamentSoftware markup.
    """
    candidates = []

    # nearby text from link itself
    text = clean_text(tag.get_text(" ", strip=True))
    if text:
        candidates.append(text)

    # parent/list item/card text
    for parent in [
        tag.parent,
        tag.find_parent("li"),
        tag.find_parent("tr"),
        tag.find_parent("div"),
    ]:
        if parent:
            ptext = clean_text(parent.get_text(" ", strip=True))
            if ptext:
                candidates.append(ptext)

    for c in candidates:
        # Avoid using pure GUID-ish or empty strings
        if not GUID_ONLY_RE.fullmatch(c) and len(c) > 3:
            return c

    return ""


def extract_tournament_records_from_fragment(
    html_fragment: str,
) -> dict[str, dict]:
    """
    Returns:
        {
          GUID: {
            "tournament_id": GUID,
            "tournament_name": name,
          }
        }
    """
    soup = BeautifulSoup(html_fragment, "lxml")
    records: dict[str, dict] = {}

    def add_record(guid: str, name: str = ""):
        guid = guid.upper()
        name = clean_text(name)

        if guid not in records:
            records[guid] = {
                "tournament_id": guid,
                "tournament_name": name,
            }
        elif name and not records[guid].get("tournament_name"):
            records[guid]["tournament_name"] = name

    # Links are the best source because the visible text often contains name
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if "tournament" not in href.lower():
            continue

        name = guess_tournament_name(a)

        for match in GUID_ONLY_RE.finditer(href):
            add_record(match.group(1), name)

    # onclick handlers
    for tag in soup.select("[onclick]"):
        onclick = tag.get("onclick", "")
        if "tournament" not in onclick.lower():
            continue

        name = guess_tournament_name(tag)

        for match in GUID_ONLY_RE.finditer(onclick):
            add_record(match.group(1), name)

    # data-* attributes
    for tag in soup.find_all(True):
        for key, value in (tag.attrs or {}).items():
            if not isinstance(key, str):
                continue
            if not key.lower().startswith("data-"):
                continue

            if isinstance(value, list):
                value_text = " ".join(str(v) for v in value)
            else:
                value_text = str(value)

            if "tournament" not in value_text.lower():
                continue

            name = guess_tournament_name(tag)

            for match in GUID_ONLY_RE.finditer(value_text):
                add_record(match.group(1), name)

    # fallback around "tournament"
    for match in re.finditer(
        r"tournament.{0,160}",
        html_fragment,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        chunk = match.group(0)
        for guid_match in GUID_ONLY_RE.finditer(chunk):
            add_record(guid_match.group(1), "")

    return records


def extract_tournament_guids_from_fragment(html_fragment: str) -> set[str]:
    """
    Backward-compatible helper.
    """
    return set(extract_tournament_records_from_fragment(html_fragment).keys())


def build_payload(base_form: dict, page: int, filters: dict) -> dict:
    payload = dict(base_form)
    payload["Page"] = str(page)

    payload["TournamentFilter.DateFilterType"] = filters["DateFilterType"]
    payload["TournamentFilter.StartDate"] = filters["StartDate"]
    payload["TournamentFilter.EndDate"] = filters["EndDate"]
    payload["TournamentFilter.PostalCode"] = filters["PostalCode"]

    payload["StartDate"] = filters["StartDate"]
    payload["EndDate"] = filters["EndDate"]
    payload["PostalCode"] = filters["PostalCode"]

    if "SportID" in filters:
        payload["TournamentExtendedFilter.SportID"] = filters["SportID"]
        payload["SportID"] = filters["SportID"]
    if "Distance" in filters:
        payload["TournamentFilter.Distance"] = filters["Distance"]
        payload["Distance"] = filters["Distance"]

    payload.setdefault("TournamentFilter_Q", "")
    payload.setdefault("TournamentFilter.Q", "")

    return payload


def save_tournament_mapping(records: dict[str, dict], mapping_csv: str) -> None:
    """
    Appends/updates tournament_id -> tournament_name mapping.
    Existing names are preserved unless the new record has a name
    and the old one is blank.
    """
    path = Path(mapping_csv)
    path.parent.mkdir(parents=True, exist_ok=True)

    merged: dict[str, dict] = {}

    if path.exists() and path.stat().st_size > 0:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = clean_text(row.get("tournament_id", "")).upper()
                if not tid:
                    continue
                merged[tid] = {
                    "tournament_id": tid,
                    "tournament_name": clean_text(
                        row.get("tournament_name", "")
                    ),
                }

    for tid, rec in records.items():
        tid = tid.upper()
        new_name = clean_text(rec.get("tournament_name", ""))

        if tid not in merged:
            merged[tid] = {
                "tournament_id": tid,
                "tournament_name": new_name,
            }
        elif new_name and not merged[tid].get("tournament_name"):
            merged[tid]["tournament_name"] = new_name

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["tournament_id", "tournament_name"],
        )
        writer.writeheader()
        for tid in sorted(merged):
            writer.writerow(merged[tid])

    print(f"Saved tournament mapping with {len(merged)} rows to {path}")


def fetch_tournament_records(
    start_date: str,
    end_date: str,
    postal_code: str = DEFAULT_POSTAL_CODE,
    max_pages: int = DEFAULT_MAX_PAGES,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
    empty_page_patience: int = DEFAULT_EMPTY_PAGE_PATIENCE,
    verbose: bool = True,
    mapping_csv: str | None = DEFAULT_MAPPING_CSV,
    base_url: str = BASE,
    sport_id: str | int | None = None,
    distance: str | int | None = None,
) -> dict[str, dict]:
    """
    Fetch tournament records for a date range.

    Returns:
        {
          GUID: {
            "tournament_id": GUID,
            "tournament_name": name,
          }
        }
    """
    filters = build_filters(
        start_date,
        end_date,
        postal_code,
        sport_id=sport_id,
        distance=distance,
    )

    base_url = base_url.rstrip("/")
    find_url = f"{base_url}/find"
    dosearch_url = f"{base_url}/find/tournament/DoSearch"

    session = make_session()
    set_basic_cookie_consent(session, base_url)

    if verbose:
        print(f"GET {find_url} start={start_date} end={end_date}")

    session.headers.clear()
    session.headers.update(HEADERS_GET)

    response = session.get(
        find_url,
        params={**filters, "page": 1},
        timeout=30,
    )
    response.raise_for_status()

    base_form = extract_form_fields(response.text)

    if verbose:
        print(f"Extracted {len(base_form)} form fields from /find")

    session.headers.clear()
    session.headers.update(
        {
            **HEADERS_POST,
            "Origin": base_url,
            "Referer": find_url,
        }
    )

    records: dict[str, dict] = {}
    empty_pages = 0

    for page in range(1, max_pages + 1):
        payload = build_payload(base_form, page, filters)

        response = session.post(
            dosearch_url,
            data=payload,
            timeout=30,
        )
        response.raise_for_status()

        fragment = response.text
        page_records = extract_tournament_records_from_fragment(fragment)

        new_ids = sorted(tid for tid in page_records if tid not in records)

        for tid, rec in page_records.items():
            if tid not in records:
                records[tid] = rec
            elif rec.get("tournament_name") and not records[tid].get(
                "tournament_name"
            ):
                records[tid]["tournament_name"] = rec["tournament_name"]

        if new_ids:
            empty_pages = 0
        else:
            empty_pages += 1

        if verbose:
            print(
                f"page {page:03d}: +{len(new_ids)} "
                f"(total {len(records)}) "
                f"empty_streak={empty_pages} "
                f"len={len(fragment)}"
            )

        if empty_pages >= empty_page_patience:
            if verbose:
                print("Stopping after consecutive empty pages.")
            break

        time.sleep(sleep_seconds)

    if mapping_csv:
        save_tournament_mapping(records, mapping_csv)

    return dict(sorted(records.items()))


def fetch_tournament_ids(
    start_date: str,
    end_date: str,
    postal_code: str = DEFAULT_POSTAL_CODE,
    max_pages: int = DEFAULT_MAX_PAGES,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
    empty_page_patience: int = DEFAULT_EMPTY_PAGE_PATIENCE,
    verbose: bool = True,
    mapping_csv: str | None = DEFAULT_MAPPING_CSV,
    base_url: str = BASE,
    sport_id: str | int | None = None,
    distance: str | int | None = None,
) -> list[str]:
    """
    Backward-compatible function.

    Returns:
        Sorted list of uppercase tournament GUID strings.

    Also writes/appends tournament mapping CSV by default.
    """
    records = fetch_tournament_records(
        start_date=start_date,
        end_date=end_date,
        postal_code=postal_code,
        max_pages=max_pages,
        sleep_seconds=sleep_seconds,
        empty_page_patience=empty_page_patience,
        verbose=verbose,
        mapping_csv=mapping_csv,
        base_url=base_url,
        sport_id=sport_id,
        distance=distance,
    )

    return sorted(records.keys())


def save_tournament_ids(ids: Iterable[str], output_csv: str) -> None:
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    unique_ids = sorted(set(ids))

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tournament_id"])
        for tournament_id in unique_ids:
            writer.writerow([tournament_id])

    print(f"Saved {len(unique_ids)} tournament IDs to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape FIR tournament IDs from Tournament Software."
    )

    parser.add_argument(
        "--start", required=True, help="Start date in YYYY-MM-DD format."
    )
    parser.add_argument(
        "--end", required=True, help="End date in YYYY-MM-DD format."
    )
    parser.add_argument(
        "--postal", default=DEFAULT_POSTAL_CODE, help="Postal code filter."
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT_CSV, help="Output CSV path."
    )
    parser.add_argument(
        "--mapping-output",
        default=DEFAULT_MAPPING_CSV,
        help="Tournament ID to name mapping CSV path.",
    )
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument(
        "--empty-page-patience", type=int, default=DEFAULT_EMPTY_PAGE_PATIENCE
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ids = fetch_tournament_ids(
        start_date=args.start,
        end_date=args.end,
        postal_code=args.postal,
        max_pages=args.max_pages,
        sleep_seconds=args.sleep,
        empty_page_patience=args.empty_page_patience,
        verbose=True,
        mapping_csv=args.mapping_output,
    )

    save_tournament_ids(ids, args.output)


if __name__ == "__main__":
    main()
