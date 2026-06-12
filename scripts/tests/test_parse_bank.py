"""decode_greek_morph 單元測試（純函式、不碰網路）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from parse_bank import (decode_greek_morph, GREEK_OPTIONS,  # noqa: E402
                        decode_hebrew_morph, HEBREW_OPTIONS)


def _golds(res):
    return {f["k"]: f["gold"] for f in res["fields"]}


def test_noun_nsf():
    r = decode_greek_morph("N-NSF")
    assert r["pos"] == "名詞"
    assert _golds(r) == {"case": "主格", "number": "單數", "gender": "陰性"}


def test_noun_with_suffix_ignored():
    # 專有名詞 -P / 標題 -T 後綴不影響 格數性
    r = decode_greek_morph("N-GSM-P")
    assert _golds(r) == {"case": "屬格", "number": "單數", "gender": "陽性"}


def test_article():
    r = decode_greek_morph("T-DPF")
    assert r["pos"] == "冠詞"
    assert _golds(r) == {"case": "與格", "number": "複數", "gender": "陰性"}


def test_finite_verb_present_active_indicative():
    r = decode_greek_morph("V-PAI-3S")
    assert r["pos"] == "動詞"
    assert _golds(r) == {"tense": "現在", "voice": "主動", "mood": "直說",
                         "person": "第三", "number": "單數"}


def test_second_aorist_prefix_stripped():
    r = decode_greek_morph("V-2AAI-3S")
    assert _golds(r)["tense"] == "不定過去"
    assert _golds(r)["voice"] == "主動"


def test_participle_has_cng():
    r = decode_greek_morph("V-PAP-NSM")
    g = _golds(r)
    assert g["mood"] == "分詞"
    assert g["case"] == "主格" and g["number"] == "單數" and g["gender"] == "陽性"


def test_infinitive_no_person_number():
    r = decode_greek_morph("V-PAN")
    g = _golds(r)
    assert g["mood"] == "不定詞"
    assert "person" not in g and "case" not in g


def test_deponent_voice_excluded():
    # 異相語態 E（關身/被動）不出題，回 None 以免黃金答案有爭議
    assert decode_greek_morph("V-PEI-1S") is None
    assert decode_greek_morph("V-PNI-3S") is None


def test_non_inflected_pos_returns_none():
    for code in ("CONJ", "PREP", "ADV", "COND", "PRT", "P-1AS", "D-NSM"):
        assert decode_greek_morph(code) is None


def test_garbage_returns_none():
    assert decode_greek_morph("") is None
    assert decode_greek_morph("ZZZ") is None
    assert decode_greek_morph("N-XYZ") is None


def test_all_golds_are_valid_options():
    # 任一解碼結果的 gold 必在該維度的選項清單內（頁面 dropdown 才出得來）
    for code in ("N-NSF", "V-PAI-3S", "V-PAP-NSM", "V-2AAI-1P", "T-GSN", "A-ASF"):
        r = decode_greek_morph(code)
        if not r:
            continue
        for f in r["fields"]:
            assert f["gold"] in GREEK_OPTIONS[f["k"]], f"{code}: {f['k']}={f['gold']} 不在選項"


# ── 希伯來文 ────────────────────────────────────────────────────────────────
def _hg(res):
    return {f["k"]: f["gold"] for f in res["fields"]}


def test_heb_verb_qal_perfect():
    r = decode_hebrew_morph("HVqp3ms")  # ברא 創造 創 1:1
    assert r["pos"] == "動詞"
    assert _hg(r) == {"stem": "Qal", "conj": "完成式", "person": "第三",
                      "gender": "陽性", "number": "單數"}


def test_heb_stem_case_sensitive():
    # 大小寫敏感：h=Hiphil、H=Hophal、p=Piel、P=Pual
    assert _hg(decode_hebrew_morph("HVhi3ms"))["stem"] == "Hiphil"
    assert _hg(decode_hebrew_morph("HVHi3ms"))["stem"] == "Hophal"
    assert _hg(decode_hebrew_morph("HVpp3ms"))["stem"] == "Piel"
    assert _hg(decode_hebrew_morph("HVPp3ms"))["stem"] == "Pual"


def test_heb_noun_gender_number_state():
    r = decode_hebrew_morph("HNcfsa")
    assert r["pos"] == "名詞"
    assert _hg(r) == {"gender": "陰性", "number": "單數", "state": "絕對"}


def test_heb_construct_state():
    assert _hg(decode_hebrew_morph("HNcmsc"))["state"] == "連屬"


def test_heb_participle_no_person():
    r = decode_hebrew_morph("HVqrms")  # qal 主動分詞 陽性單數
    g = _hg(r)
    assert g["conj"] == "主動分詞" and "person" not in g
    assert g["gender"] == "陽性" and g["number"] == "單數"


def test_heb_strip_optional_leading_H():
    assert decode_hebrew_morph("Ncfsa") is not None  # 第二語素無 H 前綴也可解


def test_heb_unknown_returns_none():
    assert decode_hebrew_morph("HC") is None       # 連接詞
    assert decode_hebrew_morph("HR") is None        # 介系詞
    assert decode_hebrew_morph("") is None


def test_heb_all_golds_valid_options():
    for code in ("HVqp3ms", "HVHi3ms", "HNcfsa", "HNcmsc", "HVqrms"):
        r = decode_hebrew_morph(code)
        for f in r["fields"]:
            assert f["gold"] in HEBREW_OPTIONS[f["k"]], f"{code}: {f['k']}={f['gold']}"
