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


# ── 卍續藏 X ───────────────────────────────────────────────
def test_xuzang_divisions_cover_1_to_1671():
    """X 第一層部類（抓自 CBETA 原書目錄）必須連續覆蓋經號 1–1671。"""
    prev = 0
    for _k, _l, lo, hi in tc.XUZANG_DIVISIONS:
        assert lo == prev + 1, f"{_l} 起點 {lo} 與前一部尾 {prev} 不連續"
        assert hi >= lo
        prev = hi
    assert prev == 1671
    assert tc.division_of("X", 240) == "x-jingshu"     # 華嚴綱要
    assert tc.division_of("X", 1571) == "x-shizhuan"   # 五燈全書
    assert tc.division_of("X", 1) == "x-india"


def test_division_of_refuses_unknown_canon():
    """🚨 原本寫成「不是 T 就套南傳表」—— 加 X 進來時整部續藏會被默默
    按冊號丟進南傳八分部，每部都拿到看似正常的 division_key。必須明列。"""
    import pytest
    with pytest.raises(ValueError):
        tc.division_of("J", 1, vol=1)          # 嘉興藏，還沒定部類表
    assert tc.division_of("N", 1, vol=9) == "n-majjhima"   # N 仍照冊號


def test_xuzang_subdivisions_nest_inside_their_division():
    """109 個子類都必須落在自己的第一層部類區間內，否則就是抄錯了。"""
    divs = {k: (lo, hi) for k, _l, lo, hi in tc.XUZANG_DIVISIONS}
    for key, label, spans in tc.XUZANG_SUBDIVISIONS:
        parent = key.rsplit("-", 1)[0]
        lo, hi = divs[parent]
        for a, b in spans:
            assert lo <= a <= b <= hi, f"{label} {a}-{b} 落在 {parent} {lo}-{hi} 之外"


def test_shizhuan_subdivisions_are_interleaved_not_contiguous():
    """🚨 史傳部的子類經號是**交錯**的（雜傳散在 1623-1628、1640-1645…），
    假設連續會把感應神異傳、居士善女傳整批吃進雜傳。"""
    sub = {k: spans for k, _l, spans in tc.XUZANG_SUBDIVISIONS}
    assert len(sub["x-shizhuan-011"]) > 1          # 雜傳本身就是多段
    assert tc.subdivision_of("X", 1646) == "x-shizhuan-013"   # 居士善女傳
    assert tc.subdivision_of("X", 1645) == "x-shizhuan-011"   # 雜傳
    assert tc.subdivision_of("X", 1639) == "x-shizhuan-012"   # 感應神異傳
    assert tc.subdivision_of("T", 262) == ""       # 只有 X 有子類


def test_split_work_title_suffix_stripped_but_real_juan_titles_kept():
    """CBETA 把 6 部跨冊的書切成兩檔，書名尾巴加「(第1卷-第44卷)」。
    那是檔案註記不是書名；但「華嚴經論〔卷十〕」「四家語錄卷一」的卷是書名本身。"""
    assert tc._norm_title("華嚴綱要(第1卷-第44卷)", "X") == "華嚴綱要"
    assert tc._norm_title("五燈全書(第34卷-第120卷)", "X") == "五燈全書"
    assert tc._norm_title("華嚴經論〔卷十〕", "X") == "華嚴經論〔卷十〕"
    assert tc._norm_title("馬祖道一禪師廣錄（四家語錄卷一）", "X") == "馬祖道一禪師廣錄（四家語錄卷一）"
    # 🚨 南傳不可剝：N01n0001「經分別(第1卷-第4卷)」與 N02n0001「經分別(第5卷-第15卷)」
    # 是**兩部不同的書**（id 帶冊號），卷範圍正是區分它們的唯一資訊。全 N 有 51 筆。
    assert tc._norm_title("經分別(第1卷-第4卷)", "N") == "經分別(第1卷-第4卷)"
    assert tc._norm_title("長部經典(第15卷-第23卷)", "N") == "長部經典(第15卷-第23卷)"


