# -*- coding: utf-8 -*-
"""分批 OCR 的頁碼指派（ocr_with_gemini.assign_batch_pages）。

🚨 原本是 `pg["page"] = lo + off + 1` —— 照**位移**硬編號，假設模型一定回傳
剛好 60 頁。實測模型會把 60 頁的切片吐成 16 頁或 359 頁，於是整批頁碼寫歪，
而且**總頁數還是對得上**（527 頁的書報 536 頁），看起來完全正常。
《世界宗教理念史 卷一》就這樣產出 63 個重複頁碼、43 頁整段消失。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ocr_with_gemini import assign_batch_pages  # noqa: E402


def _pages(*specs):
    return [{"page": p, "text": t} for p, t in specs]


class TestAssignBatchPages:
    def test_normal_batch_maps_to_absolute_pages(self):
        got = _pages((1, "甲"), (2, "乙"), (3, "丙"))
        out, ok = assign_batch_pages(got, lo=300, want=3)
        assert [p["page"] for p in out] == [301, 302, 303]
        assert ok

    def test_model_page_field_wins_over_position(self):
        # 模型漏掉中間一頁但**自己標了頁號** → 照它的頁號對應，不要照位移擠位
        got = _pages((1, "甲"), (3, "丙"))
        out, _ = assign_batch_pages(got, lo=300, want=3)
        assert [p["page"] for p in out] == [301, 303]

    def test_position_fallback_when_page_field_missing(self):
        got = [{"text": "甲"}, {"text": "乙"}]
        out, _ = assign_batch_pages(got, lo=100, want=2)
        assert [p["page"] for p in out] == [101, 102]

    def test_out_of_range_page_field_falls_back_to_position(self):
        # 模型吐出 999（超出這一批的範圍）→ 不可信，用位移
        got = _pages((999, "甲"), (2, "乙"))
        out, _ = assign_batch_pages(got, lo=0, want=2)
        assert [p["page"] for p in out] == [1, 2]

    def test_repeated_page_number_is_dropped_not_renumbered(self):
        # 🚨 模型重吐同一頁時，重編號會把它塞到別頁去（p181 出現兩份不同內容）
        got = _pages((1, "甲"), (1, "甲又一次"), (2, "乙"))
        out, _ = assign_batch_pages(got, lo=180, want=2)
        assert [p["page"] for p in out] == [181, 182]
        assert out[0]["text"] == "甲"

    def test_batch_returning_far_too_few_pages_is_not_ok(self):
        # 60 頁的切片只回 16 頁 → 有 43 頁沒拿到，這一批不可接受
        got = _pages(*[(i + 1, f"p{i}") for i in range(16)])
        _, ok = assign_batch_pages(got, lo=180, want=60)
        assert not ok

    def test_batch_returning_far_too_many_pages_is_not_ok(self):
        got = _pages(*[(1, "同一頁") for _ in range(359)])
        _, ok = assign_batch_pages(got, lo=300, want=60)
        assert not ok

    def test_a_few_blank_pages_omitted_is_still_ok(self):
        # 模型略過幾張空白頁是正常的，不該整批退掉
        got = _pages(*[(i + 1, f"p{i}") for i in range(57)])
        _, ok = assign_batch_pages(got, lo=0, want=60)
        assert ok

    def test_empty_batch(self):
        out, ok = assign_batch_pages([], lo=0, want=60)
        assert out == [] and not ok

    def test_non_dict_entries_are_skipped(self):
        got = [{"page": 1, "text": "甲"}, "垃圾", {"page": 2, "text": "乙"}]
        out, _ = assign_batch_pages(got, lo=0, want=2)
        assert [p["page"] for p in out] == [1, 2]
