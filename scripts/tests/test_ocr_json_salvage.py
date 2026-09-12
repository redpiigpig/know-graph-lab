# -*- coding: utf-8 -*-
"""Gemini 回傳的 JSON 壞掉時的搶救（ocr_with_gemini.parse_pages_json）。

🚨 分批路徑原本直接 `json.loads`，沒有單次路徑那道 json_repair 搶救，
於是長中文書只要**任何一批**吐出非法跳脫字元，整本就陣亡——
《世界宗教理念史 卷一》527 頁就是這樣卡住的（`Invalid \\escape`）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ocr_with_gemini import parse_pages_json  # noqa: E402


class TestParsePagesJson:
    def test_clean_json(self):
        assert parse_pages_json('{"pages":[{"page":1,"text":"正文"}]}') == [
            {"page": 1, "text": "正文"}]

    def test_invalid_escape_is_salvaged(self):
        # 模型偶爾吐出 \\d 這種非法跳脫；json.loads 會整份拒收
        bad = '{"pages":[{"page":1,"text":"見第\\d章"},{"page":2,"text":"下一頁"}]}'
        pages = parse_pages_json(bad)
        assert len(pages) == 2
        assert pages[1]["text"] == "下一頁"

    def test_truncated_json_keeps_whole_pages(self):
        cut = '{"pages":[{"page":1,"text":"完整"},{"page":2,"text":"被切掉一半'
        pages = parse_pages_json(cut)
        assert pages and pages[0]["text"] == "完整"

    def test_empty_input(self):
        assert parse_pages_json("") == []
        assert parse_pages_json(None) == []

    def test_unrecoverable_returns_empty(self):
        # 完全不是 JSON → 回空 list，讓呼叫端照既有邏輯判失敗，不要拋例外
        assert parse_pages_json("模型回了一段道歉的散文") == []

    def test_non_dict_payload(self):
        assert parse_pages_json('["不是物件"]') == []
