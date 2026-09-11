# -*- coding: utf-8 -*-
"""日文讀本一課十題翻譯練習：語料驗證器與挖句器的純函式測試。

測的是不必連網、不必讀 28 MB 語料檔就能跑的那一層：斷詞結果怎麼被判讀、
哪些東西不算詞、助詞能不能拿去查詞表、三道閘各擋住什麼。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from build_japanese_exercises import anchor_note, item_for  # noqa: E402
from build_japanese_lemma_corpus import (  # noqa: E402
    Segmenter,
    Token,
    Vocabulary,
    balance_quotes,
    classify_register,
    clean_line,
    global_lesson,
    is_grammar,
    is_word,
    iter_units,
    may_consult_wordlist,
    sentence_is_keepable,
    split_sentences,
    to_hiragana,
)
from compose_japanese_sentences import (  # noqa: E402
    coverage_for,
    describe_lesson,
    entry_key,
    lesson_targets,
    resolve_lesson,
    verify_tokens,
)


# 一份縮小的詞表，欄位與 data/originalReaders/vocabulary/japanese-2000.json 同形。
# 「は＝歯」與「や＝屋」是真的在課本詞表裡，這兩條就是本檔要釘住的那個坑。
ENTRIES = [
    {"kana": "わたし", "kanji": "私", "pos": "名詞", "dictionaryForm": "",
     "glossZh": "我", "volume": 1, "readerLesson": 1},
    {"kana": "は", "kanji": "歯", "pos": "名詞", "dictionaryForm": "",
     "glossZh": "牙齒", "volume": 1, "readerLesson": 1},
    {"kana": "や", "kanji": "屋", "pos": "名詞", "dictionaryForm": "",
     "glossZh": "房子", "volume": 1, "readerLesson": 1},
    {"kana": "ほん", "kanji": "本", "pos": "名詞", "dictionaryForm": "",
     "glossZh": "書", "volume": 1, "readerLesson": 2},
    {"kana": "よみます", "kanji": "読みます", "pos": "動詞", "dictionaryForm": "読む",
     "glossZh": "讀", "volume": 1, "readerLesson": 2},
    {"kana": "いつも", "kanji": "", "pos": "副詞", "dictionaryForm": "",
     "glossZh": "總是", "volume": 1, "readerLesson": 3},
    {"kana": "あさごはん", "kanji": "朝ご飯", "pos": "名詞", "dictionaryForm": "",
     "glossZh": "早餐", "volume": 1, "readerLesson": 3},
    {"kana": "しゅうきょう", "kanji": "宗教", "pos": "名詞", "dictionaryForm": "",
     "glossZh": "宗教", "volume": 2, "readerLesson": 10},
]

LEMMAS = {
    "私": {"pos": "代名詞", "reading": "わたし", "count": 900, "docs": 80, "surfaces": ["私"]},
    "本": {"pos": "名詞", "reading": "ほん", "count": 400, "docs": 70, "surfaces": ["本"]},
    "読む": {"pos": "動詞", "reading": "よむ", "count": 300, "docs": 60,
             "surfaces": ["読ん", "読む", "読み"]},
    "宗教": {"pos": "名詞", "reading": "しゅうきょう", "count": 200, "docs": 40,
             "surfaces": ["宗教"]},
    "いつ": {"pos": "代名詞", "reading": "いつ", "count": 100, "docs": 30, "surfaces": ["いつ"]},
}

GRAMMAR = frozenset({"は", "を", "も", "ます", "た", "の", "。", "、"})


@pytest.fixture(scope="module")
def vocabulary() -> Vocabulary:
    return Vocabulary(ENTRIES)


@pytest.fixture(scope="module")
def segmenter() -> Segmenter:
    return Segmenter()


def tok(surface, base, pos, sub="", reading=""):
    return Token(surface=surface, base=base, pos=pos, sub=sub, reading=reading)


def check(tokens, vocabulary, lesson):
    return verify_tokens(
        tokens, vocabulary=vocabulary, lemmas=LEMMAS, lesson=lesson, grammar=GRAMMAR
    )


# ---------------------------------------------------------------- 助詞 vs 詞表


def test_particle_ha_is_never_looked_up_as_the_word_for_tooth(vocabulary):
    """🚨 主題助詞「は」不可被當成名詞「歯」（牙齒）。

    詞表裡「は」真的是歯。照假名比中，全書每個主題助詞都會印成「牙齒」——逐詞
    對譯層第一次試排就是這樣印出來的。這一條釘死，不要再讓它回來。
    """
    particle = tok("は", "は", "助詞", "係助詞", "は")
    assert may_consult_wordlist(particle) is False
    assert vocabulary.lookup(particle) is None
    # 而名詞的「歯」照樣查得到，擋的是助詞不是那個詞。
    assert vocabulary.lookup(tok("歯", "歯", "名詞", "普通名詞", "は"))["glossZh"] == "牙齒"


def test_particle_ya_is_not_the_word_for_house(vocabulary):
    assert vocabulary.lookup(tok("や", "や", "助詞", "終助詞", "や")) is None


def test_real_sentence_does_not_practise_a_lesson_word_through_a_particle(
    vocabulary, segmenter
):
    """整句跑一次：「わたしは本を読みます。」不可以算成練到了「歯」。"""
    report = check(segmenter.tokenize("わたしは本を読みます。"), vocabulary, lesson=2)
    practised = set(report["vocabulary"])
    assert entry_key({"kana": "は", "kanji": "歯"}) not in practised
    assert entry_key({"kana": "わたし", "kanji": "私"}) in practised
    assert report["passed"] is True


def test_two_character_auxiliary_may_still_fall_back_to_the_wordlist():
    """兩個字以上的助詞助動詞要能回退查表，不然「ある」「という」整批空掉。"""
    assert may_consult_wordlist(tok("ます", "ます", "助動詞", "", "ます")) is True
    assert may_consult_wordlist(tok("ながら", "ながら", "助詞", "接続助詞")) is True


def test_punctuation_never_consults_the_wordlist():
    assert may_consult_wordlist(tok("。", "。", "補助記号", "句点")) is False


# ---------------------------------------------------------------- 什麼不算詞


def test_numbers_and_brackets_are_not_words():
    """斷詞器把「2304」與「（」都標成名詞，放著會造出「二千三百零四」「左括號」。"""
    assert is_word(tok("2304", "2304", "名詞", "数詞")) is False
    assert is_word(tok("（", "（", "補助記号", "括弧開")) is False
    assert is_word(tok("２３０４", "２３０４", "名詞", "数詞")) is False
    assert is_word(tok("Bible", "Bible", "名詞", "普通名詞")) is False
    assert is_word(tok("宗教", "宗教", "名詞", "普通名詞")) is True


def test_grammar_classes_cover_both_tagsets():
    """UniDic 的「補助記号」與 janome 的「記号」都要算標點，換斷詞器不換判準。"""
    assert is_grammar(tok("。", "。", "補助記号", "句点")) is True
    assert is_grammar(tok("。", "。", "記号", "句点")) is True
    assert is_grammar(tok("宗教", "宗教", "名詞", "普通名詞")) is False


# ---------------------------------------------------------------- 詞組


def test_multi_morpheme_headwords_are_matched_as_one_word(vocabulary):
    """課本的「いつも」被斷成 いつ／も，逐個 token 查會判成尚未教過。"""
    tokens = [
        tok("いつ", "いつ", "代名詞", "", "いつ"),
        tok("も", "も", "助詞", "係助詞", "も"),
    ]
    spans = list(iter_units(tokens, vocabulary))
    assert len(spans) == 1
    assert spans[0][1]["glossZh"] == "總是"


def test_a_span_of_pure_particles_never_matches_a_headword(vocabulary):
    """整串都是助詞時不查詞組表——那是「は」那個坑的另一條路。"""
    tokens = [
        tok("に", "に", "助詞", "格助詞"),
        tok("は", "は", "助詞", "係助詞"),
    ]
    assert vocabulary.lookup_phrase(tokens) is None


# ------------------------------------------------- 第一道閘：基本形要有語料為證


def test_base_form_attestation_accepts_an_inflected_form_never_seen(vocabulary):
    """🚨 日文放寬的那一條：查基本形，不查表層形。

    「読まなければ」語料裡沒出現過，但辭書形「読む」出現過。日語活用規則可推，
    硬要求表層形出現過會把正確的句子整批誤判。表層形沒見過只記在 unseenForms。
    """
    tokens = [
        tok("私", "私", "代名詞", "", "わたし"),
        tok("は", "は", "助詞", "係助詞", "は"),
        tok("本", "本", "名詞", "普通名詞", "ほん"),
        tok("を", "を", "助詞", "格助詞", "を"),
        tok("読ま", "読む", "動詞", "一般", "よむ"),
    ]
    report = check(tokens, vocabulary, lesson=2)
    assert report["unattested"] == []
    assert report["unseenForms"] == ["読ま"]
    assert report["passed"] is True


def test_an_invented_word_is_rejected_as_unattested(vocabulary):
    tokens = [
        tok("私", "私", "代名詞", "", "わたし"),
        tok("は", "は", "助詞", "係助詞", "は"),
        tok("ぬるぽ", "ぬるぽ", "名詞", "普通名詞", "ぬるぽ"),
    ]
    report = check(tokens, vocabulary, lesson=3)
    assert report["unattested"] == ["ぬるぽ"]
    assert report["passed"] is False


def test_a_textbook_word_missing_from_the_corpus_is_still_attested(vocabulary):
    """「朝ご飯」戰前作家寫「朝飯」，語料查不到——但那是課本第 3 課教的詞。"""
    tokens = [
        tok("朝ご飯", "朝ご飯", "名詞", "普通名詞", "あさごはん"),
        tok("を", "を", "助詞", "格助詞", "を"),
        tok("読む", "読む", "動詞", "一般", "よむ"),
    ]
    assert "朝ご飯" not in LEMMAS
    report = check(tokens, vocabulary, lesson=3)
    assert report["unattested"] == []


# ----------------------------------------------------- 第二道閘：詞必須已教過


def test_a_later_lesson_word_is_untaught(vocabulary):
    tokens = [
        tok("宗教", "宗教", "名詞", "普通名詞", "しゅうきょう"),
        tok("の", "の", "助詞", "格助詞", "の"),
        tok("本", "本", "名詞", "普通名詞", "ほん"),
    ]
    assert check(tokens, vocabulary, lesson=3)["untaught"] == ["宗教"]
    # 第二冊第 10 課＝通編 60，到那時候就教過了。
    assert check(tokens, vocabulary, lesson=60)["untaught"] == []


def test_a_word_outside_the_two_thousand_is_untaught(vocabulary):
    tokens = [
        tok("私", "私", "代名詞", "", "わたし"),
        tok("は", "は", "助詞", "係助詞", "は"),
        tok("いつ", "いつ", "代名詞", "", "いつ"),
    ]
    # 「いつ」單獨出現不是課內詞（課內的是詞組「いつも」）。
    assert check(tokens, vocabulary, lesson=3)["untaught"] == ["いつ"]


def test_a_sentence_shorter_than_three_words_fails(vocabulary):
    tokens = [
        tok("私", "私", "代名詞", "", "わたし"),
        tok("。", "。", "補助記号", "句点"),
    ]
    report = check(tokens, vocabulary, lesson=1)
    assert report["words"] == 1
    assert report["passed"] is False


# --------------------------------------------------- 第三道閘：二十詞全覆蓋


def test_coverage_counts_only_this_lesson_words(vocabulary):
    targets = lesson_targets(vocabulary, 2)
    assert {entry["glossZh"] for entry in targets} == {"書", "讀"}
    reports = [{"vocabulary": [entry_key(targets[0])]}]
    coverage = coverage_for(reports, targets)
    assert coverage == {
        "lessonWords": 2,
        "practised": 1,
        "notPractised": [
            {"headword": "読みます", "kana": "よみます", "glossZh": "讀"}
        ],
    }


def test_coverage_is_complete_when_every_word_is_used(vocabulary):
    targets = lesson_targets(vocabulary, 2)
    reports = [{"vocabulary": [entry_key(entry) for entry in targets]}]
    assert coverage_for(reports, targets)["notPractised"] == []


# ------------------------------------------------------------ 課次身分


def test_lesson_numbering_is_volume_plus_lesson():
    """第二冊第 3 課與通編 53 是同一課；冊次叫第一冊／第二冊，不是上下冊。"""
    assert resolve_lesson(3, 2) == 53
    assert resolve_lesson(53, None) == 53
    assert global_lesson({"volume": 2, "readerLesson": 3}) == 53
    assert describe_lesson(53).startswith("第二冊第 3 課")


def test_lesson_out_of_range_for_a_volume_is_refused():
    with pytest.raises(SystemExit):
        resolve_lesson(51, 1)


# ------------------------------------------------------------ 句子清理


def test_unmatched_quote_is_stripped():
    """按句號切開後留下的開引號會印成半句話。"""
    assert balance_quotes("「誰方？") == "誰方？"
    assert balance_quotes("「誰方？」") == "「誰方？」"


def test_verse_numbers_and_furigana_are_dropped():
    assert clean_line("12") == ""
    assert clean_line("籠（こ）もよ") == "籠もよ"
    assert clean_line("0001　籠もよ") == "籠もよ"


def test_split_sentences_cuts_at_sentence_final_punctuation():
    got = list(split_sentences("これは本です。私は読みます。\n次の行。"))
    assert got == ["これは本です。", "私は読みます。", "次の行。"]


def test_keepable_rejects_a_fragment_and_a_chinese_line(vocabulary):
    """半句話（讀點結尾）與整句沒有假名的漢文都不是可引用的日文句子。"""
    tokens = [
        tok("私", "私", "代名詞", "", "わたし"),
        tok("は", "は", "助詞", "係助詞", "は"),
        tok("本", "本", "名詞", "普通名詞", "ほん"),
        tok("、", "、", "補助記号", "読点"),
    ]
    assert sentence_is_keepable("私は本、", tokens, vocabulary) is False
    assert sentence_is_keepable("殊方言欲稽。", tokens, vocabulary) is False


def test_keepable_accepts_a_whole_sentence_of_taught_words(vocabulary):
    tokens = [
        tok("私", "私", "代名詞", "", "わたし"),
        tok("は", "は", "助詞", "係助詞", "は"),
        tok("本", "本", "名詞", "普通名詞", "ほん"),
        tok("を", "を", "助詞", "格助詞", "を"),
        tok("読み", "読む", "動詞", "一般", "よむ"),
        tok("ます", "ます", "助動詞", "", "ます"),
        tok("。", "。", "補助記号", "句点"),
    ]
    assert sentence_is_keepable("私は本を読みます。", tokens, vocabulary) is True


def test_keepable_rejects_a_sentence_with_an_untaught_word(vocabulary):
    tokens = [
        tok("彼", "彼", "代名詞", "", "かれ"),
        tok("は", "は", "助詞", "係助詞", "は"),
        tok("本", "本", "名詞", "普通名詞", "ほん"),
        tok("を", "を", "助詞", "格助詞", "を"),
        tok("読み", "読む", "動詞", "一般", "よむ"),
        tok("ます", "ます", "助動詞", "", "ます"),
        tok("。", "。", "補助記号", "句点"),
    ]
    assert sentence_is_keepable("彼は本を読みます。", tokens, vocabulary) is False


# ------------------------------------------------------------ 斷詞器


def test_reading_is_hiragana():
    assert to_hiragana("ワタシ") == "わたし"
    assert to_hiragana("") == ""


def test_segmenter_reads_a_bungo_verb_as_one_word(segmenter):
    """🚨 文語「見給ひき」是 見る／給ふ／き 三個詞。

    janome 拆成 見／給／ひき 並替碎片造出「ふる」「ひる」這種辭書形，逐詞對譯層
    因此印出「揮舞」226 次。用 fugashi＋UniDic 就是為了這件事，這條測試順便說明
    輸出裡的 tokenizer 欄為什麼一定要記。
    """
    if segmenter.name != "fugashi":
        pytest.skip("這台機器沒有 fugashi，跑的是 janome")
    bases = [token.base for token in segmenter.tokenize("見給ひき")]
    assert bases == ["見る", "給ふ", "き"]


def test_segmenter_records_which_engine_ran(segmenter):
    described = segmenter.describe()
    assert described["name"] in {"fugashi", "janome"}
    assert described["version"] and described["dictionary"]


# ------------------------------------------------------------ 語體閘
#
# 🚨 兩段都是 `output/source-cache/original-readers/japanese-full/scripture/` 裡
# 實際存在的文字，同一卷、相鄰兩章，掛的是同一個「文語訳・公有領域」標籤。
# 第 1 章是現代語譯本（仍在著作權內），第 2 章才是明治元訳。兩個方向都要釘住：
# 判不出現代語會把有版權的文字當公有領域收；把文語誤判成現代語則會把整卷丟掉。

ISAIAH_1_MODERN = (
    "アモツの子イザヤが、ユダとエルサレムについて見た幻。"
    "これはユダの王、ウジヤ、ヨタム、アハズ、ヒゼキヤの治世のことである。"
    "天よ聞け、地よ耳を傾けよ、主が語られる。"
    "わたしは子らを育てて大きくした。しかし、彼らはわたしに背いた。"
    "牛は飼い主を知り、ろばは主人の飼い葉桶を知っている。"
)
ISAIAH_2_BUNGO = (
    "アモツの子イザヤが示されたるユダとヱルサレムとにかかる言。"
    "すゑの日にヱホバの家の山はもろもろの山のいただきに堅立ち、"
    "もろもろの嶺よりもたかく擧り、すべての國は流のごとく之につかん。"
    "おほくの民ゆきて相語いはん、率われらヱホバの山にのぼりヤコブの神の家にゆかん。"
)


def test_isaiah_one_is_classified_as_modern_japanese():
    """🚨 掛著「文語訳」標籤的以賽亞書第 1 章，實際上是現代語譯本。"""
    verdict = classify_register(ISAIAH_1_MODERN)
    assert verdict["register"] == "現代語"
    assert verdict["modernHits"] > verdict["bungoHits"]


def test_isaiah_two_is_classified_as_bungo():
    """同一卷第 2 章是真的明治元訳，不可被誤判成現代語而整章丟掉。"""
    verdict = classify_register(ISAIAH_2_BUNGO)
    assert verdict["register"] == "文語"
    assert verdict["bungoHits"] >= 3


def test_a_short_bungo_creed_is_not_called_uncertain():
    """信經只有幾百字，樣本少；短篇一個特徵就算數，否則會被誤報成可疑。"""
    # 實際檔案：使徒信経（日本聖公会 1941 年版），490 字，文語特徵只有「われら」一處。
    creed = (
        "我は天地の造主・全能の父なる神を信ず。"
        "我はその独子・われらの主イエス・キリストを信ず。"
    )
    verdict = classify_register(creed)
    assert verdict["chars"] < 800
    assert verdict["register"] == "文語"


def test_empty_text_is_uncertain_not_bungo():
    assert classify_register("")["register"] == "不確定"


# ------------------------------------------------- 引用題的中文由作者撰寫


def _hit(sentence_id: str, text: str):
    return {
        "row": {"id": sentence_id, "text": text, "title": "某篇", "author": "某人",
                "source": "aozora", "ref": "000001", "sourceUrl": "https://example.invalid"},
        "report": {"vocabulary": [], "unattested": [], "untaught": [],
                   "grammar": [], "passed": True},
    }


def test_a_practice_item_carries_no_chinese():
    """🚨 練習題不附中文（owner 2026-09-11）。

    題目只印日文原文，學習者自己翻；中文只有每課的範文（讀物）才有。這兩欄
    留空是規格，不是待辦——別再有人「順手補上」。
    """
    item = item_for(1, _hit("aozora:000001:s0001", "本を読みます。"), [])
    assert item["chinese"] == ""
    assert item["chineseSource"] == ""
    assert item["kind"] == "quoted"
    assert item["text"] == "本を読みます。"


def test_anchor_note_is_blank_when_three_quotations_were_found():
    assert anchor_note(3) == ""
    assert anchor_note(5) == ""


def test_anchor_note_says_so_when_no_quotation_exists():
    """定錨不足不放寬詞表硬湊，改由自撰題補滿十題，並在該課註明。"""
    assert anchor_note(0) == "本課無可用經典原句"
    assert "2 題" in anchor_note(1)
