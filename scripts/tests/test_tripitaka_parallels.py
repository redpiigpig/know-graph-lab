"""tripitaka_parallels 純函式測試（零 network/DB）。

鎖住四個真的踩過、且都是「靜默給出錯答案」型的坑：
  1. `sa-2.180` 是別譯雜阿含第 180 經，不是雜阿含 2.180
  2. 大正藏標題的漢數字是逐位排列（二二二＝222），不是十百進位
  3. 四部阿含在 CBETA 裡的經號位置各不相同，硬套一種會整批對錯
  4. `t213.4` 的品號不能丟 —— 丟了就把四千多筆逐品對照塌成「整部」
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tripitaka_parallels as tp  # noqa: E402


# ── uid 切分 ──────────────────────────────────────────────
def test_split_uid_longest_prefix_wins():
    assert tp.split_uid("sa1267")[:2] == ("sa", "1267")
    # 別譯雜阿含：正規式切法會誤判成 sa + '2.180'
    assert tp.split_uid("sa-2.180")[:2] == ("sa-2", ".180")
    assert tp.split_uid("sa-3.12")[:2] == ("sa-3", ".12")


def test_split_uid_partial_marker_and_segment():
    prefix, number, seg, partial = tp.split_uid("~t212.1#t0613b04")
    assert prefix == "t" and number == "212.1"
    assert seg == "t0613b04"
    assert partial is True, "'~' ＝部分平行，當成完整對應是誇大"
    assert tp.split_uid("dn22")[3] is False


# ── 漢數字 ────────────────────────────────────────────────
def test_cjk_number_positional_style():
    """大正藏用逐位排列：二二二＝222、三〇＝30。"""
    assert tp.cjk_number("二二二") == 222
    assert tp.cjk_number("三〇") == 30
    assert tp.cjk_number("一") == 1
    assert tp.cjk_number("一三六二") == 1362


def test_cjk_number_decimal_style():
    assert tp.cjk_number("十") == 10
    assert tp.cjk_number("二十二") == 22
    assert tp.cjk_number("一百五十二") == 152


def test_cjk_number_rejects_junk():
    assert tp.cjk_number("") is None
    assert tp.cjk_number("初誦") is None


def test_head_sutta_no():
    assert tp.head_sutta_no("（二二二）中阿含例品例經第十一（第五後誦）") == 222
    assert tp.head_sutta_no("（一）第一分初大本經第一") == 1
    assert tp.head_sutta_no("中阿含七法品第一（有十經）") is None  # 數字不在開頭括號


# ── 語言歸屬 ──────────────────────────────────────────────
def test_lang_of_simple_and_compound():
    assert tp.lang_of("sn") == "pi"
    assert tp.lang_of("sf") == "sa"
    assert tp.lang_of("d") == "bo"
    # 律典複合 uid 看第一段
    assert tp.lang_of("san-mu-bu-pm-gbm") == "sa"
    assert tp.lang_of("xct-mu-bi-pm-pc") == "bo"
    assert tp.lang_of("pli-tv-bu-vb-pj1") == "pi"
    # lzh 是漢文側，不是對照欄
    assert tp.lang_of("lzh-mi-bi-vb-pc") is None


def test_gandhari_and_patna_are_not_sanskrit():
    """犍陀羅語法句經與波特那法句經是中期印度語，
    塞進「梵文」欄是語言學上的錯誤。"""
    assert tp.lang_of("gdhp") == "pra"
    assert tp.lang_of("pdhp") == "pra"
    assert tp.lang_of("sn") != "pra"


def test_vinaya_school_mapping():
    assert tp.vinaya_parts("lzh-dg-bu-pm-pj") == ("lzh", "dg")
    assert tp.VINAYA_SCHOOL_TO_TAISHO["dg"] == "T1428"    # 法藏部＝四分律
    assert tp.VINAYA_SCHOOL_TO_TAISHO["sarv"] == "T1435"  # 說一切有部＝十誦律
    assert tp.VINAYA_SCHOOL_TO_TAISHO["tv"] is None       # 上座部無漢譯廣律
    assert tp.vinaya_parts("sn") == (None, None)


# ── 經號 → 段（用假的目錄樹，不碰檔案）─────────────────────
def _fake_toc(monkeypatch, work_id: str, toc: list[dict]):
    tp._TOC_CACHE[work_id] = toc
    tp._SUTTA_INDEX.pop(work_id, None)


def test_sutta_index_reads_number_from_head_when_n_missing(monkeypatch):
    """長阿含／中阿含的 jing 沒有 n，經號只在標題裡。"""
    _fake_toc(monkeypatch, "T0026", [
        {"i": 0, "depth": 0, "type": "pin", "head": "七法品第一", "n": None,
         "parent": -1, "seg": "S0", "juan": 1},
        {"i": 1, "depth": 1, "type": "jing", "head": "（一）中阿含七法品善法經第一",
         "n": None, "parent": 0, "seg": "S1", "juan": 1},
        {"i": 2, "depth": 1, "type": "jing", "head": "（二二二）中阿含例品例經第十一",
         "n": None, "parent": 0, "seg": "S222", "juan": 60},
    ])
    assert tp.jing_seg("T0026", "1") == "S1"
    assert tp.jing_seg("T0026", "222") == "S222"
    assert tp.jing_seg("T0026", "999") is None


def test_sutta_index_ekottarika_uses_pin_dot_jing(monkeypatch):
    """增壹阿含 SC 用「品.經」（ea32.2），CBETA 的 n 是品內序號。"""
    _fake_toc(monkeypatch, "T0125", [
        {"i": 0, "depth": 0, "type": "pin", "head": "十念品第二", "n": "2",
         "parent": -1, "seg": "P2", "juan": 1},
        {"i": 1, "depth": 1, "type": "jing", "head": "（一）", "n": "1",
         "parent": 0, "seg": "P2J1", "juan": 1},
        {"i": 2, "depth": 1, "type": "jing", "head": "（二）", "n": "2",
         "parent": 0, "seg": "P2J2", "juan": 1},
    ])
    assert tp.jing_seg("T0125", "2.2") == "P2J2"
    assert tp.jing_seg("T0125", "2.9") is None


def test_range_uid_resolves_to_its_start(monkeypatch):
    """'sa1060-1061' 指一段連續的經 —— 取起點，不硬拆成多筆。"""
    _fake_toc(monkeypatch, "T0099", [
        {"i": 0, "depth": 0, "type": "jing", "head": "（一〇六〇）", "n": "1060",
         "parent": -1, "seg": "S1060", "juan": 38},
    ])
    assert tp.jing_seg("T0099", "1060-1061") == "S1060"


def test_pin_seg(monkeypatch):
    """t213.4 的品號＝跨語言主對齊層，不可丟。"""
    tp._TOC_CACHE["T0213"] = [
        {"i": 0, "depth": 0, "type": "pin", "head": "1 有為品", "n": "1",
         "parent": -1, "seg": "A", "juan": 1},
        {"i": 1, "depth": 0, "type": "pin", "head": "法集要頌經放逸品第四", "n": "4",
         "parent": -1, "seg": "D", "juan": 1},
    ]
    assert tp.pin_seg("T0213", "4") == "D"
    assert tp.pin_seg("T0213", "9") is None
    assert tp.pin_seg("T0213", None) is None


def test_label_of():
    names = {"sn": "Saṁyutta Nikāya"}
    assert tp.label_of("sn", "22.12", names) == "SN 22.12（Saṁyutta Nikāya）"
    assert tp.label_of("zz", "1", {}) == "ZZ 1"
