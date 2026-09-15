import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from radio_best_of_week import (
    calculate_chart_score,
    fetch_show_backfill_tracks,
    rank_tracks_for_charts,
    build_playlist_sync_sql,
    build_schedule_sync_sql,
)



class TestRadioBestOfWeek(unittest.TestCase):

    def test_calculate_chart_score_high_rated(self):
        # 5-star track with 2 likes and 0 hates
        row = {"stars": 5.0, "average": 5.0, "count": 2, "likes": 2, "hates": 0}
        score = calculate_chart_score(row)
        # 5.0 + (2 * 0.5) + min(2 * 0.2, 1.0) = 5.0 + 1.0 + 0.4 = 6.4
        self.assertAlmostEqual(score, 6.4, places=2)

    def test_calculate_chart_score_disliked_track(self):
        # Disliked track with hates >= 2 and hates > likes
        row = {"stars": 3.0, "average": 3.0, "count": 3, "likes": 0, "hates": 3}
        score = calculate_chart_score(row)
        self.assertEqual(score, -999.0)

    def test_calculate_chart_score_low_star_track(self):
        # Low star rating (<= 2.2)
        row = {"stars": 1.8, "average": 1.8, "count": 2, "likes": 0, "hates": 0}
        score = calculate_chart_score(row)
        self.assertEqual(score, -999.0)

    def test_rank_tracks_for_charts_ordering(self):
        rows = [
            {"artist": "Artist A", "title": "Track Low", "stars": 3.0, "count": 1, "likes": 0, "hates": 0},
            {"artist": "Artist B", "title": "Track Top", "stars": 5.0, "count": 3, "likes": 3, "hates": 0},
            {"artist": "Artist C", "title": "Track Good", "stars": 4.2, "count": 1, "likes": 1, "hates": 0},
            {"artist": "Artist D", "title": "Track Bad", "stars": 2.0, "count": 2, "likes": 0, "hates": 2},
        ]
        ranked = rank_tracks_for_charts(rows, min_score=3.5, max_tracks=10)
        # Track Bad and Track Low (< 3.5) should be excluded
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["title"], "Track Top")
        self.assertEqual(ranked[1]["title"], "Track Good")
        self.assertGreater(ranked[0]["chart_score"], ranked[1]["chart_score"])

    def test_build_playlist_sync_sql(self):
        resolved = [
            ({"artist": "Artist 1", "title": "Title 1"}, 101),
            ({"artist": "Artist 2", "title": "Title 2"}, 102),
        ]
        sql = build_playlist_sync_sql(869, resolved)
        self.assertIn("START TRANSACTION;", sql)
        self.assertIn("DELETE FROM station_playlist_media WHERE playlist_id = 869;", sql)
        self.assertIn("INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued) VALUES (869, 101, 1, 0, 1);", sql)
        self.assertIn("INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued) VALUES (869, 102, 2, 0, 1);", sql)
        self.assertIn("COMMIT;", sql)

    def test_build_schedule_sync_sql(self):
        sql = build_schedule_sync_sql(869)
        self.assertIn("START TRANSACTION;", sql)
        self.assertIn("DELETE FROM station_schedules WHERE playlist_id = 869 AND days = '7';", sql)
        self.assertIn("VALUES (869, 1800, 2000, NULL, NULL, '7', 0);", sql)
        self.assertIn("UPDATE station_schedules \nSET start_time = 2000, end_time = 2130 \nWHERE playlist_id = 863 AND days = '7';", sql)
        self.assertIn("COMMIT;", sql)

    @patch("radio_best_of_week.execute_mariadb_query")
    def test_fetch_show_backfill_tracks(self, mock_query):
        # Mock TSV returned by execute_mariadb_query
        mock_tsv = (
            "id\tartist\ttitle\tlength\tplaylist_id\tshow_name\n"
            "201\tArtist A\tTrack A1\t240\t859\t01 Sunrise\n"
            "202\tArtist B\tTrack B1\t300\t860\t02 Morning Drive\n"
            "203\tArtist C\tTrack C1\t320\t861\t03 Lunch Groove\n"
            "204\tArtist A\tTrack A2\t250\t859\t01 Sunrise\n"
        )
        mock_query.return_value = (0, mock_tsv, "")

        backfill = fetch_show_backfill_tracks(count_needed=2, exclude_media_ids={201})
        self.assertEqual(len(backfill), 2)
        # Media 201 is excluded from Show 859, so next track 204 is chosen, then 202 from Show 860
        self.assertEqual(backfill[0][1], 204)
        self.assertEqual(backfill[0][0]["artist"], "Artist A")
        self.assertEqual(backfill[1][1], 202)
        self.assertEqual(backfill[1][0]["artist"], "Artist B")
        self.assertIn("Show Highlight", backfill[0][0]["source"])


    def test_fetch_show_backfill_tracks_zero_needed(self):
        backfill = fetch_show_backfill_tracks(count_needed=0)
        self.assertEqual(backfill, [])



if __name__ == "__main__":
    unittest.main()
