# -*- coding: utf-8 -*-
"""avesta_translate.py 的純函式測試 —— 分批與落地前的退回閘。

這支腳本翻壞的方式都不會報錯：中文欄有字、段數也對，只有真的去讀
才發現那是英文原樣、拒絕語或簡體。退回閘就是為此存在。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from avesta_translate import (  # noqa: E402
    BATCH, BATCH_CHARS, SOLO_CHARS, make_batches, reject_reason,
)


def seg(en, ref="Vd 1.1"):
    return {"en": en, "ref": ref, "orig": "", "zh": ""}


# ───────────────── 分批 ─────────────────

def test_long_segment_goes_alone():
    """逾千字的段落跟別段同批會撐爆回傳 JSON，整批報廢。"""
    todo = [(0, seg("a" * 50)), (1, seg("b" * (SOLO_CHARS + 1))), (2, seg("c" * 50))]
    batches = make_batches(todo)
    solo = [b for b in batches if len(b) == 1 and b[0][0] == 1]
    assert solo, "超長段落沒有單獨成批"


def test_batch_respects_char_budget():
    todo = [(i, seg("x" * 900)) for i in range(6)]
    for b in make_batches(todo):
        assert sum(len(s["en"]) for _, s in b) <= BATCH_CHARS or len(b) == 1


def test_batch_respects_count_cap():
    todo = [(i, seg("x")) for i in range(BATCH * 3)]
    for b in make_batches(todo):
        assert len(b) <= BATCH


def test_every_segment_appears_exactly_once():
    """分批不可漏段也不可重複——漏了就是那一段永遠沒有中文而版面正常。"""
    todo = [(i, seg("y" * (i * 37 % 900 + 10))) for i in range(40)]
    idxs = [i for b in make_batches(todo) for i, _ in b]
    assert sorted(idxs) == list(range(40))


# ───────────────── 退回閘 ─────────────────

def test_accepts_a_normal_translation():
    zh = "物質世界的造主啊，持阿沙的聖者啊！哪一處大地最為歡喜？"
    assert reject_reason(zh, "O Maker of the material world...") is None


def test_rejects_untranslated_english():
    """模型有時直接回英文原樣。中文欄看起來有東西，其實一個字沒翻。"""
    en = "The first of the good lands and countries which I, Ahura Mazda, created."
    assert reject_reason(en, en) is not None


def test_rejects_refusal_and_ai_preamble():
    for bad in ["抱歉，我無法翻譯這段內容。", "As an AI language model, I cannot..."]:
        assert reject_reason(bad, "x") is not None


def test_rejects_simplified_chinese():
    # 使用者鐵則：任何寫入一律繁體
    assert reject_reason("这是第一块好土地，我阿胡拉‧马兹达所造。", "x") is not None


def test_rejects_markdown_fence_leakage():
    assert reject_reason("```json\n物質世界的造主啊\n```", "x") is not None


def test_rejects_japanese_kana():
    assert reject_reason("アフラ‧マズダーが答えた", "x") is not None


def test_rejects_empty_and_too_short():
    assert reject_reason("", "x") is not None
    assert reject_reason("　", "x") is not None
    assert reject_reason("好", "x") is not None


def test_does_not_reject_translation_containing_numbers_and_parens():
    """數字與括號是本書的實質內容，不可被閘誤殺。"""
    zh = "他當受四百鞭：以馬鞭四百，以斯勞沙鞭四百（見〔第四章〕）。"
    assert reject_reason(zh, "x") is None


def test_does_not_reject_translation_with_transliterated_names():
    zh = "查拉圖斯特拉問阿胡拉‧馬茲達：艾里亞納‧瓦埃賈的納蘇該如何處置？"
    assert reject_reason(zh, "x") is None


# ───────────────── 專名比對（去附加符號）─────────────────

from avesta_translate import fold, mentions  # noqa: E402


def test_diacritics_are_folded_for_matching():
    """詞庫寫 daēva，英譯寫 Daeva；比不到的話「迭瓦」永遠進不了 prompt。"""
    blob = fold("The Daevas and the corpse of Verethraghna, said Shkand.")
    assert mentions("daēva", blob)
    assert mentions("Vərəθraγna", blob)
    assert mentions("Škand-gumānīg Wizār", blob)


def test_slash_keys_match_either_side():
    blob = fold("the Videvdad prescribes; the magus said")
    assert mentions("Vendidad / Videvdad", blob)
    assert mentions("magi / magus", blob)


def test_multiword_titles_match_on_their_first_word():
    """英譯常只寫 "the Shkand"，鍵卻是完整書名——不試首詞就會漏，
    而模型會自己另譯書名，版面照樣正常。"""
    assert mentions("Škand-gumānīg Wizār", fold("as the Shkand teaches"))
    assert mentions("Ardā Wīrāz Nāmag", fold("in the Arda Wiraz account"))


def test_short_keys_do_not_match_promiscuously():
    """短詞會到處命中，反而把不相干的專名塞進 prompt 稀釋掉真正相關的。"""
    assert not mentions("Ab", fold("about the land"))
    assert not mentions("Sad Dar", fold("he was sad and went home"))


def test_absent_name_is_not_matched():
    assert not mentions("Anahita", fold("The first of the good lands."))


# ───────────────── 回傳鍵正規化（跨引擎）─────────────────

from avesta_translate import normalise_keys  # noqa: E402


def test_haiku_bracketed_keys_are_accepted():
    """Haiku 把鍵回成 "[2]"（照抄 prompt 的段落標記），Gemini／NVIDIA 回 "2"。

    2026-09-06 實測：只查 "2" 的話整批對不上，而腳本一個字都不印，靜靜空轉。
    """
    assert normalise_keys({"[2]": "甲", "[6]": "乙"}) == {"2": "甲", "6": "乙"}
    assert normalise_keys({"2": "甲"}) == {"2": "甲"}
    assert normalise_keys({2: "甲"}) == {"2": "甲"}


def test_non_string_values_are_dropped():
    assert normalise_keys({"1": None, "2": 3, "3": "丙"}) == {"3": "丙"}


def test_non_dict_returns_empty():
    assert normalise_keys(["甲", "乙"]) == {}
    assert normalise_keys(None) == {}


# ───────────────── 單段批次：模型把長段拆碎 ─────────────────

from avesta_translate import join_parts  # noqa: E402


def test_join_parts_restores_a_split_passage():
    """單段批次時 Haiku 常不理會段落標記，把長段拆成 1,2,3,4 回來。

    2026-09-06 全書跑完有 18 段卡在這裡：鍵對不上而整段譯不到。
    整份回應本來就只講這一段，按鍵序併回即可。
    """
    got = {"2": "第二塊", "1": "第一塊", "10": "第十塊", "3": "第三塊"}
    assert join_parts(got) == "第一塊\n第二塊\n第三塊\n第十塊"   # 數值排序，非字典序


def test_join_parts_drops_blank_pieces():
    assert join_parts({"1": "甲", "2": "   ", "3": "乙"}) == "甲\n乙"


def test_join_parts_single_piece():
    assert join_parts({"1": "整段"}) == "整段"


# ───────────────── 起句引錄：閘不可誤殺 ─────────────────

from avesta_translate import is_citation_list  # noqa: E402

CITATION_EN = ("Ahura Mazda answered: 'These are the words in the Gathas that are to be "
               "said twice:- ahya yasa ... urvanem (Y28.2), humatenam ... mahi (Y35.2), "
               "ashahya aad saire ... ahubya (Y35.8).")


def test_citation_list_is_recognised():
    assert is_citation_list(CITATION_EN)


def test_ordinary_prose_is_not_a_citation_list():
    assert not is_citation_list("The first of the good lands which I, Ahura Mazda, created.")
    # 只有一個出處、沒有省略號——正文偶爾夾一個出處不算引錄
    assert not is_citation_list("See the passage (Y28.2) for the wording.")


def test_citation_segments_survive_the_han_ratio_gate():
    """迦薩起句本來就該保留轉寫不譯，漢字自然少。

    2026-09-06 全書跑完僅存的兩段未譯（Vd 10.4、10.8）就是被這條誤殺的。
    """
    zh = ("阿胡拉‧馬茲達答道：「以下是迦薩中當誦二遍的詞句，你當高聲誦二遍：──"
          "ahya yasa ... urvanem（Y28.2）、humatenam ... mahi（Y35.2）、"
          "ashahya aad saire ... ahubya（Y35.8）。")
    assert reject_reason(zh, CITATION_EN) is None
    # 同一段譯文若來源不是引錄，仍應被擋下（門檻只對引錄放寬）
    assert reject_reason(zh, "The first of the good lands.") is not None


def test_english_passthrough_still_rejected_even_for_citations():
    """放寬門檻不等於放行英文原樣。"""
    assert reject_reason(CITATION_EN, CITATION_EN) is not None


# ───────────────── 截斷閘：長段被摘要 ─────────────────

def test_summarised_long_passage_is_rejected():
    """模型面對長段落會「講重點」——中文欄有字、讀起來通順，
    只有跟英譯並排才看得出少了三分之二。

    2026-09-06 全書跑完有 11 段這樣，最慘的英譯 1303 字只剩 47 字。
    """
    en = "A" * 800
    assert reject_reason("阿胡拉‧馬茲達答道：義人停留三十天。", en) is not None


def test_full_translation_of_long_passage_passes():
    en = "A" * 800
    zh = "阿" * 260          # 比值 0.33，接近全書中位數 0.31
    assert reject_reason(zh, en) is None


def test_short_segments_are_not_subject_to_the_ratio():
    """短段落的中英字數比波動大，套比值會誤殺。"""
    assert reject_reason("他答道。", "He answered thus, saying so.") is None


# ───────────────── 長段切塊分譯 ─────────────────

from avesta_translate import LONG_CHARS, PIECE_CHARS, split_long_en  # noqa: E402


def test_long_passage_is_split_into_manageable_pieces():
    """合併段（Vd 7.5-8、Vd 12.22-24）英譯有八百到一千六百字，
    模型面對這種長度一律講重點——即使明令不可摘要也一樣，實測連退三輪不收斂。"""
    en = "This is a sentence about the corpse. " * 40      # ~1480 字
    pieces = split_long_en(en)
    assert len(pieces) > 1
    assert all(len(p) <= PIECE_CHARS * 1.8 for p in pieces)


def test_split_never_breaks_mid_sentence():
    en = "First one here. Second one here. Third one here. " * 20
    for p in split_long_en(en):
        assert p.endswith(".") or p.endswith("here")


def test_split_preserves_all_words():
    """切塊不可掉字——掉了就是漏譯，而併回來的譯文讀起來完全正常。"""
    en = " ".join(f"word{i}." for i in range(300))
    joined = " ".join(split_long_en(en))
    assert set(en.split()) == set(joined.split())


def test_short_passage_is_not_split():
    en = "A short verse."
    assert split_long_en(en) == [en]


def test_paragraph_boundaries_are_respected():
    en = "First paragraph.\nSecond paragraph.\nThird paragraph."
    assert split_long_en(en) == ["First paragraph.", "Second paragraph.", "Third paragraph."]


def test_long_threshold_is_below_the_truncation_danger_zone():
    """被摘要的那 11 段英譯都在 621 字以上；門檻須低於此才攔得到。"""
    assert LONG_CHARS < 621
