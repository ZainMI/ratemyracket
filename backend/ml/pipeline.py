#!/usr/bin/env python3
"""
backend/ml/pipeline.py
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from scrapers.tournament_id_scraper import (
    FIR_BASE,
    GLOBAL_BASE,
    fetch_tournament_ids,
)
from scrapers.match_scraper import fetch_matches_for_tournaments
from scrapers.jacketlon_scraper import (
    fetch_jacketlon_matches,
    fetch_jacketlon_tournaments,
    prefixed_tournament_id,
)
from data_clean import clean_matches
from features import build_training_data
from models.catboost.catboost_fin import train_full_and_package

ROLLING_LOOKBACK_DAYS = 30
ROLLING_LOOKAHEAD_DAYS = 7


def reset_state_for_tournaments(
    state_file: Path,
    tournament_ids: Iterable[str],
) -> None:
    if not state_file.exists():
        return

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        done = state.setdefault("done", {})

        removed = 0
        for tid in tournament_ids:
            if tid in done:
                done.pop(tid, None)
                removed += 1

        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print(f"Reset scraper state for {removed} recent tournaments.")

    except Exception as e:
        print(f"Warning: failed to reset scraper state: {e}")


def remove_file_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def merge_match_csvs(full_path: Path, source_path: Path) -> None:
    if not source_path.exists() or source_path.stat().st_size == 0:
        print(f"No matches found at {source_path}; skipping merge.")
        return

    source = pd.read_csv(source_path, low_memory=False)

    if source.empty:
        print(f"Match file is empty: {source_path}; skipping merge.")
        return

    if full_path.exists() and full_path.stat().st_size > 0:
        full = pd.read_csv(full_path, low_memory=False)
        merged = pd.concat([full, source], ignore_index=True)
    else:
        merged = source

    dedupe_cols = [
        "mode",
        "tournament_id",
        "match_date",
        "match_time",
        "draw",
        "draw_id",
        "round",
        "team1_players",
        "team2_players",
        "raw_points",
    ]

    dedupe_cols = [c for c in dedupe_cols if c in merged.columns]

    if dedupe_cols:
        before = len(merged)
        merged = merged.drop_duplicates(subset=dedupe_cols, keep="last")
        after = len(merged)
        print(
            f"Merged {source_path.name}: "
            f"{before} rows -> {after} after dedupe."
        )
    else:
        print("Warning: no dedupe columns found; writing without raw dedupe.")

    full_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(full_path, index=False)

    print(f"Saved full raw match history to: {full_path}")


def run_pipeline(
    lookback_days: int = ROLLING_LOOKBACK_DAYS,
    lookahead_days: int = ROLLING_LOOKAHEAD_DAYS,
    retrain: bool = True,
    full_backfill: bool = False,
) -> dict:
    print("=== Starting RacketRating ML Pipeline ===")

    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    raw_matches_csv = data_dir / "matches_raw.csv"
    scraped_matches_csv = data_dir / "matches_recent.csv"
    jacketlon_matches_csv = data_dir / "matches_jacketlon_recent.csv"
    added_data_csv = data_dir / "added_data.csv"

    cleaned_matches_csv = data_dir / "matches_cleaned.csv"
    feature_csv = data_dir / "data.csv"
    inference_state_path = data_dir / "inference_state.pkl"
    tournament_mapping_csv = data_dir / "tournament_mapping.csv"

    run_label = "full" if full_backfill else "recent"
    tournament_ids_csv = data_dir / f"tournament_ids_{run_label}.csv"
    state_file = data_dir / f"scraper_state_{run_label}.json"
    jacketlon_state_file = data_dir / f"jacketlon_state_{run_label}.json"
    jacketlon_ids_csv = data_dir / f"jacketlon_tournament_ids_{run_label}.csv"

    predictor_dir = (
        BASE_DIR / "models" / "catboost" / "artifacts" / "predictor_package"
    )

    today = datetime.date.today()

    if full_backfill:
        start_date = "2000-01-01"
        end_date = (today + datetime.timedelta(days=lookahead_days)).strftime(
            "%Y-%m-%d"
        )
        print("\nRunning FULL historical backfill.")
    else:
        start_date = (today - datetime.timedelta(days=lookback_days)).strftime(
            "%Y-%m-%d"
        )
        end_date = (today + datetime.timedelta(days=lookahead_days)).strftime(
            "%Y-%m-%d"
        )
        print("\nRunning recent update.")

    print(f"\n[1/6] Fetching tournaments from {start_date} to {end_date}...")

    tournament_sources = [
        {
            "name": "FIR",
            "base_url": FIR_BASE,
            "postal_code": "12211",
            "sport_id": None,
            "distance": None,
        },
        {
            "name": "TournamentSoftware",
            "base_url": GLOBAL_BASE,
            "postal_code": "",
            "sport_id": 12,
            "distance": 15,
        },
    ]
    ids_by_source: dict[str, int] = {}
    tournament_ids: list[str] = []
    source_errors: dict[str, str] = {}

    for source in tournament_sources:
        try:
            source_ids = fetch_tournament_ids(
                start_date=start_date,
                end_date=end_date,
                postal_code=source["postal_code"],
                verbose=False,
                mapping_csv=str(tournament_mapping_csv),
                base_url=source["base_url"],
                sport_id=source["sport_id"],
                distance=source["distance"],
            )
            ids_by_source[source["name"]] = len(source_ids)
            tournament_ids.extend(source_ids)
            print(f"  {source['name']}: {len(source_ids)} tournaments")
        except Exception as exc:
            source_errors[source["name"]] = str(exc)
            print(f"  Warning: {source['name']} discovery failed: {exc}")

    tournament_ids = sorted(set(tournament_ids))

    jacketlon_tournaments: list[dict] = []
    try:
        # Jacketlon has a small historical catalog. Always discover it so a
        # server's first ordinary daily run bootstraps the French archive;
        # its state file makes subsequent runs skip completed old events.
        jacketlon_tournaments = fetch_jacketlon_tournaments(
            start_date="2000-01-01",
            end_date=end_date,
            mapping_csv=str(tournament_mapping_csv),
        )
        ids_by_source["Jacketlon"] = len(jacketlon_tournaments)
        print(f"  Jacketlon: {len(jacketlon_tournaments)} tournaments")
    except Exception as exc:
        source_errors["Jacketlon"] = str(exc)
        print(f"  Warning: Jacketlon discovery failed: {exc}")

    if len(source_errors) == len(tournament_sources) + 1:
        raise RuntimeError(
            "Tournament discovery failed for every configured source: "
            + "; ".join(
                f"{name}: {error}" for name, error in source_errors.items()
            )
        )

    print(
        "Found "
        f"{len(tournament_ids) + len(jacketlon_tournaments)} tournaments "
        "across all sources."
    )
    print(f"Tournament mapping updated at: {tournament_mapping_csv}")

    pd.DataFrame({"tournament_id": tournament_ids}).to_csv(
        tournament_ids_csv,
        index=False,
    )
    jacketlon_ids = [
        prefixed_tournament_id(tournament["id"])
        for tournament in jacketlon_tournaments
    ]
    jacketlon_recent_ids = [
        prefixed_tournament_id(tournament["id"])
        for tournament in jacketlon_tournaments
        if start_date
        <= str(tournament.get("start_date") or "")
        <= end_date
    ]
    pd.DataFrame({"tournament_id": jacketlon_ids}).to_csv(
        jacketlon_ids_csv,
        index=False,
    )

    if not tournament_ids:
        print(
            "No tournament IDs found. Continuing with existing historical data."
        )

    print("\n[2/6] Scraping tournament matches...")

    remove_file_if_exists(scraped_matches_csv)
    remove_file_if_exists(jacketlon_matches_csv)

    if not full_backfill:
        reset_state_for_tournaments(state_file, tournament_ids)
        reset_state_for_tournaments(
            jacketlon_state_file,
            jacketlon_recent_ids,
        )

    if tournament_ids:
        fetch_matches_for_tournaments(
            tournament_ids=tournament_ids,
            out_csv=str(scraped_matches_csv),
            state_json=str(state_file),
            fresh=full_backfill,
            verbose=True,
        )
    else:
        print("Skipping match scrape because no tournament IDs were found.")

    jacketlon_result = {
        "processed_tournaments": 0,
        "matches_written": 0,
        "errors": [],
    }
    if jacketlon_tournaments:
        try:
            jacketlon_result = fetch_jacketlon_matches(
                tournaments=jacketlon_tournaments,
                out_csv=str(jacketlon_matches_csv),
                state_json=str(jacketlon_state_file),
                fresh=full_backfill,
                verbose=True,
            )
        except Exception as exc:
            source_errors["Jacketlon matches"] = str(exc)
            print(f"  Warning: Jacketlon match scrape failed: {exc}")
    else:
        print("Skipping Jacketlon match scrape: no tournaments found.")

    print("\n[3/6] Merging scraped + manually added matches...")

    merge_match_csvs(
        full_path=raw_matches_csv,
        source_path=scraped_matches_csv,
    )

    merge_match_csvs(
        full_path=raw_matches_csv,
        source_path=jacketlon_matches_csv,
    )

    merge_match_csvs(
        full_path=raw_matches_csv,
        source_path=added_data_csv,
    )

    if not raw_matches_csv.exists() or raw_matches_csv.stat().st_size == 0:
        raise RuntimeError(
            "No historical match file exists after merge. "
            "Run with --full, seed ml/data/matches_raw.csv, "
            "or add rows to ml/data/added_data.csv first."
        )

    print("\n[4/6] Cleaning and deduplicating full match history...")

    deleted_matches_csv = data_dir / "deleted_matches.csv"
    if deleted_matches_csv.exists() and deleted_matches_csv.stat().st_size > 0:
        deleted_df = pd.read_csv(deleted_matches_csv)
        if "match_id" in deleted_df.columns:
            deleted_ids = set(deleted_df["match_id"].astype(str))

            raw_df = pd.read_csv(raw_matches_csv, low_memory=False)

            def compute_hash(row):
                keys = [
                    "tournament_id",
                    "match_date",
                    "team1_players",
                    "team2_players",
                    "raw_points",
                ]
                vals = [str(row.get(k, "")) for k in keys]
                return hashlib.md5("|".join(vals).encode("utf-8")).hexdigest()

            if not raw_df.empty:
                raw_df["_match_hash"] = raw_df.apply(compute_hash, axis=1)
                before_len = len(raw_df)
                raw_df = raw_df[~raw_df["_match_hash"].isin(deleted_ids)]
                raw_df = raw_df.drop(columns=["_match_hash"])
                after_len = len(raw_df)

                if before_len != after_len:
                    print(
                        f"Filtered out {before_len - after_len} deleted matches."
                    )
                    raw_df.to_csv(raw_matches_csv, index=False)

    clean_matches(
        input_csv=str(raw_matches_csv),
        output_csv=str(cleaned_matches_csv),
    )

    print("\n[5/6] Building features and inference state...")

    build_training_data(
        in_csv=str(cleaned_matches_csv),
        out_csv=str(feature_csv),
        out_inference_state=str(inference_state_path),
    )

    metadata = None

    if retrain:
        print("\n[6/6] Retraining and packaging CatBoost predictor...")

        predictor = train_full_and_package(
            data_path=str(feature_csv),
            inference_state_path=str(inference_state_path),
            output_dir=str(predictor_dir),
        )

        metadata = getattr(predictor, "metadata", None)
    else:
        print("\n[6/6] Skipping retraining.")

    summary = {
        "status": "ok",
        "mode": "full_backfill" if full_backfill else "recent_update",
        "start_date": start_date,
        "end_date": end_date,
        "tournaments_found": len(tournament_ids) + len(jacketlon_tournaments),
        "tournaments_by_source": ids_by_source,
        "tournament_source_errors": source_errors,
        "tournament_ids_csv": str(tournament_ids_csv),
        "jacketlon_tournament_ids_csv": str(jacketlon_ids_csv),
        "tournament_mapping_csv": str(tournament_mapping_csv),
        "raw_matches_csv": str(raw_matches_csv),
        "scraped_matches_csv": str(scraped_matches_csv),
        "jacketlon_matches_csv": str(jacketlon_matches_csv),
        "jacketlon_result": jacketlon_result,
        "added_data_csv": str(added_data_csv),
        "cleaned_matches_csv": str(cleaned_matches_csv),
        "feature_csv": str(feature_csv),
        "inference_state": str(inference_state_path),
        "predictor_dir": str(predictor_dir),
        "retrained": retrain,
        "metadata": metadata,
        "note": (
            "Pipeline updated files on disk. Restart FastAPI or clear "
            "server-side caches to load the new state/model."
        ),
    }

    summary_path = data_dir / "pipeline_last_run.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )

    print("\n=== Pipeline Complete ===")
    print(f"Saved run summary to: {summary_path}")
    print("Restart FastAPI so server-side caches reload the new files.")

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full historical backfill from 2000-01-01.",
    )

    parser.add_argument(
        "--no-retrain",
        action="store_true",
        help="Skip model retraining.",
    )

    args = parser.parse_args()

    run_pipeline(
        full_backfill=args.full,
        retrain=not args.no_retrain,
    )
