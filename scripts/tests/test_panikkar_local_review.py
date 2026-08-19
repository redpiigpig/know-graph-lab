import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import panikkar_auto as pa


class PanikkarLocalReviewTests(unittest.TestCase):
    def test_provenance_marks_existing_unknown(self):
        self.assertEqual(
            pa._provenance({"engines": ["gemini"]}, ["甲", "乙", None], 3),
            ["gemini", "unknown", None],
        )

    def test_review_replaces_only_ollama_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "demo"
            folder.mkdir()
            checkpoint = folder / "sec0.json"
            checkpoint.write_text(json.dumps({
                "src": ["one", "two", "three"],
                "zh": ["本機一", "雲端二", None],
                "engines": ["ollama", "gemini-first", None],
            }), encoding="utf-8")

            with patch.object(pa, "DATA_ROOT", root):
                count = pa.review_local_work(
                    "demo", lambda source: f"複核：{source}",
                    engine_name="gemini-first", max_total_paras=10)

            result = json.loads(checkpoint.read_text(encoding="utf-8"))
            self.assertEqual(count, 1)
            self.assertEqual(result["zh"], ["複核：one", "雲端二", None])
            self.assertEqual(
                result["engines"], ["gemini-first", "gemini-first", None])


if __name__ == "__main__":
    unittest.main()
