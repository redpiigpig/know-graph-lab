"""tripitaka_vernacular 純函式測試（零 network/LLM）。

這一支唯一會靜默出錯的地方是**段落錯位**：一次送多段省呼叫數，但模型很容易
把兩段併成一段或漏掉一段，若照順序硬分，白話欄會整批往前位移而頁面正常。
parse_reply 的記號校驗就是防這個，測試全繞著它。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tripitaka_vernacular as tv  # noqa: E402


def _seg(uid, text, kind="prose"):
    return {"uid": uid, "seg": uid, "kind": kind, "sources": {"lzh": text}}


# ── 記號校驗（命門）────────────────────────────────────────
def test_parse_reply_happy_path():
    got = tv.parse_reply("【1】第一段白話\n\n【2】第二段白話", 2)
    assert got == ["第一段白話", "第二段白話"]


def test_parse_reply_rejects_merged_segments():
    """🚨 模型把兩段併成一段 → 記號只剩一個。照順序硬分會讓
    第二段之後全部往前位移，所以必須整批退回、拆單段重譯。"""
    assert tv.parse_reply("【1】兩段被併在一起了", 2) is None


def test_parse_reply_rejects_dropped_segment():
    """漏掉中間一段（記號跳號）也必須退回。"""
    assert tv.parse_reply("【1】一\n【3】三", 3) is None
    assert tv.parse_reply("【1】一\n【2】二", 3) is None


def test_parse_reply_rejects_reordered_or_extra():
    assert tv.parse_reply("【2】二\n【1】一", 2) is None, "順序錯亂要退回"
    assert tv.parse_reply("【1】一\n【2】二\n【3】三", 2) is None, "多出一段要退回"


def test_parse_reply_rejects_empty_body():
    """記號齊全但某段是空的，也不可當成功 —— 那一段會變成空白欄。"""
    assert tv.parse_reply("【1】一\n【2】\n【3】三", 3) is None


def test_parse_reply_ignores_preamble():
    """模型偶爾會加一句前言；記號集合對就照收。"""
    got = tv.parse_reply("以下是白話翻譯：\n【1】一\n【2】二", 2)
    assert got == ["一", "二"]


# ── 分批 ──────────────────────────────────────────────────
def test_make_batches_respects_char_cap(monkeypatch):
    monkeypatch.setattr(tv, "BATCH_CHARS", 10)
    segs = [_seg("a", "1234567"), _seg("b", "1234567"), _seg("c", "12")]
    batches = tv.make_batches(segs, {})
    assert [[s["uid"] for s in b] for b in batches] == [["a"], ["b", "c"]]


def test_make_batches_skips_done_and_untranslatable():
    segs = [
        _seg("a", "已譯過"),
        _seg("b", "標題", kind="head"),      # 標題不必白話化
        _seg("c", "署名", kind="byline"),
        _seg("d", "要譯的"),
        {"uid": "e", "seg": "e", "kind": "prose", "sources": {}},   # 無漢文
    ]
    batches = tv.make_batches(segs, {"a": "已有白話"})
    assert [s["uid"] for b in batches for s in b] == ["d"]


def test_render_numbers_from_one():
    out = tv.render([_seg("a", "甲"), _seg("b", "乙")])
    assert out == "【1】甲\n\n【2】乙"


# ── 書單 ──────────────────────────────────────────────────
def test_works_are_taisho_ids_and_unique():
    assert len(tv.WORKS) == len(set(tv.WORKS))
    assert all(w.startswith("T") and w[1:].isdigit() for w in tv.WORKS)


def test_prompt_keeps_proper_nouns_and_markers():
    """提示詞必須交代兩件事：記號原樣保留、佛教專名不譯白。
    少了任一條，輸出就不可用。"""
    assert "【數字】" in tv.PROMPT or "【" in tv.PROMPT
    assert "般若波羅蜜" in tv.PROMPT      # 專名照抄的例子
    assert "繁體" in tv.PROMPT
    assert "{source}" in tv.PROMPT
