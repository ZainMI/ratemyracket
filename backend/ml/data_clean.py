import csv
import re
from pathlib import Path

INVALID_DRAWS = ["double", "doubles", "mixed", "league", "team"]
DEFAULT_PLAYER_CORRECTIONS = (
    Path(__file__).resolve().parent / "data" / "player_corrections.csv"
)
PLAYER_CORRECTION_FIELDS = [
    "source_name",
    "source_country",
    "canonical_name",
    "canonical_country",
]
UNKNOWN_COUNTRIES = {
    "",
    "unknown",
    "unknown country",
    "unk",
    "nan",
    "none",
    "n/a",
    "na",
    "-",
    "?",
}


def normalize_name(value):
    name = re.sub(r"\s*\[.*?\]\s*", "", str(value or ""))
    return " ".join(name.split()).strip().lower()


def normalize_country(value):
    country = str(value or "").strip().lower()
    return "" if country in UNKNOWN_COUNTRIES else country


def load_player_corrections(path=DEFAULT_PLAYER_CORRECTIONS):
    """Load case-insensitive player corrections keyed by name and country."""
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return {}

    corrections = {}
    with path.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        missing = set(PLAYER_CORRECTION_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{path} is missing correction columns: "
                + ", ".join(sorted(missing))
            )

        for line_number, row in enumerate(reader, start=2):
            source_name = normalize_name(row.get("source_name"))
            source_country = normalize_country(row.get("source_country"))
            canonical_name = normalize_name(row.get("canonical_name"))
            canonical_country = normalize_country(
                row.get("canonical_country")
            )

            if not source_name and not source_country:
                continue
            if not canonical_name and not canonical_country:
                raise ValueError(
                    f"{path}:{line_number} must set a canonical name or country"
                )

            corrections[(source_name, source_country)] = (
                canonical_name,
                canonical_country,
            )

    return corrections


def correct_player(name, country, corrections):
    """Apply exact rules and safely infer missing countries by player name."""
    name = normalize_name(name)
    country = normalize_country(country)

    correction = (
        corrections.get((name, country))
        or corrections.get((name, ""))
        or corrections.get(("", country))
    )

    # When nationality is missing, use a name match only if every matching
    # correction agrees on one canonical identity. This avoids guessing for
    # genuinely different players who share a name.
    if not correction and not country and name:
        candidates = {
            (canonical_name or source_name, canonical_country)
            for (source_name, _source_country), (
                canonical_name,
                canonical_country,
            ) in corrections.items()
            if (source_name == name or canonical_name == name)
            and canonical_country
        }
        if len(candidates) == 1:
            correction = next(iter(candidates))

    if not correction:
        return name, country

    canonical_name, canonical_country = correction
    return canonical_name or name, canonical_country or country


def infer_match_gender_from_draw(draw_name):
    draw = (draw_name or "").lower()

    if (
        "women" in draw
        or "women's" in draw
        or "female" in draw
        or "girl" in draw
        or "girls" in draw
    ):
        return "female"

    return "male"


def clean_matches(
    input_csv="data/matches.csv",
    output_csv="data/matches_cleaned.csv",
    corrections_csv=DEFAULT_PLAYER_CORRECTIONS,
):
    corrections = load_player_corrections(corrections_csv)

    with open(input_csv, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        fieldnames = list(reader.fieldnames or [])
        if "match_gender" not in fieldnames:
            fieldnames.append("match_gender")

        with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            seen_matches = set()
            kept = 0
            removed = 0

            for row in reader:
                original_draw = row.get("draw") or ""
                row["match_gender"] = infer_match_gender_from_draw(
                    original_draw
                )

                draw = original_draw.lower()
                if any(bad in draw for bad in INVALID_DRAWS):
                    removed += 1
                    continue

                p1_name = row.get("team1_players") or ""
                p2_name = row.get("team2_players") or ""
                if "/" in p1_name or "/" in p2_name:
                    removed += 1
                    continue

                raw_points = (row.get("raw_points") or "").strip()
                if not raw_points:
                    removed += 1
                    continue

                match_date = (row.get("match_date") or "").strip()
                if not match_date:
                    removed += 1
                    continue

                sq_p1 = row.get("SQ_p1")
                sq_p2 = row.get("SQ_p2")
                if (
                    sq_p1 is None
                    or sq_p2 is None
                    or str(sq_p1).strip() == ""
                    or str(sq_p2).strip() == ""
                ):
                    removed += 1
                    continue

                for side in (1, 2):
                    player_field = f"team{side}_players"
                    country_field = f"team{side}_nationalities"
                    player, country = correct_player(
                        row.get(player_field),
                        row.get(country_field),
                        corrections,
                    )
                    row[player_field] = player
                    row[country_field] = country

                dedup_key = (
                    row.get("tournament_id"),
                    row.get("match_date"),
                    row.get("team1_players"),
                    row.get("team2_players"),
                )

                if dedup_key in seen_matches:
                    removed += 1
                    continue

                seen_matches.add(dedup_key)

                writer.writerow(row)
                kept += 1

    print(f"Saved cleaned file to {output_csv}")
    print(f"Applied {len(corrections)} player correction rules.")
    print(f"Kept: {kept} rows | Removed: {removed} rows")


if __name__ == "__main__":
    clean_matches()
