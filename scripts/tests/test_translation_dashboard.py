import json
import tempfile
import unittest
from pathlib import Path

from scripts.translation_dashboard import (
    ApiStatus,
    _accs_target,
    _checkpoint_counts,
    _command_arg,
    _dazangjing_catalog_counts,
    _greek_source_total,
    _greek_work_registry,
    _next_source_page,
    apply_runtime_rate_limits,
    api_inventory,
    cloud_lane_model_unavailable,
    cloud_lane_rate_limits,
    scan_json_checkpoints,
)


class TranslationDashboardTests(unittest.TestCase):
    def test_panikkar_checkpoint_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sec0.json"
            path.write_text(json.dumps({
                "heading": "## 第一章",
                "src": ["a", "b", "c"],
                "zh": ["甲", None, "丙"],
            }), encoding="utf-8")
            self.assertEqual(_checkpoint_counts(path, "src"), (2, 3, "第一章", 0))

    def test_sbe_exhausted_segment_is_not_translation_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sec0.json"
            path.write_text(json.dumps({
                "title": "第一節",
                "en": ["a", "b"],
                "zh": ["甲", None],
                "fail": [0, 3],
            }), encoding="utf-8")
            self.assertEqual(_checkpoint_counts(path, "en"), (1, 2, "第一節", 0))

    def test_accs_known_targets(self):
        self.assertEqual(
            _accs_target("gen", "accs_gen_某書創12-50.raw.jsonl", 120), 654)
        self.assertEqual(_accs_target("num", "accs_num_合卷.raw.jsonl", 40), 96)
        self.assertEqual(_accs_target("jos", "accs_jos_約書亞記.raw.jsonl", 54), 142)

    def test_checkpoint_work_requires_exact_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "demo"
            folder.mkdir()
            (folder / "sec0.json").write_text(json.dumps({
                "heading": "測試",
                "src": list(range(20)),
                "zh": ["譯文"] * 19 + [None],
            }), encoding="utf-8")
            row = scan_json_checkpoints(
                "潘尼卡", root, {"demo": "測試作品"}, [], "src")[0]
            self.assertEqual((row.done, row.total), (19, 20))
            self.assertNotEqual(row.state, "完成")

    def test_command_arg(self):
        cmd = "python scripts/ingest_lit_review.py --project genesis-philosophy --resume"
        self.assertEqual(_command_arg(cmd, "--project"), "genesis-philosophy")

    def test_dazangjing_catalog_counts_unique_classifications(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed = root / "seed.json"
            ledger = root / "classified.jsonl"
            a = {"source": "loc", "url": "a", "title": "A", "author": "", "date": ""}
            b = {"source": "dnb", "url": "b", "title": "B", "author": "", "date": ""}
            blank = {"source": "dnb", "url": "query", "title": "", "author": "", "date": ""}
            seed.write_text(
                json.dumps({"records": [a, a, b, blank]}), encoding="utf-8")
            ledger.write_text(
                "\n".join([
                    json.dumps({"record_key": "loc|a|a||", "engine": "gemini"}),
                    json.dumps({"record_key": "loc|a|a||", "engine": "gemini"}),
                    "not-json",
                    json.dumps({"record_key": "dnb|b|b||", "engine": "none"}),
                ]),
                encoding="utf-8",
            )
            self.assertEqual(_dazangjing_catalog_counts(seed, ledger), (1, 2))

    def test_next_source_page_uses_real_page_number(self):
        self.assertEqual(_next_source_page({43, 44, 96}), 97)

    def test_api_inventory_has_eight_remote_and_ollama(self):
        rows = api_inventory()
        self.assertEqual(sum(r.provider == "Gemini" for r in rows), 4)
        self.assertEqual(sum(r.provider == "NVIDIA" for r in rows), 4)
        self.assertEqual(sum(r.provider == "本機" for r in rows), 1)

    def test_generation_429_overrides_connectivity_probe(self):
        statuses = [ApiStatus("Gemini", "Gemini #1", "可連線", 20, 1, "HTTP 200")]
        actual = apply_runtime_rate_limits(statuses, {
            "gemini-1": {"state": "cooldown", "next_restart_at": 0},
        })
        self.assertEqual(actual[0].state, "429 冷卻")
        self.assertIn("實際生成回報 HTTP 429", actual[0].note)

    def test_cloud_lane_429_is_cleared_by_later_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state.json"
            logs = root / "logs"
            logs.mkdir()
            state.write_text(json.dumps({
                "project": "demo",
                "lanes": {"gemini-1": {"state": "running"}},
            }), encoding="utf-8")
            log = logs / "demo_gemini-1.log"
            log.write_text("Gemini 429 key#0\n· para 2/10\n", encoding="utf-8")
            self.assertEqual(cloud_lane_rate_limits(state, logs), {})
            log.write_text("· para 2/10\nGemini 429 key#0\n", encoding="utf-8")
            self.assertIn("gemini-1", cloud_lane_rate_limits(state, logs))

    def test_cloud_lane_model_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state.json"
            logs = root / "logs"
            logs.mkdir()
            state.write_text(json.dumps({
                "project": "demo",
                "lanes": {"nvidia-1": {"state": "cooldown"}},
            }), encoding="utf-8")
            log = logs / "demo_nvidia-1.log"
            log.write_text("HTTP 404: model unavailable\n", encoding="utf-8")
            self.assertIn(
                "nvidia-1", cloud_lane_model_unavailable(state, logs))

    def test_greek_registry_and_source_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.py"
            registry.write_text(
                "_P, _A = '柏拉圖', '亞里斯多德'\n"
                "_TABLE = [('demo', _P, 'tlg001', 1, '測試篇', 'Demo', "
                "'section', 'grc2')]\n",
                encoding="utf-8",
            )
            works = _greek_work_registry(registry)
            self.assertEqual(works[0]["title"], "測試篇")
            source = root / "tlg0059.tlg001.perseus-grc2.xml"
            source.write_text(
                '<milestone unit="section" n="1a"/>'
                '<milestone n="1b" unit="section"/>'
                '<milestone unit="page" n="2"/>',
                encoding="utf-8",
            )
            self.assertEqual(_greek_source_total(works[0], root), 2)


if __name__ == "__main__":
    unittest.main()
