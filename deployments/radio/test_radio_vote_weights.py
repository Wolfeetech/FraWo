import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from radio_vote_weights import (
    apply_weights_to_azuracast,
    build_weight_updates,
    calculate_rotation_tier,
    fetch_ratings,
)


class TestRadioVoteWeights(unittest.TestCase):

    def test_calculate_rotation_tier_stars(self):
        # 5 stars -> Power rotation (weight 1, is_queued 1)
        w, q, tier = calculate_rotation_tier(5.0)
        self.assertEqual((w, q, tier), (1, 1, "Power Rotation"))

        w, q, tier = calculate_rotation_tier(4.5)
        self.assertEqual((w, q, tier), (1, 1, "Power Rotation"))

        # 4 stars -> Elevated rotation (weight 25, is_queued 1)
        w, q, tier = calculate_rotation_tier(4.0)
        self.assertEqual((w, q, tier), (25, 1, "Elevated Rotation"))

        w, q, tier = calculate_rotation_tier(3.8)
        self.assertEqual((w, q, tier), (25, 1, "Elevated Rotation"))

        # Neutral / Middle -> Standard rotation (weight 100, is_queued 1)
        w, q, tier = calculate_rotation_tier(3.5)
        self.assertEqual((w, q, tier), (100, 1, "Standard Rotation"))

        w, q, tier = calculate_rotation_tier(None)
        self.assertEqual((w, q, tier), (100, 1, "Standard Rotation"))

        # Low rating -> Quarantined (weight 9999, is_queued 0)
        w, q, tier = calculate_rotation_tier(2.0)
        self.assertEqual((w, q, tier), (9999, 0, "Quarantined"))

        w, q, tier = calculate_rotation_tier(1.0)
        self.assertEqual((w, q, tier), (9999, 0, "Quarantined"))

    def test_calculate_rotation_tier_votes(self):
        # Likes with no ratings
        w, q, tier = calculate_rotation_tier(None, likes=3, hates=0)
        self.assertEqual((w, q, tier), (1, 1, "Power Rotation"))

        w, q, tier = calculate_rotation_tier(None, likes=1, hates=0)
        self.assertEqual((w, q, tier), (25, 1, "Elevated Rotation"))

        # Skips / Hates override positive signals
        w, q, tier = calculate_rotation_tier(5.0, hates=3)
        self.assertEqual((w, q, tier), (9999, 0, "Quarantined"))

        w, q, tier = calculate_rotation_tier(None, likes=5, hates=4)
        self.assertEqual((w, q, tier), (9999, 0, "Quarantined"))

    def test_build_weight_updates(self):
        input_rows = [
            {
                "track_id": "test_1",
                "artist": "  Artist One  ",
                "title": " Track One ",
                "stars": 5,
                "average": 4.8,
                "count": 2,
                "likes": 0,
                "hates": 0,
            },
            {
                "track_id": "test_2",
                "artist": "Artist Two",
                "title": "Track Two",
                "stars": 2,
                "average": 2.0,
                "count": 1,
                "likes": 0,
                "hates": 0,
            },
            {
                "track_id": "test_3",
                "artist": "Artist Three",
                "title": "Track Three",
                "stars": 3,
                "average": None,
                "count": 1,
                "likes": 0,
                "hates": 0,
            }
        ]

        updates = build_weight_updates(input_rows)
        self.assertEqual(len(updates), 3)

        # Row 1: 4.8 stars -> Power Rotation
        self.assertEqual(updates[0]["artist"], "Artist One")
        self.assertEqual(updates[0]["title"], "Track One")
        self.assertEqual(updates[0]["weight"], 1)
        self.assertEqual(updates[0]["is_queued"], 1)
        self.assertEqual(updates[0]["tier"], "Power Rotation")

        # Row 2: 2.0 stars -> Quarantined
        self.assertEqual(updates[1]["weight"], 9999)
        self.assertEqual(updates[1]["is_queued"], 0)
        self.assertEqual(updates[1]["tier"], "Quarantined")

        # Row 3: 3.0 stars -> Standard Rotation
        self.assertEqual(updates[2]["weight"], 100)
        self.assertEqual(updates[2]["is_queued"], 1)
        self.assertEqual(updates[2]["tier"], "Standard Rotation")

    @patch("requests.get")
    def test_fetch_ratings(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"track_id": "1", "artist": "A", "title": "B", "stars": 5}]
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        ratings = fetch_ratings("https://frawo.tech", "test_token")
        self.assertEqual(len(ratings), 1)
        self.assertEqual(ratings[0]["artist"], "A")
        mock_get.assert_called_once_with(
            "https://frawo.tech/radio/ratings/export?min_count=1",
            headers={"X-Agent-Token": "test_token"},
            timeout=20,
        )

    def test_apply_weights_empty(self):
        res = apply_weights_to_azuracast([])
        self.assertEqual(res, 0)

    @patch("subprocess.run")
    def test_apply_weights_to_azuracast(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        updates = [
            {"artist": "Artist's Name", "title": "Cool Song", "weight": 1, "is_queued": 1}
        ]
        res = apply_weights_to_azuracast(updates)
        self.assertEqual(res, 1)
        mock_run.assert_called_once()
        called_input = mock_run.call_args[1].get("input", "")
        self.assertIn("Artist\\'s Name", called_input)
        self.assertIn("spm.weight = 1", called_input)
        self.assertIn("spm.is_queued = 1", called_input)


if __name__ == "__main__":
    unittest.main()
