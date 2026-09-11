# -*- coding: utf-8 -*-
"""譯文輸出閘：壞輸出一定要擋下，正常輸出一個都不能誤殺。

2026-09-11 補。此前譯文**從來沒有驗過「它到底是不是中文」**——唯一的守門員
`_looks_like_prompt_echo` 只認中文提示詞，所以推理模型外洩的英文思考過程
一路綠燈存進 checkpoint 並且上線。豪斯評傳 sec5[57] 存了 22,590 字的
「We need to translate the given English paragraph…」。

誤殺這一側同樣重要：穆勒與潘尼卡的書本來就滿是梵文轉寫（atman、Naighantuka），
拉丁字母比漢字多是**正常**的。分界靠英文虛詞密度，不是靠字母比例。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translate_ebook_to_zh import unusable_reason  # noqa: E402


# ── 要擋下的 ──────────────────────────────────────────────────────────────────
def test_truncated_reasoning_tag():
    """🚨 病灶本體：<think> 開了沒關，代表回應被截斷在推理中間。"""
    assert unusable_reason("<think>Okay, the user wants me to translate") == "truncated-reasoning"


def test_reasoning_leak_english():
    got = unusable_reason(
        "We need to translate the given English paragraph into Traditional Chinese, "
        "following all the rules. We must not add any preface, explanation, or notes.")
    assert got in ("reasoning-leak", "untranslated")


def test_reasoning_leak_even_when_mostly_chinese():
    """外洩的推理常常中英夾雜——比例判準看不出來，招牌句看得出來。"""
    t = ("We need to translate 「日本作為一個國家並未選擇回顧」。"
         "或「日本作為一個國家並未選擇回顧，而是一貫地向前看。」"
         "這樣讀起來比較自然，中文的引號要用「」。再看第二句怎麼處理比較好。")
    assert unusable_reason(t) == "reasoning-leak"


def test_untranslated_english_prose():
    assert unusable_reason(
        "The forms divi, dii, and dei do not enable us to establish an essential "
        "difference between the gods of Greece and those of Italy, and there is "
        "no reason to suppose that they were borrowed.") == "untranslated"


# ── 絕不可誤殺的 ──────────────────────────────────────────────────────────────
def test_plain_chinese_passes():
    assert unusable_reason("內村於1893年出版《基督信徒的慰藉》，時年三十二。") == ""


def test_sanskrit_transliteration_passes():
    """🚨 拉丁字母遠多於漢字，但那是術語轉寫不是沒譯——虛詞密度接近 0。"""
    t = ("《娑摩吠陀的尼達那經》（Nidana-sutra）與《波羅提娑佉》（Pratisakhya）、"
         "奈漢圖卡（Naighantuka）、奈伽瑪（Naigama）、Charana、Sruti、Smriti、"
         "Anupada-sutra、Asvalayana、Shadgurushishya、parsadam、atman、anila。")
    assert unusable_reason(t) == ""


def test_short_english_term_in_chinese_passes():
    assert unusable_reason("它們屬於語言科學（the science of language）發展的早期階段。") == ""


def test_english_sentence_buried_in_chinese_paragraph():
    """🚨 整段比例過得了關，中間卻夾著一整句沒譯的英文——比例判準看不到這種。"""
    t = ("在赫西俄德的敘述中，宙斯推翻克洛諾斯之後接掌了天界，並與兄弟均分世界："
         "海洋歸波塞冬，冥界歸哈得斯，而天空歸宙斯自己。這一段分配的敘事在後世"
         "神話學者之間引起長期爭論，穆勒本人也在此處留下了相當長的一段案語，"
         "以下是他徵引的原文段落。"
         "of Hesiod, we are told that Zeus, after having dethroned Kronos, took "
         "possession of the sky, and that he divided the world with his brothers, "
         "so that the sea fell to Poseidon and the nether world to Hades.")
    assert unusable_reason(t) == "partial-untranslated"


def test_short_english_quotation_passes():
    """引號裡的短句、書名、術語不該中——門檻是連續 120 個字母。"""
    assert unusable_reason(
        "穆勒稱之為「the science of language」，並在《比較神話學》中反覆申論此點。") == ""


def test_bilingual_verse_row_passes():
    """並列體例「原文　／　中譯」是刻意的，不是沒譯。"""
    assert unusable_reason("Trust in the Lord with all thine heart　／　你要專心仰賴耶和華") == ""


def test_empty_is_not_this_gates_problem():
    assert unusable_reason("") == ""
    assert unusable_reason(None) == ""
