# -*- coding: utf-8 -*-
"""鎖住 conversion 術語收斂的兩道閘：英文佐證、受詞檢查。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from redo_conversion_terms import hits, rewrite_zh  # noqa: E402


# ── 英文佐證閘 ────────────────────────────────────────────────────────────────
def test_kaishin_with_evidence_is_selected():
    src = ["He described his conversion and his later study in America."]
    zh = ["他敘述了他的回心歷程，以及其後在美國的求學。"]
    assert hits(src, zh) == [0]


def test_no_english_evidence_is_left_alone():
    """「皈依」在講佛教皈依三寶時是對的——英文沒有 convert 就別碰。"""
    src = ["The disciple takes refuge in the Buddha, the Dharma, and the Sangha."]
    zh = ["弟子皈依佛、皈依法、皈依僧。"]
    assert hits(src, zh) == []


def test_catholic_context_keeps_guiyi():
    src = ["Several converts to the Catholic Church joined the Jesuit mission."]
    zh = ["數名皈依天主教會的人加入了耶穌會的宣教。"]
    assert hits(src, zh) == []


def test_catholic_context_still_selected_when_kaishin_present():
    """天主教語境的豁免只保「皈依」，「回心」照改。"""
    src = ["The Catholic convert described his conversion at length."]
    zh = ["這位皈依天主教者詳述了他的回心經過。"]
    assert hits(src, zh) == [0]


def test_already_canonical_is_not_touched():
    src = ["His conversion took place in 1878."]
    zh = ["他的歸信發生在一八七八年。"]
    assert hits(src, zh) == []


def test_untranslated_paragraph_is_skipped():
    assert hits(["His conversion took place in 1878."], [None]) == []


def test_conversation_is_not_conversion():
    r"""\b 邊界：conversation 不可觸發。"""
    src = ["Their conversation turned to religion."]
    zh = ["他們的談話轉向宗教，他因此信主。"]
    assert hits(src, zh) == []


# ── 改寫規則 ──────────────────────────────────────────────────────────────────
def test_plain_noun_swap():
    assert rewrite_zh("他的回心歷程") == "他的歸信歷程"
    assert rewrite_zh("回心者如何協調") == "歸信者如何協調"
    assert rewrite_zh("皈依基督教") == "歸信基督教"
    assert rewrite_zh("日本人改宗基督教") == "日本人歸信基督教"


def test_causative_phrase_reads_as_chinese():
    """「他回心父親」是英文 converted his father 的直譯，中文不成話。"""
    assert rewrite_zh("他回心父親後數個月") == "他使父親歸信後數個月"
    assert rewrite_zh("鑑三使他的父親回心信仰基督教") == "鑑三使他的父親歸信基督教"


def test_gaizong_wei_phrase():
    assert rewrite_zh("名和橫井改宗為基督教") == "名和橫井歸信基督教"


def test_xinzhu_forms():
    assert rewrite_zh("他們所領人信主者") == "他們所領人歸信者"
    assert rewrite_zh("信主的人通常") == "歸信的人通常"


def test_pacifism_is_not_a_religion():
    """「歸信非戰論」不通——受詞是主張時原樣留著。"""
    assert rewrite_zh("向同仁宣布皈依非戰論。") == "向同仁宣布皈依非戰論。"
    assert rewrite_zh("聽述路德而皈依再臨思想") == "聽述路德而皈依再臨思想"


def test_mixed_paragraph_only_the_religious_object_changes():
    got = rewrite_zh("他先皈依基督教，數年後又宣布皈依非戰論。")
    assert got == "他先歸信基督教，數年後又宣布皈依非戰論。"


def test_paragraph_with_only_a_non_religion_object_is_not_a_hit():
    """改寫後沒變就不算命中，免得白寫一次檔。"""
    src = ["He converted to pacifism."]
    zh = ["他皈依非戰論。"]
    assert hits(src, zh) == []


def test_juezhi_and_guizhu_are_left_alone():
    """「決志」多半在講下定決心，「歸主」語感不等值——都不動。"""
    assert rewrite_zh("要獨立的決志") == "要獨立的決志"
    assert rewrite_zh("他終於歸主") == "他終於歸主"


def test_unambiguous_phrase_needs_no_english_evidence():
    """英文寫 "initial commitment to Christianity" 而非 conversion，意思一樣——
    受詞明確是基督教的片語不必等佐證。"""
    src = ["After this initial commitment to Christianity, he trained in fisheries science."]
    zh = ["在初次皈依基督教之後，他進修水產科學。"]
    assert hits(src, zh) == [0]


def test_unambiguous_phrase_still_yields_to_the_catholic_guard():
    src = ["He entered the Catholic Church that year."]
    zh = ["他那一年皈依基督教會（天主教）。"]
    assert hits(src, zh) == []
