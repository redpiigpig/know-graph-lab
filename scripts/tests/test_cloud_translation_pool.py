import unittest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from scripts.lit_review_quality_reviewer import PROMPT, digest_pair, parse_review
from scripts import translation_cloud_supervisor as cloud
from scripts import translation_lane_claim as claim


class CloudTranslationPoolTests(unittest.TestCase):
    def test_seven_translators_and_dedicated_gemini_four_reviewer(self):
        pool = cloud.lanes()
        translators = [lane for lane in pool if lane["kind"] == "translate"]
        reviewers = [lane for lane in pool if lane["kind"] == "review"]
        self.assertEqual(len(pool), 8)
        self.assertEqual(len(translators), 7)
        self.assertEqual({lane["shard"] for lane in translators}, set(range(7)))
        self.assertEqual(len(reviewers), 1)
        self.assertEqual(reviewers[0]["id"], "gemini-4-reviewer")
        self.assertFalse(any(
            lane["provider"] == "gemini" and lane["slot"] == 4
            for lane in translators))

    def test_quality_review_json_and_digest(self):
        rendered = PROMPT.format(original="source", translation="譯文")
        self.assertIn('{"status":"ok"', rendered)
        self.assertEqual(parse_review('{"status":"ok","text":""}')["status"], "ok")
        revised = parse_review(
            '```json\n{"status":"revised","text":"修正版"}\n```')
        self.assertEqual(revised["text"], "修正版")
        self.assertEqual(digest_pair("a", "甲"), digest_pair("a", "甲"))
        self.assertNotEqual(digest_pair("a", "甲"), digest_pair("a", "乙"))

    def test_claim_lease_is_visible_and_expired_claim_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.json"
            rows = {
                "gemini-2": {"owner": "claude", "expires_at_epoch": time.time() + 60},
                "nvidia-1": {"owner": "claude", "expires_at_epoch": time.time() - 1},
            }
            path.write_text(json.dumps(rows), encoding="utf-8")
            with patch.object(claim, "CLAIMS_PATH", path), \
                    patch.object(cloud, "CLAIMS_PATH", path):
                self.assertEqual(set(claim.load_claims()), {"gemini-2"})
                self.assertEqual(set(cloud.active_claims()), {"gemini-2"})


if __name__ == "__main__":
    unittest.main()
