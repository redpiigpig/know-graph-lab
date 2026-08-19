import unittest

from scripts.ingest_lit_review import shard_for


class LiteratureReviewShardingTests(unittest.TestCase):
    def test_seven_shards_are_stable_and_mutually_exclusive(self):
        keys = [f"reference-{i}" for i in range(1000)]
        first = {key: shard_for(key, 7) for key in keys}
        second = {key: shard_for(key, 7) for key in reversed(keys)}
        self.assertEqual(first, second)
        self.assertTrue(all(0 <= shard < 7 for shard in first.values()))
        self.assertEqual(sum(list(first.values()).count(i) for i in range(7)), len(keys))
        self.assertTrue(all(list(first.values()).count(i) > 90 for i in range(7)))


if __name__ == "__main__":
    unittest.main()
