import csv
import tempfile
import unittest
from pathlib import Path

try:
    from ml.data_clean import clean_matches
    from ml.scrapers.jacketlon_scraper import FIELDNAMES, match_to_row
except ImportError:
    from data_clean import clean_matches
    from scrapers.jacketlon_scraper import FIELDNAMES, match_to_row


def sample_match():
    return {
        "id": 123,
        "player1": {
            "id": 6,
            "first_name": "Julien",
            "last_name": "CASTEL",
            "country": "FR",
            "gender": "H",
        },
        "player2": {
            "id": 848,
            "first_name": "Clément",
            "last_name": "DUVAL",
            "country": "FR",
            "gender": "H",
        },
        "winner": {"id": 848},
        "team1": None,
        "team2": None,
        "played": True,
        "is_bye": False,
        "is_walkover": False,
        "is_tie": False,
        "sport_keys": ["table_tennis", "badminton", "squash", "tennis"],
        "table_tennis_p1": 21,
        "table_tennis_p2": 11,
        "badminton_p1": 17,
        "badminton_p2": 21,
        "squash_p1": 5,
        "squash_p2": 21,
        "tennis_p1": 9,
        "tennis_p2": 12,
        "round": "5/6",
        "bracket": 12,
    }


class JacketlonScraperTests(unittest.TestCase):
    def test_match_maps_to_existing_schema(self):
        tournament = {
            "id": 41,
            "name": "Open",
            "city": "Saint-Chamond",
            "start_date": "2025-01-04",
        }
        row = match_to_row(sample_match(), tournament, {12: "SHA"})

        self.assertIsNotNone(row)
        self.assertEqual(set(row), set(FIELDNAMES))
        self.assertEqual(row["tournament_id"], "JACKETLON:41")
        self.assertEqual(row["match_date"], "20250104")
        self.assertEqual(row["team1_nationalities"], "fra")
        self.assertEqual(row["team1_player_ids"], "jacketlon:6")
        self.assertEqual(row["winner_side"], 2)
        self.assertEqual(row["draw"], "Men SHA")
        self.assertEqual(row["raw_points"], "21-11|17-21|5-21|9-12")

    def test_cross_source_duplicate_prefers_existing_row(self):
        tournament = {
            "id": 41,
            "name": "Open",
            "city": "Saint-Chamond",
            "start_date": "2025-01-04",
        }
        jacketlon = match_to_row(sample_match(), tournament, {12: "SHA"})
        existing = dict(jacketlon)
        existing.update(
            {
                "mode": "new",
                "tournament_id": "GUID-1",
                "match_date": "20250105",
                "team1_players": jacketlon["team2_players"],
                "team2_players": jacketlon["team1_players"],
                "team1_player_ids": "",
                "team2_player_ids": "",
                "team1_nationalities": "fra",
                "team2_nationalities": "fra",
                "winner_side": 1,
                "TT_p1": 11,
                "TT_p2": 21,
                "BD_p1": 21,
                "BD_p2": 17,
                "SQ_p1": 21,
                "SQ_p2": 5,
                "TN_p1": 12,
                "TN_p2": 9,
                "raw_points": "11-21|21-17|21-5|12-9",
            }
        )

        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.csv"
            cleaned = Path(tmp) / "cleaned.csv"
            corrections = Path(tmp) / "missing.csv"
            with raw.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows([jacketlon, existing])

            clean_matches(raw, cleaned, corrections)

            with cleaned.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["mode"], "new")

    def test_known_walkover_is_removed_by_cleaner(self):
        row = dict.fromkeys(FIELDNAMES, "")
        row.update(
            {
                "mode": "jacketlon",
                "tournament_id": "JACKETLON:2",
                "match_date": "20260530",
                "draw": "Men SHA",
                "team1_players": "Jonathan GILL",
                "team2_players": "Paul MUNIERE",
                "team1_nationalities": "usa",
                "team2_nationalities": "fra",
                "status_message": "Jacketlon match 199",
                "TT_p1": 16,
                "TT_p2": 21,
                "BD_p1": 7,
                "BD_p2": 21,
                "SQ_p1": 1,
                "SQ_p2": 21,
                "raw_points": "16-21|7-21|1-21|-",
            }
        )

        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.csv"
            cleaned = Path(tmp) / "cleaned.csv"
            corrections = Path(tmp) / "missing-corrections.csv"
            exclusions = Path(tmp) / "exclusions.csv"
            with raw.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerow(row)
            with exclusions.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "mode",
                        "tournament_id",
                        "match_date",
                        "team1_players",
                        "team2_players",
                        "status_message",
                        "reason",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "mode": "jacketlon",
                        "tournament_id": "JACKETLON:2",
                        "match_date": "20260530",
                        "team1_players": "Jonathan Gill",
                        "team2_players": "Paul Muniere",
                        "status_message": "Jacketlon match 199",
                        "reason": "walkover",
                    }
                )

            clean_matches(raw, cleaned, corrections, exclusions)

            with cleaned.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
