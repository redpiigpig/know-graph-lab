"""tripitaka_sanskrit 純函式測試（零 network）。

這一支的核心是**那道拒絕對齊的閘**。梵漢品數不合時若照順序硬對，
頁面看起來完全正常，內容卻整批位移一格 —— 是本專案最危險的一類錯。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tripitaka_sanskrit as ts  # noqa: E402
import tripitaka_parallels as tpp  # noqa: E402

TEI = "http://www.tei-c.org/ns/1.0"


def _tei(body: str) -> str:
    return f'<TEI xmlns="{TEI}"><text><body>{body}</body></text></TEI>'


def _write(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / f"{name}.xml"
    p.write_text(_tei(body), encoding="utf-8")
    return p


# ── GRETIL 解析 ────────────────────────────────────────────
def test_parse_chapter_verse_form(tmp_path):
    """中論式：頌號嵌在正文 `// MMK_1.1 //`，品號是它的前半。"""
    p = _write(tmp_path, "mmk",
               "<lg><l>a b c /</l><l>d e f // MMK_1.2 //</l></lg>"
               "<lg><l>g h i /</l><l>j k l // MMK_2.1 //</l></lg>")
    out = ts.parse_gretil(p, "MMK", "chapter.verse")
    assert sorted(out) == [1, 2]
    assert len(out[1]) == 2 and len(out[2]) == 2


def test_parse_chapter_marker_in_head(tmp_path):
    """章節標記常放在 <head>；只掃 l/p 會讓整部書看起來只有一品。"""
    p = _write(tmp_path, "bca",
               "<head>Pariccheda 1</head><p>first</p>"
               "<head>Pariccheda 2</head><p>second</p>")
    out = ts.parse_gretil(p, r"Pariccheda (\d+)", "regex")
    assert sorted(out) == [1, 2]


def test_parse_form_none_is_single_chapter(tmp_path):
    p = _write(tmp_path, "hr", "<p>gate gate pāragate</p>")
    assert list(ts.parse_gretil(p, "", "none")) == [1]


def test_verse_ref_extracts_only_real_numbers():
    """自編序號長得像引用式卻不是 —— 抓不到頌號就留空，不可造一個。"""
    e = {"siglum": "MMK", "form": "chapter.verse"}
    assert ts.verse_ref("... // MMK_1.1 //", e) == "MMK 1.1"
    assert ts.verse_ref("上半偈，無頌號", e) == ""
    assert ts.verse_ref("// Saddhp_3 //", {"siglum": "Saddhp", "form": "chapter"}) == ""


# ── 漢文品層 ────────────────────────────────────────────────
def test_zh_pin_segs_accepts_untyped_divs(monkeypatch):
    """CBETA 有時不給 div 的 type（道行般若只有第一品標了 pin）。
    只認 type=='pin' 會讓整部書的品層被判定為不存在。"""
    tpp._TOC_CACHE["TX"] = [
        {"i": 0, "depth": 0, "type": "xu", "head": "道行般若經序", "n": None,
         "parent": -1, "uid": "S0", "juan": 1},
        {"i": 1, "depth": 0, "type": "pin", "head": "摩訶般若波羅蜜道行品第一",
         "n": "1", "parent": -1, "uid": "S1", "juan": 1},
        {"i": 2, "depth": 0, "type": "", "head": "摩訶般若波羅蜜難問品第二",
         "n": "2", "parent": -1, "uid": "S2", "juan": 1},
    ]
    out = ts.zh_pin_segs("TX")
    assert out == {1: "S1", 2: "S2"}
    assert "S0" not in out.values()   # 序不是品


def test_zh_pin_segs_reads_number_from_head(monkeypatch):
    tpp._TOC_CACHE["TY"] = [
        {"i": 0, "depth": 0, "type": "pin", "head": "中論觀因緣品第一（十六偈）",
         "n": None, "parent": -1, "uid": "A", "juan": 1},
        {"i": 1, "depth": 0, "type": "pin", "head": "中論觀去來品第二",
         "n": None, "parent": -1, "uid": "B", "juan": 1},
    ]
    assert ts.zh_pin_segs("TY") == {1: "A", 2: "B"}


# ── 🚨 對齊閘 ───────────────────────────────────────────────
def test_gate_blocks_mismatched_chapter_counts(tmp_path, monkeypatch):
    """梵 3 品 vs 漢 5 品 → 必須擋下，不可照順序對前三品。"""
    p = _write(tmp_path, "x", "".join(
        f"<head>Ch {i}</head><p>t{i}</p>" for i in range(1, 4)))
    monkeypatch.setattr(ts, "fetch", lambda _n: p)
    tpp._TOC_CACHE["TZ"] = [
        {"i": i, "depth": 0, "type": "pin", "head": f"第{n}品", "n": str(i + 1),
         "parent": -1, "uid": f"S{i + 1}", "juan": 1}
        for i, n in enumerate("一二三四五")
    ]
    r = ts.audit_one({"file": "x", "work": "TZ", "zh": "測", "sa": "Test",
                      "siglum": r"Ch (\d+)", "form": "regex"})
    assert "🚨" in r["status"]
    assert "3" in r["detail"] and "5" in r["detail"]


def test_gate_allows_equal_chapter_counts(tmp_path, monkeypatch):
    p = _write(tmp_path, "y", "".join(
        f"<head>Ch {i}</head><p>t{i}</p>" for i in range(1, 4)))
    monkeypatch.setattr(ts, "fetch", lambda _n: p)
    tpp._TOC_CACHE["TW"] = [
        {"i": i, "depth": 0, "type": "pin", "head": f"第{n}品", "n": str(i + 1),
         "parent": -1, "uid": f"S{i + 1}", "juan": 1}
        for i, n in enumerate("一二三")
    ]
    r = ts.audit_one({"file": "y", "work": "TW", "zh": "測", "sa": "Test",
                      "siglum": r"Ch (\d+)", "form": "regex"})
    assert r["status"] == "品數相符"


def test_lotus_chapter_map_is_offset_after_devadatta():
    """法華：梵 27 品、羅什漢譯 28 品。梵 11（見寶塔）含漢 12（提婆達多），
    故漢從 12 起比梵多一。照順序對會讓 12 品以後全體位移。"""
    e = next(x for x in ts.REGISTRY if x["work"] == "T0262")
    cmap = e["chapter_map"]
    assert cmap[11] == 11
    assert cmap[12] == 13, "梵 12 應對到漢 13，不是漢 12"
    assert cmap[27] == 28
    assert len(cmap) == 27


def test_registry_entries_are_wellformed():
    for e in ts.REGISTRY:
        assert e["form"] in ("chapter", "chapter.verse", "regex", "none"), e["zh"]
        assert e["work"].startswith("T"), e["zh"]
        # chapter_map 只在梵漢品數不同時才該出現，且鍵值都要是正整數
        for k, v in (e.get("chapter_map") or {}).items():
            assert int(k) > 0 and int(v) > 0
