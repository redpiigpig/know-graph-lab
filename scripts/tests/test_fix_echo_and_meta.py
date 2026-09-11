# -*- coding: utf-8 -*-
"""清譯文殘渣的三道判斷：拒譯回覆／原文回抄／傍點行，以及兩個不可誤傷的例外。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fix_echo_and_meta as fe  # noqa: E402


def test_meta_reply_is_blanked():
    zh = "申し訳ありませんが、提供いただいたテキストは日文ではなく、英文です。翻訳はお応えできません。"
    assert fe.classify("And of the triumphs", zh) == "meta"
    assert fe.repair("And of the triumphs", zh) is None


def test_tone_alone_is_not_a_meta_reply():
    """只看語氣會誤殺正文——「我已準備妥當，要往耶路撒冷去」被丟掉過。"""
    assert fe.classify("I am ready to go", "我已準備妥當，要往耶路撒冷去。") == "ok"


def test_echo_prefix_is_stripped():
    src = "五、汝今衣食を得るに困しむ、しからば汝も空の鳥のごとくなりて天に任せよ、"
    zh = src + " 五、你如今為衣食而困頓，那麼你也要像空中的鳥一樣，把命運交託於天。"
    assert fe.classify(src, zh) == "echo"
    assert fe.repair(src, zh).startswith("五、你如今")


def test_half_translated_is_partial_not_truncated():
    """🚨 沒有長度閘，「翻一半」會被當成回抄而截斷：
    「獨逸國に生れたる世界の市民」只剩「市民」。截斷比留著日文更糟。"""
    src = "独逸国に生れたる世界の市民"
    zh = "獨逸國に生れたる世界の市民"
    assert fe.classify(src, zh) == "partial"
    assert fe.repair(src, zh) == zh


def test_bilingual_pairs_are_never_touched():
    """🚨「原文　／　中譯」是刻意並列的（引詩），不是沒翻。"""
    src = "独逸国に生れたる世界の市民"
    zh = "独逸国に生れたる世界の市民" + fe.BILINGUAL_SEP + "生於德意志國的世界公民"
    assert fe.classify(src, zh) == "ok"
    assert fe.repair(src, zh) == zh


def test_quoted_kana_is_a_citation_not_a_miss():
    """正文在**討論**那個日文詞，砍掉就毀了那一句。"""
    zh = "（《馬可傳》第一章第十二節「往かしめし」乃英語之 Driveth，意為「無理逐趕」。）"
    assert fe.classify("Mark 1:12", zh) == "ok"


def test_bouten_line_is_kept_as_is():
    marks = "ヽヽヽヽヽヽヽヽヽヽ"
    assert fe.classify(marks, "申し訳ございませんが、翻訳すべきテキストがありません") == "bouten"
    assert fe.repair(marks, "申し訳…") == marks
