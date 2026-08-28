"""tripitaka_cbeta 純解析函式測試（零 network/DB）。

鎖住三件最容易靜默壞掉的事：
  1. 段的鍵必須是大正藏行號，不是自編流水號（使用者定調）
  2. 偈頌的換行不可被壓成一整段散文
  3. equiv-notes 在 cb: 命名空間下，用 {TEI}div 找會靜默回 0 筆
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tripitaka_cbeta as tc  # noqa: E402

TEI = "http://www.tei-c.org/ns/1.0"
CB = "http://www.cbeta.org/ns/1.0"

# 最小樣本：仿 T30n1564《中論》—— 序 + 一品（偈頌 + 長行）+ 巴利對應註 + 缺字 + 異文
SAMPLE = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xmlns:cb="{CB}" xml:id="T30n1564">
 <teiHeader><fileDesc>
  <titleStmt>
    <title level="s" xml:lang="zh-Hant">大正新脩大藏經</title>
    <title level="m" xml:lang="zh-Hant">中論</title>
    <author>龍樹菩薩造 梵志青目釋 姚秦 鳩摩羅什譯</author>
  </titleStmt>
  <extent>4卷</extent>
  <publicationStmt><idno type="CBETA">
    <idno type="canon">T</idno>.<idno type="vol">30</idno>.<idno type="no">1564</idno>
  </idno></publicationStmt>
 </fileDesc></teiHeader>
 <text><body>
  <milestone unit="juan" n="1"/>
  <pb n="0001a" ed="T"/><lb n="0001a05" ed="T"/>
  <cb:div type="xu"><head>釋僧叡序</head>
    <lb n="0001a07" ed="T"/><p>《中論》有五百偈<note place="foot" n="0001001">校勘一</note>，
      龍樹菩薩之所造也<note place="inline">夾註要留</note>。</p>
  </cb:div>
  <cb:div type="pin"><cb:mulu level="1" n="1" type="品">觀因緣品第一</cb:mulu>
    <lb n="0001b10" ed="T"/><head>觀因緣品第一</head>
    <lb n="0001b15" ed="T"/>
    <lg type="regular"><l>不生亦不滅，</l><l>不常亦不斷，</l></lg>
    <lb n="0002a01" ed="T"/><p>問曰：何故造此<g ref="#CB00001"/>？
      <app><lem>答</lem><rdg wit="【宋】">荅</rdg></app>曰：有人言萬物從大自在天生。</p>
  </cb:div>
  <milestone unit="juan" n="2"/>
  <lb n="0010a01" ed="T"/><p>卷二第一段。</p>
  <cb:div type="apparatus"><p>不該出現在正文的校勘表</p></cb:div>
  <cb:div type="equiv-notes"><head>相對應巴利文書名</head>
    <p><note n="0001001" type="equivalent" place="foot">S. 22. 12-14. Anicca, etc.</note></p>
  </cb:div>
 </body></text>
</TEI>"""

GAIJI = {"CB00001": {"uni_char": "論", "composition": "[言+侖]"}}


def _parse(monkeypatch=None):
    tc._GAIJI = GAIJI
    return tc.parse_work(SAMPLE)


# ── 目錄欄位 ──────────────────────────────────────────────
def test_meta_ids_and_division():
    meta, _, _ = _parse()
    assert meta["id"] == "T1564"
    assert meta["canon"] == "T" and meta["vol"] == 30 and meta["work_no"] == 1564
    assert meta["title_zh"] == "中論"
    assert meta["juan_count"] == 4
    assert meta["division_key"] == "zhongguan"   # 1564 落在中觀部
    assert meta["japanese"] is False


def test_byline_composite_dynasty_in_middle():
    """'龍樹菩薩造 梵志青目釋 姚秦 鳩摩羅什譯' —— 朝代夾在中間，
    只看開頭會抓不到，這是最早踩到的 bug。"""
    b = tc.parse_byline("龍樹菩薩造 梵志青目釋 姚秦 鳩摩羅什譯")
    assert b["dynasty"] == "姚秦"
    assert b["translator"] == "鳩摩羅什"
    assert b["author"] == "龍樹菩薩"


def test_byline_variants():
    assert tc.parse_byline("劉宋 求那跋陀羅譯")["translator"] == "求那跋陀羅"
    assert tc.parse_byline("世親菩薩造 唐 玄奘譯")["dynasty"] == "唐"
    co = tc.parse_byline("後秦 佛陀耶舍共竺佛念譯")
    assert co["roles"][0]["names"] == ["佛陀耶舍", "竺佛念"]
    lost = tc.parse_byline("失譯人名今附秦錄")
    assert lost["lost_translator"] is True
    assert lost["dynasty"] == ""        # 「失譯」不是朝代


