import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import mueller_auto as ma


class SbeLocalReviewTests(unittest.TestCase):
    def test_review_replaces_only_ollama_drafts(self):
        work = {"slug": "sbe-demo"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / work["slug"]
            folder.mkdir()
            checkpoint = folder / "sec0.json"
            checkpoint.write_text(json.dumps({
                "en": ["one", "two", "three"],
                "zh": ["本機一", "雲端二", None],
                "engines": ["ollama", "gemini-first", None],
            }), encoding="utf-8")

            with patch.object(ma, "DATA_ROOT", root):
                count = ma.review_local_drafts(
                    work, lambda source, _de="": f"複核：{source}",
                    engine_name="gemini-first", max_total_paras=10)

            result = json.loads(checkpoint.read_text(encoding="utf-8"))
            self.assertEqual(count, 1)
            self.assertEqual(result["zh"], ["複核：one", "雲端二", None])
            self.assertEqual(
                result["engines"], ["gemini-first", "gemini-first", None])


if __name__ == "__main__":
    unittest.main()
