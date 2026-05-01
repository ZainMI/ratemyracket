#!/usr/bin/env python3
"""
backend/ml/pipeline.py

Self-sustaining orchestrator for RacketRating.

Pipeline:
1. Fetch tournament IDs and update tournament mapping
2. Scrape matches
3. Merge scraped matches into full historical raw matches
4. Clean + deduplicate full match history
5. Build leakage-safe features and inference state
6. Retrain and package CatBoost predictor

Important:
- This updates files on disk.
- If the FastAPI server is running with server-side caches, restart the backend
  after running this pipeline so it loads the new model/state.
"""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from scrapers.tournament_id_scraper import fetch_tournament_ids
from scrapers.match_scraper import fetch_matches_for_tournaments
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


def merge_match_csvs(full_path: Path, recent_path: Path) -> None:
    if not recent_path.exists() or recent_path.stat().st_size == 0:
        print("No scraped matches found; skipping merge.")
        return

    recent = pd.read_csv(recent_path, low_memory=False)

    if recent.empty:
        print("Scraped match file is empty; skipping merge.")
        return

    if full_path.exists() and full_path.stat().st_size > 0:
        full = pd.read_csv(full_path, low_memory=False)
        merged = pd.concat([full, recent], ignore_index=True)
    else:
        merged = recent

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
        print(f"Merged raw matches: {before} rows -> {after} after dedupe.")
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
    cleaned_matches_csv = data_dir / "matches_cleaned.csv"
    feature_csv = data_dir / "data.csv"
    inference_state_path = data_dir / "inference_state.pkl"
    tournament_mapping_csv = data_dir / "tournament_mapping.csv"

    run_label = "full" if full_backfill else "recent"
    tournament_ids_csv = data_dir / f"tournament_ids_{run_label}.csv"
    state_file = data_dir / f"scraper_state_{run_label}.json"

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

    tournament_ids = fetch_tournament_ids(
        start_date=start_date,
        end_date=end_date,
        verbose=False,
        mapping_csv=str(tournament_mapping_csv),
    )

    tournament_ids = sorted(set(tournament_ids))

    print(f"Found {len(tournament_ids)} tournaments.")
    print(f"Tournament mapping updated at: {tournament_mapping_csv}")

    pd.DataFrame({"tournament_id": tournament_ids}).to_csv(
        tournament_ids_csv,
        index=False,
    )

    if not tournament_ids:
        print(
            "No tournament IDs found. Continuing with existing historical data."
        )

    print("\n[2/6] Scraping tournament matches...")

    remove_file_if_exists(scraped_matches_csv)

    if not full_backfill:
        reset_state_for_tournaments(state_file, tournament_ids)

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

    print("\n[3/6] Merging scraped matches into full historical match file...")

    merge_match_csvs(
        full_path=raw_matches_csv,
        recent_path=scraped_matches_csv,
    )

    if not raw_matches_csv.exists() or raw_matches_csv.stat().st_size == 0:
        raise RuntimeError(
            "No historical match file exists after merge. "
            "Run with --full or seed ml/data/matches_raw.csv first."
        )

    print("\n[4/6] Cleaning and deduplicating full match history...")

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
        "tournaments_found": len(tournament_ids),
        "tournament_ids_csv": str(tournament_ids_csv),
        "tournament_mapping_csv": str(tournament_mapping_csv),
        "raw_matches_csv": str(raw_matches_csv),
        "scraped_matches_csv": str(scraped_matches_csv),
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
