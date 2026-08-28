"""tripitaka_tibetan 純函式測試（零 network）。

藏文那一層有兩個獨有的坑：TMX 的章尾標記會被誤判成章首，
以及不少 Toh 的 TMX 根本沒有章標記（整部書會一句都收不到）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tripitaka_tibetan as tb  # noqa: E402
import tripitaka_sanskrit as ts  # noqa: E402
import tripitaka_parallels as tpp  # noqa: E402


def _tmx(units: list[tuple[str, str]]) -> str:
    body = "".join(
        f'<tu id="U{i}"><tuv xml:lang="bo"><seg>{bo}</seg></tuv>'
        f'<tuv xml:lang="en"><seg>{en}</seg></tuv></tu>'
        for i, (bo, en) in enumerate(units))
    return f"<tmx><body>{body}</body></tmx>"


def _write(tmp_path: Path, name: str, units) -> Path:
    p = tmp_path / f"{name}.tmx"
    p.write_text(_tmx(units), encoding="utf-8")
    return p


# ── TMX 解析 ──────────────────────────────────────────────
def test_chapter_head_detected_at_segment_start(tmp_path):
    """84000 的章標題嵌在段首：`Skill in Methods Chapter 2  Then…`。"""
    p = _write(tmp_path, "t", [
        ("བོད་༡", "The Introduction Chapter 1"),
        ("བོད་༢", "some text"),
        ("བོད་༣", "Skill in Methods Chapter 2  Then the Bhagavān"),
    ])
    ch, titles = tb.parse_tmx(p)
    assert sorted(ch) == [1, 2]
    assert ch[1] == ["བོད་༡", "བོད་༢"]
    assert titles[2] == "Skill in Methods"


def test_chapter_tail_marker_is_not_a_new_chapter(tmp_path):
    """🚨「This concludes …, the second chapter of …」是**章尾**。
    當成章首會讓每一章的結尾又開一章，章數翻倍且內容錯位。"""
    p = _write(tmp_path, "t", [
        ("བོད་༡", "The Introduction Chapter 1"),
        ("བོད་༢", "{100}  This concludes “The Introduction,” the first chapter of the Dharma"),
        ("བོད་༣", "Skill in Methods Chapter 2  Then"),
    ])
    ch, _ = tb.parse_tmx(p)
    assert sorted(ch) == [1, 2]
    assert len(ch[1]) == 2, "章尾那一句仍屬第 1 章"


def test_texts_without_chapter_markers_still_collected(tmp_path):
    """🚨 不少 Toh 的 TMX 英文側沒有任何章標記（解深密、維摩詰都是）。
    若從第 0 章起算，整部書會一句都收不到而看起來「沒有藏文」。"""
    p = _write(tmp_path, "t", [("བོད་༡", "text one"), ("བོད་༢", "text two")])
    ch, titles = tb.parse_tmx(p)
    assert list(ch) == [1]
    assert len(ch[1]) == 2
    assert titles == {}


def test_empty_tibetan_segments_are_skipped(tmp_path):
    p = _write(tmp_path, "t", [("", "English-only heading"), ("བོད", "real")])
    ch, _ = tb.parse_tmx(p)
    assert ch[1] == ["བོད"]


# ── 與梵文共用同一張法華品對照表 ────────────────────────────
def test_lotus_map_is_shared_with_sanskrit_not_copied():
    """藏本章序與梵本一致。兩邊各抄一份表遲早會漂移，
    所以藏文這邊是去梵文的 REGISTRY 取，不是自己再寫一次。"""
    shared = tb._lotus_map()
    sa_map = next(e for e in ts.REGISTRY if e["work"] == "T0262")["chapter_map"]
    assert shared is sa_map or shared == sa_map
    assert shared[21] == 26 and shared[27] == 22


def test_registry_entries_are_wellformed():
    for e in tb.REGISTRY:
        assert e["toh"].startswith("toh")
        assert e["work"].startswith("T")
        for k, v in (e.get("chapter_map") or {}).items():
            assert int(k) > 0 and int(v) > 0


# ── 整部層級的落點 ─────────────────────────────────────────
def test_first_segment_falls_back_to_toc_head(monkeypatch):
    """心經、藥師這類漢本無品層的書，原文要掛在全經首段，
    不該因為「沒有品」就整個不掛。"""
    tpp._TOC_CACHE["TQ"] = [
        {"i": 0, "depth": 0, "type": "other", "head": "序", "n": None,
         "parent": -1, "uid": "HEAD", "juan": 1},
    ]
    assert tb.first_segment("TQ") == "HEAD"
