import csv
import re

INVALID_DRAWS = ["double", "doubles", "mixed", "league", "team"]


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
):
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

                for field in ("team1_players", "team2_players"):
                    name = row.get(field) or ""
                    name = re.sub(r"\s*\[.*?\]\s*", "", name)
                    row[field] = name.strip().lower()

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
