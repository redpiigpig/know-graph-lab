"""tripitaka_nanchuan 純函式測試（零 network）。

漢譯南傳的編號陷阱全在相應部：相應號每冊重編、相應與品同深度、
判別要看標題結尾。任一條沒處理好，1,691 經會整批錯位而頁面看不出來。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tripitaka_nanchuan as nc  # noqa: E402
import tripitaka_parallels as tpp  # noqa: E402


def _node(i, depth, head, parent=-1, uid=None, juan=1):
    return {"i": i, "depth": depth, "type": "other", "head": head, "n": None,
            "parent": parent, "uid": uid or f"U{i}", "juan": juan}


# ── 編號解析 ──────────────────────────────────────────────
def test_bracket_no():
    """相應部的經號寫在全形方括號裡，且跨品連號。"""
    assert nc.bracket_no("〔一一〕歡喜園") == 11
    assert nc.bracket_no("〔一〕瀑流") == 1
    assert nc.bracket_no("〔二〇〕三彌提") == 20
    assert nc.bracket_no("第一　葦品") is None      # 品不是經


def test_ordinal_no():
    assert nc.ordinal_no("第一　諸天相應") == 1
    assert nc.ordinal_no("第十一　帝釋相應") == 11
    assert nc.ordinal_no("〔一〕瀑流") is None


# ── 相應部：三個會靜默錯位的陷阱 ───────────────────────────
def test_samyutta_numbering_is_cumulative_across_volumes(monkeypatch):
    """🚨 相應號在每冊重新編。N17 從「第八 聚落主相應」開始、跨篇又跳回
    「第三 念處相應」—— 讀標題序數會把 SN 45 當成 SN 3。
    正解是跨六冊照文件順序連號。"""
    monkeypatch.setattr(nc, "n_works", lambda lo, hi: ["V1", "V2"])
    tpp._TOC_CACHE["V1"] = [
        _node(0, 1, "第一　諸天相應"),
        _node(1, 3, "〔一〕瀑流", parent=0, uid="A1"),
        _node(2, 1, "第二　天子相應"),
        _node(3, 3, "〔一〕迦葉", parent=2, uid="B1"),
    ]
    # 第二冊的標題序數又從「第一」開始 —— 但它其實是第 3 個相應
    tpp._TOC_CACHE["V2"] = [
        _node(0, 1, "第一　因緣相應"),
        _node(1, 3, "〔一〕法說", parent=0, uid="C1"),
    ]
    monkeypatch.setitem(nc.NIKAYA, "sn",
                        {"vols": (13, 18), "depth": 3, "expect": "56 相應", "zh": "相應部"})
    monkeypatch.setitem(nc.NIKAYA, "dn", {"vols": (6, 8), "depth": 0, "expect": None, "zh": "長部"})
    monkeypatch.setitem(nc.NIKAYA, "mn", {"vols": (9, 12), "depth": 2, "expect": None, "zh": "中部"})
    idx, report = nc.build_index()
    # 只有 3 個相應 ≠ 56 → 閘擋下，整個相應部不掛
    assert report["sn"]["ok"] is False
    assert not any(k.startswith("sn") for k in idx)


def test_samyutta_detected_by_head_suffix_not_depth(monkeypatch):
    """🚨 N14 把相應與其下的品放在同一深度。靠深度分辨會把「食品」
    也算成一個相應，整批往後位移。判別要看標題結尾是不是「相應」。"""
    monkeypatch.setattr(nc, "n_works", lambda lo, hi: ["V"])
    tpp._TOC_CACHE["V"] = [
        _node(0, 1, "第一　因緣相應"),
        _node(1, 1, "第二　食品"),          # 同深度，但這是品不是相應
        _node(2, 3, "〔一一〕大樹", uid="X"),
    ]
    seen = []
    for node in tpp._TOC_CACHE["V"]:
        if node["depth"] <= 1 and node["head"].strip().endswith("相應"):
            seen.append(node["head"])
    assert seen == ["第一　因緣相應"], "「食品」不可被當成相應"


def test_dn_mn_counts_are_hard_gates(monkeypatch):
    """長部 34、中部 152 是巴利藏的定數。數不對表示層級判錯，
    寧可整個尼柯耶不掛，也不要掛錯。"""
    monkeypatch.setattr(nc, "n_works", lambda lo, hi: ["W"])
    tpp._TOC_CACHE["W"] = [_node(i, 0, f"{i}　某經") for i in range(3)]  # 只有 3 經
    monkeypatch.setitem(nc.NIKAYA, "dn", {"vols": (6, 8), "depth": 0, "expect": 34, "zh": "長部"})
    monkeypatch.setitem(nc.NIKAYA, "mn", {"vols": (9, 12), "depth": 2, "expect": 152, "zh": "中部"})
    monkeypatch.setitem(nc.NIKAYA, "sn", {"vols": (13, 18), "depth": 3, "expect": "56 相應", "zh": "相應部"})
    idx, report = nc.build_index()
    assert report["dn"]["ok"] is False
    assert not any(k.startswith("dn") for k in idx)


def test_dn_mn_index_is_sequential(monkeypatch):
    monkeypatch.setattr(nc, "n_works", lambda lo, hi: ["A", "B"])
    tpp._TOC_CACHE["A"] = [_node(0, 0, "一　梵網經", uid="A1"),
                           _node(1, 0, "二　沙門果經", uid="A2")]
    tpp._TOC_CACHE["B"] = [_node(0, 0, "三　阿摩晝經", uid="B1")]
    monkeypatch.setitem(nc.NIKAYA, "dn", {"vols": (6, 8), "depth": 0, "expect": 3, "zh": "長部"})
    monkeypatch.setitem(nc.NIKAYA, "mn", {"vols": (9, 12), "depth": 2, "expect": None, "zh": "中部"})
    monkeypatch.setitem(nc.NIKAYA, "sn", {"vols": (13, 18), "depth": 3, "expect": "56 相應", "zh": "相應部"})
    idx, report = nc.build_index()
    assert report["dn"]["ok"] is True
    assert idx["dn1"] == ("A", 0)
    assert idx["dn3"] == ("B", 0), "經號要跨冊連號，不是每冊重來"


# ── 取經文 ────────────────────────────────────────────────
def test_descendants_collects_whole_sutta():
    """長部的經在 depth 0，底下還有誦品；取經文要連子孫一起收。"""
    toc = [_node(0, 0, "一　梵網經"), _node(1, 1, "第一　誦品", parent=0),
           _node(2, 2, "稱讚如來", parent=1), _node(3, 0, "二　沙門果經")]
    assert nc.descendants(toc, 0) == {0, 1, 2}
    assert nc.descendants(toc, 3) == {3}
