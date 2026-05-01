import csv
import re

INVALID_DRAWS = ["double", "doubles", "mixed", "league", "team"]


# clean
def clean_matches(
    input_csv="data/matches.csv",
    output_csv="data/matches_cleaned.csv",
):
    with open(input_csv, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            seen_matches = set()
            kept = 0
            removed = 0

            for row in reader:
                # 1. Filter invalid draw names
                draw = (row.get("draw") or "").lower()
                if any(bad in draw for bad in INVALID_DRAWS):
                    removed += 1
                    continue

                # 2. Filter out doubles matches by player name format
                p1_name = row.get("team1_players") or ""
                p2_name = row.get("team2_players") or ""
                if "/" in p1_name or "/" in p2_name:
                    removed += 1
                    continue

                # 3. Filter incomplete matches (no raw score text)
                raw_points = (row.get("raw_points") or "").strip()
                if not raw_points:
                    removed += 1
                    continue

                # 4. Remove rows without match_date
                match_date = (row.get("match_date") or "").strip()
                if not match_date:
                    removed += 1
                    continue

                # 5. Remove rows without squash score
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

                # 6. Normalize player names
                for field in ("team1_players", "team2_players"):
                    name = row.get(field) or ""

                    # Remove seeding like [3/4], [2], etc.
                    name = re.sub(r"\s*\[.*?\]\s*", "", name)

                    # Normalize
                    row[field] = name.strip().lower()

                # 7. Deduplicate (Crucial for recurring pipeline)
                # We use tournament_id + date + team1 + team2 to uniquely identify the match
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
    print(f"Kept: {kept} rows | Removed: {removed} rows")


if __name__ == "__main__":
    clean_matches()
