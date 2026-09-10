# -*- coding: utf-8 -*-
"""鎖住 redo_conversion_terms.hits 的英文佐證閘。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from redo_conversion_terms import hits  # noqa: E402


def test_kaishin_with_evidence_is_cleared():
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


def test_catholic_context_still_cleared_when_kaishin_present():
    """天主教語境的豁免只保「皈依」，「回心」照清。"""
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
    """\\b 邊界：conversation 不可觸發。"""
    src = ["Their conversation turned to religion."]
    zh = ["他們的談話轉向宗教，他因此信主。"]
    assert hits(src, zh) == []
