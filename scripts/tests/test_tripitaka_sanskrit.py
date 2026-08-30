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


def test_zh_pin_segs_prefers_head_number_over_div_n():
    """🚨 CBETA 的 n 有時是**文件順序流水號**而非品號。

    寶性論 T1611 的偈本在卷一（品一～十一），釋論在卷二～四重出品二／五／六，
    那三個節點的 n 是 12／15／16。先讀 n 就會憑空多出品 12／15／16，
    漢品數從 11 變 14 —— 而 --audit 只會報「品數不合」，看不出是幻影品。
    """
    tpp._TOC_CACHE["TZ"] = [
        {"i": 0, "depth": 0, "type": "pin", "head": "教化品第一",
         "n": "1", "parent": -1, "uid": "P1", "juan": 1},
        {"i": 1, "depth": 0, "type": "pin", "head": "究竟一乘寶性論佛寶品第二",
         "n": "2", "parent": -1, "uid": "P2", "juan": 1},
        # 卷二重出品二，n 卻是 12
        {"i": 2, "depth": 0, "type": "pin", "head": "佛寶品第二",
         "n": "12", "parent": -1, "uid": "P2b", "juan": 2},
    ]
    out = ts.zh_pin_segs("TZ")
    assert out == {1: "P1", 2: "P2"}, "重出的品要併回原品號，不可另立新品"
    assert 12 not in out, "n=12 是流水號，不是品十二"


def test_zh_pin_segs_subdivided_pin_keeps_real_number():
    """「述求品第十二之一／之二」的 n 是「之幾」（1、2），不是品號。
    先讀 n 會讓品十二的落點掛到品一去（setdefault 撞到既有鍵而靜默失敗）。"""
    tpp._TOC_CACHE["TW"] = [
        {"i": 0, "depth": 0, "type": "pin", "head": "緣起品第一",
         "n": "1", "parent": -1, "uid": "Q1", "juan": 1},
        {"i": 1, "depth": 0, "type": "pin", "head": "大乘莊嚴經論述求品第十二之一",
         "n": "1", "parent": -1, "uid": "Q12", "juan": 5},
        {"i": 2, "depth": 0, "type": "pin", "head": "述求品第十二之二",
         "n": "2", "parent": -1, "uid": "Q12b", "juan": 6},
    ]
    out = ts.zh_pin_segs("TW")
    assert out[1] == "Q1"
    assert out[12] == "Q12", "品十二要指向「之一」，不是掉進品一或品二"


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


def test_lotus_chapter_map_has_two_divergences_not_one():
    """🚨 法華的梵漢差異有**兩處**，不是一處。第一版只處理了第一處，
    尾段四個品全配錯（陀羅尼、妙莊嚴王、普賢、囑累），而頁面看不出來。

      ① 提婆達多品（漢 12）在梵本併入見寶塔品（梵 11）→ 之後位移一格
      ② 羅什把囑累品移到第 22、陀羅尼排到第 26；梵藏本則陀羅尼在 21、
         囑累在最末 27 → 尾段七品次序完全不同
    """
    e = next(x for x in ts.REGISTRY if x["work"] == "T0262")
    cmap = e["chapter_map"]
    assert len(cmap) == 27
    assert sorted(cmap.values()) == [i for i in range(1, 29) if i != 12],         "27 個梵品應一對一蓋住漢 28 品中除提婆達多品（12）以外的全部"
    assert cmap[11] == 11                      # 見寶塔（含提婆達多）
    assert cmap[12] == 13                      # 勸持
    assert cmap[20] == 21                      # 如來神力
    assert cmap[21] == 26, "梵 21 陀羅尼 → 漢 26，不是漢 22"
    assert cmap[25] == 27, "梵 25 妙莊嚴王 → 漢 27"
    assert cmap[26] == 28, "梵 26 普賢勸發 → 漢 28"
    assert cmap[27] == 22, "梵 27 囑累 → 漢 22（羅什移到前面）"