def test_merge_parts_offsets_toc_and_segment_pointers():
    """🚨 段的 i、目錄的 i/parent、段指向目錄的 d 都是**檔內索引**。
    直接串接會讓後半部的目錄父子鏈指到前半部的節點上 ——
    側欄看起來有東西，層級卻全錯，而頁面完全正常。"""
    a = ({"id": "X0240", "juan_count": 44,
          "toc": [{"i": 0, "parent": -1, "head": "上"},
                  {"i": 1, "parent": 0, "head": "上-子"}], "terms": []},
         [{"i": 0, "d": 0, "uid": "A0"}, {"i": 1, "d": 1, "uid": "A1"}], [])
    b = ({"id": "X0240", "juan_count": 36,
          "toc": [{"i": 0, "parent": -1, "head": "下"},
                  {"i": 1, "parent": 0, "head": "下-子"}], "terms": []},
         [{"i": 0, "d": 0, "uid": "B0"}, {"i": 1, "d": -1, "uid": "B1"}], [])
    meta, segs, _ = tc.merge_parts([a, b])
    assert [s["uid"] for s in segs] == ["A0", "A1", "B0", "B1"]
    assert [s["i"] for s in segs] == [0, 1, 2, 3]
    # 後半的目錄節點要位移，父指標跟著位移，根節點仍是 -1
    assert [n["i"] for n in meta["toc"]] == [0, 1, 2, 3]
    assert [n["parent"] for n in meta["toc"]] == [-1, 0, -1, 2]
    # 後半的段要指到後半自己的目錄節點（2），不是前半的 0
    assert segs[2]["d"] == 2
    assert segs[3]["d"] == -1, "本來就不屬任何節點的段要保持 -1"
    assert meta["xml_parts"] == 2


def test_chan_dialog_paragraphs_are_not_dropped():
    """🚨 禪宗語錄的問答體 <cb:dialog><sp><p>…</p></sp> —— 走訪器不往下走
    就整批靜默丟掉。達磨大師破相論 X1220 全篇問答，因此一度解析成 0 段；
    全 X 部 60 部用了它、約 90.7 萬字。T／N 一個都沒有，故此洞到收 X 才現形。"""
    doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xmlns:cb="{CB}" xml:id="X63n1220">
 <teiHeader><fileDesc>
  <titleStmt><title level="m" xml:lang="zh-Hant">達磨大師破相論</title></titleStmt>
  <extent>1卷</extent>
  <publicationStmt><idno type="CBETA">
    <idno type="canon">X</idno>.<idno type="vol">63</idno>.<idno type="no">1220</idno>
  </idno></publicationStmt>
 </fileDesc></teiHeader>
 <text><body>
  <milestone unit="juan" n="1"/><pb n="0008c" ed="X"/>
  <cb:div><cb:dialog type="qa">
    <sp cb:type="question"><lb n="0008c09" ed="X"/><p>若復有人志求佛道者，當脩何法最為省要？</p></sp>
    <sp cb:type="answer"><lb n="0008c12" ed="X"/><p>唯觀心一法，總攝諸法，最為省要。</p></sp>
  </cb:dialog></cb:div>
 </body></text>
</TEI>"""
    tc._GAIJI = {}
    meta, segs, _ = tc.parse_work(doc)
    assert meta["id"] == "X1220"
    texts = [s["sources"]["lzh"] for s in segs]
    assert any("志求佛道" in t for t in texts), "問句被丟掉了"
    assert any("唯觀心一法" in t for t in texts), "答句被丟掉了"
    assert len(segs) >= 2


def test_only_own_canon_line_numbers_become_segment_keys():
    """🚨 X 的每一行同時標了兩套行號：卍續藏自己的 <lb ed="X"> 與
    新文豐影印本的 <lb ed="R013">，交錯出現。對任何 lb 都吃的話，段鍵會拿到
    **後出現的那個**，同一部書一半是卍續藏行號、一半是影印本行號 ——
    引用式錯了，而頁面完全正常。T／N 只有一套，所以此洞到收 X 才現形。"""
    doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xmlns:cb="{CB}" xml:id="X09n0240">
 <teiHeader><fileDesc>
  <titleStmt><title level="m" xml:lang="zh-Hant">華嚴綱要</title></titleStmt>
  <extent>80卷</extent>
  <publicationStmt><idno type="CBETA">
    <idno type="canon">X</idno>.<idno type="vol">9</idno>.<idno type="no">240</idno>
  </idno></publicationStmt>
 </fileDesc></teiHeader>
 <text><body>
  <milestone unit="juan" n="45"/>
  <pb n="0001a" ed="X"/>
  <lb n="0001a05" ed="X"/><lb n="0611a02" ed="R013"/>
  <p>于闐國三藏沙門實叉難陀譯經。</p>
 </body></text>
</TEI>"""
    tc._GAIJI = {}
    _meta, segs, _ = tc.parse_work(doc)
    assert segs, "應該有段"
    assert segs[0]["seg"] == "X09n0240_p0001a05", \
        f"段鍵要用卍續藏自己的行號，拿到的是 {segs[0]['seg']}"
    assert "0611a02" not in segs[0]["seg"], "影印本 R013 的行號不可當引用式"


