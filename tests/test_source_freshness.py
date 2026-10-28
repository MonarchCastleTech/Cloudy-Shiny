import csv
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from sentiment_tracker import FIELDNAMES, HEALTH_FIELDNAMES, load_recent_live_rows


class SourceFreshnessTests(unittest.TestCase):
    def test_only_recent_matched_live_rows_are_eligible(self):
        now = dt.datetime(2026, 10, 28, 12, tzinfo=dt.timezone.utc)
        old = (now - dt.timedelta(hours=73)).isoformat()
        live = (now - dt.timedelta(hours=3)).isoformat()
        fallback = (now - dt.timedelta(hours=1)).isoformat()
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "data.csv"
            health = Path(directory) / "health.csv"
            with data.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
                writer.writeheader()
                for stamp in (old, live, fallback):
                    writer.writerow({"timestamp": stamp, "stock_fear_greed": "42", "crypto_fear_greed": "51", "vix_normalized": "30"})
            with health.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=HEALTH_FIELDNAMES)
                writer.writeheader()
                writer.writerow({"timestamp": old, "cnn_status": "live", "crypto_status": "live", "vix_status": "live"})
                writer.writerow({"timestamp": live, "cnn_status": "live", "crypto_status": "fallback", "vix_status": "live"})
                writer.writerow({"timestamp": fallback, "cnn_status": "fallback", "crypto_status": "fallback", "vix_status": "fallback"})
            result = load_recent_live_rows(data, health, now)
        self.assertEqual(set(result), {"stock", "vix"})
        self.assertEqual(result["stock"]["timestamp"], live)
        self.assertEqual(result["vix"]["timestamp"], live)

    def test_missing_health_history_never_certifies_a_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_recent_live_rows(Path(directory) / "data", Path(directory) / "health", dt.datetime.now(dt.timezone.utc)), {})