def test_vimalakirti_map_is_two_merges_not_an_offset():
    """維摩詰梵 12 品 vs 羅什 14 品，差異是**兩處合品**不是位移 ——
    依梵本尾題判定：梵 3「遣聲聞菩薩問疾」＝漢 3 弟子＋4 菩薩、
    梵 12「結勸囑累」＝漢 13 法供養＋14 囑累。
    故漢 4 與漢 14 沒有獨立梵文可掛，那是實情不是漏做。"""
    e = next(x for x in ts.REGISTRY if x["work"] == "T0475")
    cmap = e["chapter_map"]
    assert len(cmap) == 12
    assert cmap[3] == 3 and cmap[4] == 5, "梵 4 應對到漢 5（漢 4 併在梵 3 裡）"
    assert cmap[11] == 12 and cmap[12] == 13, "梵 12 對到漢 13（漢 14 併在其中）"
    assert 4 not in cmap.values() and 14 not in cmap.values()


def test_madhyantavibhaga_map_is_one_merge_of_three():
    """辯中邊論梵 5 章 vs 玄奘 7 品。差異是**一章含三品**，不是位移。

    證據在梵本第四章自己的尾題：
      Pratipakṣabhāvanā·avasthā·phala·paricchedaścaturthaḥ
      ＝ 對治修習（漢 4）＋分位（漢 5）＋果（漢 6）
    照順序對會讓梵 5 無上乘掛到漢 5 分位品去 —— 頁面照樣正常。
    """
    e = next(x for x in ts.REGISTRY if x["work"] == "T1600")
    cmap = e["chapter_map"]
    assert len(cmap) == 5
    assert cmap[4] == 4, "梵 4 掛在該三品的第一品（漢 4 辯修對治品）"
    assert cmap[5] == 7, "梵 5 無上乘 → 漢 7 辯無上乘品，不是漢 5"
    assert 5 not in cmap.values() and 6 not in cmap.values(),         "漢 5 分位、漢 6 得果併在梵 4 裡，沒有獨立梵章可掛"


def test_ratnagotravibhaga_map_and_heading_regex():
    """寶性論梵 5 章 vs 漢 11 品。兩件事都要鎖住：

    ① 章標題拼寫不一致（「2. dvitīya pariccheda」少了尾巴的 ḥ），
       regex 若把 `paricchedaḥ` 寫死，第二、三章會**整章抓不到**、
       內容默默併進第一章，梵本只解出 3 章。
    ② 梵 1 如來藏章含漢 1–7（開頭即七金剛句＝漢 1 教化品），
       其後 bodhi／guṇa／kṛtyakriyā／anuśaṃsā 逐章對漢 8–11。
    """
    import re as _re
    e = next(x for x in ts.REGISTRY if x["work"] == "T1611")
    pat = _re.compile(e["siglum"])
    for line, want in [("1. prathamaḥ paricchedaḥ", 1),
                       ("2. dvitīya pariccheda", 2),      # 少 ḥ，一樣要抓到
                       ("3. tṛtīya pariccheda", 3),
                       ("4. caturthaḥ paricchedaḥ", 4),
                       ("5. paṃcamaḥ paricchedaḥ", 5)]:
        m = pat.search(line)
        assert m and int(m.group(1)) == want, line
    cmap = e["chapter_map"]
    assert cmap == {1: 1, 2: 8, 3: 9, 4: 10, 5: 11}
    assert sorted(cmap.values())[1] == 8, "梵 2 菩提章要跳到漢 8，不是接著漢 2"


def test_registry_entries_are_wellformed():
    for e in ts.REGISTRY:
        assert e["form"] in ("chapter", "chapter.verse", "regex", "none"), e["zh"]
        assert e["work"].startswith("T"), e["zh"]
        # chapter_map 只在梵漢品數不同時才該出現，且鍵值都要是正整數
        for k, v in (e.get("chapter_map") or {}).items():
            assert int(k) > 0 and int(v) > 0