def test_glossary_entries_are_not_dropped():
    """🚨 辭書體 <entry><form>詞目</form><cb:def><p>釋義</p></cb:def></entry>。
    「事義」那一類整部都是這個結構；不處理只會留下卷首標題 ——
    阿彌陀經疏鈔事義 X0425 一度只解出 16 字，而目錄頁看起來完全正常，
    只是顯示「這部書很短」。全 X 部 105 部、約 223.7 萬字。"""
    doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xmlns:cb="{CB}" xml:id="X22n0425">
 <teiHeader><fileDesc>
  <titleStmt><title level="m" xml:lang="zh-Hant">阿彌陀經疏鈔事義</title></titleStmt>
  <extent>1卷</extent>
  <publicationStmt><idno type="CBETA">
    <idno type="canon">X</idno>.<idno type="vol">22</idno>.<idno type="no">425</idno>
  </idno></publicationStmt>
 </fileDesc></teiHeader>
 <text><body>
  <milestone unit="juan" n="1"/><pb n="0685a" ed="X"/>
  <cb:div type="other"><lb n="0685a07" ed="X"/>
    <entry><form>雲棲寺</form>
      <cb:def><lb n="0685a08" ed="X"/><p>寺名雲棲，在錢塘五雲山後。</p></cb:def></entry>
    <entry><form>棲真寺</form>
      <cb:def><lb n="0685a12" ed="X"/><p>治平二年改名。</p></cb:def></entry>
  </cb:div>
 </body></text>
</TEI>"""
    tc._GAIJI = {}
    meta, segs, _ = tc.parse_work(doc)
    assert meta["id"] == "X0425"
    texts = [s["sources"]["lzh"] for s in segs]
    assert "雲棲寺" in texts and "棲真寺" in texts, "詞目沒收進來"
    assert any("錢塘五雲山" in t for t in texts), "釋義被丟掉了"
    # 詞目是小標，釋義是本文，兩者不可黏成一段
    assert [s["kind"] for s in segs if s["sources"]["lzh"] == "雲棲寺"] == ["head"]


def test_merge_counts_distinct_juan_not_sum_of_extents():
    """🚨 印本可能在同一卷中間斷冊：四分律含注戒本疏行宗記作
    「(第1卷-第3卷)」＋「(第3卷-第4卷)」，**卷三跨兩冊**。
    把兩檔的 extent 相加得 3+2=5 卷，實際只有 4 卷。"""
    a = ({"id": "X0714", "juan_count": 3, "toc": [], "terms": []},
         [{"i": 0, "d": -1, "uid": "a", "juan": 1},
          {"i": 1, "d": -1, "uid": "a2", "juan": 2},
          {"i": 2, "d": -1, "uid": "b", "juan": 3}], [])
    b = ({"id": "X0714", "juan_count": 2, "toc": [], "terms": []},
         [{"i": 0, "d": -1, "uid": "c", "juan": 3},   # 同一卷延續到下一冊
          {"i": 1, "d": -1, "uid": "d", "juan": 4}], [])
    meta, _segs, _ = tc.merge_parts([a, b])
    assert meta["juan_count"] == 4, "卷三只能算一次"
    assert meta["extent"] == "4卷"


# ── 切段 ──────────────────────────────────────────────────
def test_segment_key_is_taisho_line_number():
    """使用者定調：段鍵＝大正藏行號，不自編流水號。"""
    _, segs, _ = _parse()
    keys = [s["seg"] for s in segs]
    assert "T30n1564_p0001a07" in keys
    assert all(k.startswith("T30n1564_p") for k in keys), keys
    # seg 本身即通行引用式，不另存 cite 欄（同值重複 95 萬次沒有意義）
    assert all("cite" not in s for s in segs)


def test_uid_disambiguates_segments_sharing_a_line():
    """🚨 行號不唯一：同一行可以起頭好幾段（全藏 6.5%、672 部）。
    seg 是引用式（可重複），uid 才是鍵。撞鍵會讓對照掛到同行的別段上。"""
    _, segs, _ = _parse()
    uids = [s["uid"] for s in segs]
    assert len(uids) == len(set(uids)), "uid 必須唯一"
    # 樣本裡序的 head 與其後的 <p> 不同行，故此處 uid == seg；
    # 真有同行兩段時，第二段起加 .2 後綴
    same_line = [s for s in segs if s["seg"] == "T30n1564_p0001b10"]
    if len(same_line) > 1:
        assert same_line[1]["uid"].endswith(".2")
    assert all(s["uid"].startswith(s["seg"]) for s in segs)


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
    assert "uid" in eq[0]           # 對應註要能貼回確切段落，不能只有註號
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
    assert node["uid"] == v["uid"] or node["uid"].startswith("T30n1564_p")
    heads = [t["head"] for t in toc]
    assert heads == ["釋僧叡序", "觀因緣品第一"]
    # 卷二那段不在任何 div 內
    assert next(s for s in segs if "卷二第一段" in s["sources"]["lzh"])["d"] == -1