def test_division_boundaries_cover_taisho():
    """部門區間不得重疊、不得留空隙（漏一段會讓整批經悄悄變 other）。"""
    prev_hi = 0
    for _key, _label, lo, hi in tc.TAISHO_DIVISIONS:
        assert lo == prev_hi + 1, f"{_label} 起點 {lo} 與前一部尾 {prev_hi} 不連續"
        assert hi >= lo
        prev_hi = hi
    assert tc.division_of("T", 262) == "fahua"
    assert tc.division_of("T", 99) == "agama"
    assert tc.division_of("T", 2145) == "mulu"
    assert tc.is_japanese_compilation("T", 2300) is True
    assert tc.is_japanese_compilation("T", 2184) is False


def test_nanchuan_division_keyed_by_volume_not_work_no():
    """南傳的經號是冊內序號（N01n0001 與 N02n0001 是兩部書），
    拿經號分部會把整套書分錯 —— 這是第一版真的踩到的錯。"""
    assert tc.division_of("N", 1, vol=1) == "n-vinaya"
    assert tc.division_of("N", 1, vol=9) == "n-majjhima"    # 同一經號、不同冊
    assert tc.division_of("N", 1, vol=45) == "n-khuddaka"   # 大義釋屬小部，非論藏
    assert tc.division_of("N", 1, vol=48) == "n-abhidhamma"
    assert tc.division_of("N", 1, vol=67) == "n-outside"    # 清淨道論屬藏外
    prev = 0
    for _k, _l, lo, hi in tc.NANCHUAN_DIVISIONS:
        assert lo == prev + 1
        prev = hi
    assert prev == 70                                        # 元亨寺版共 70 冊


def test_work_id_scheme():
    """T 用通行的經號式；N 必須帶冊號才唯一。"""
    meta, _, _ = _parse()
    assert meta["id"] == "T1564"


# ── 切段 ──────────────────────────────────────────────────
def test_segment_key_is_taisho_line_number():
    """使用者定調：段鍵＝大正藏行號，不自編流水號。"""
    _, segs, _ = _parse()
    keys = [s["seg"] for s in segs]
    assert "T30n1564_p0001a07" in keys
    assert all(k.startswith("T30n1564_p") for k in keys), keys
    # seg 本身即通行引用式，不另存 cite 欄（同值重複 95 萬次沒有意義）
    assert all("cite" not in s for s in segs)


def test_verse_keeps_line_breaks():
    """偈頌若被壓成一段散文，梵藏漢的頌號就對不上了。"""
    _, segs, _ = _parse()
    v = next(s for s in segs if s["kind"] == "verse")
    assert v["sources"]["lzh"] == "不生亦不滅，\n不常亦不斷，"


def test_juan_tracked_across_milestones():
    _, segs, _ = _parse()
    assert next(s for s in segs if "卷二第一段" in s["sources"]["lzh"])["juan"] == 2
    assert next(s for s in segs if s["seg"] == "T30n1564_p0001a07")["juan"] == 1


def test_apparatus_div_excluded_from_body():
    _, segs, _ = _parse()
    assert not any("校勘表" in s["sources"]["lzh"] for s in segs)


def test_inline_note_kept_footnote_stripped():
    _, segs, _ = _parse()
    s = next(s for s in segs if s["seg"] == "T30n1564_p0001a07")
    assert "（夾註要留）" in s["sources"]["lzh"]     # 原書雙行小字夾註屬正文
    assert "校勘一" not in s["sources"]["lzh"]       # 腳註不入正文
    assert any(n["text"] == "校勘一" for n in s["notes"])


def test_gaiji_and_variant_reading():
    _, segs, _ = _parse()
    p = next(s for s in segs if "問曰" in s["sources"]["lzh"])
    assert "造此論？" in p["sources"]["lzh"]          # 缺字還原成正字
    assert "答曰" in p["sources"]["lzh"]              # <app> 取 lem
    assert "荅" not in p["sources"]["lzh"]            # 丟 rdg 異讀


def test_gaiji_falls_back_to_composition():
    assert tc.resolve_gaiji("CB00001", GAIJI) == "論"
    assert tc.resolve_gaiji("CB99999", {"CB99999": {"composition": "[言+侖]"}}) == "[言+侖]"
    assert tc.resolve_gaiji("CB404", {}) == "[CB404]"


# ── 巴利對應 ──────────────────────────────────────────────
def test_equiv_notes_found_in_cb_namespace():
    """<cb:div> 不是 <tei:div>；用 {TEI}div 找會靜默回 0 筆而不報錯。"""
    _, _, eq = _parse()
    assert len(eq) == 1
    assert eq[0]["n"] == "0001001"
    assert eq[0]["ref"].startswith("S. 22. 12-14.")


def test_toc_tree_and_segment_index():
    """段不存整串路徑，只存目錄索引；目錄樹要能還原麵包屑。"""
    meta, segs, _ = _parse()
    toc = meta["toc"]
    v = next(s for s in segs if s["kind"] == "verse")
    node = toc[v["d"]]
    assert node["head"] == "觀因緣品第一" and node["type"] == "pin"
    assert node["parent"] == -1
    assert "path" not in v
    heads = [t["head"] for t in toc]
    assert heads == ["釋僧叡序", "觀因緣品第一"]
    # 卷二那段不在任何 div 內
    assert next(s for s in segs if "卷二第一段" in s["sources"]["lzh"])["d"] == -1
