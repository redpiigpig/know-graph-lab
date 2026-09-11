# -*- coding: utf-8 -*-
"""通用希臘文練習題三支腳本的純函式測試。

跑的全是不碰檔案、不碰網路的函式：正規化、拆詞、三層詞位解析的層序、
三道閘的判定、涵蓋計算。語料索引用手寫的幾個 token 現場組，
不讀 35 MB 的 lemma-corpus。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_greek_lemma_corpus import (  # noqa: E402
    CANONICAL_APOSTROPHE,
    LAYER_KOINE_EXACT,
    LAYER_KOINE_FOLDED,
    LAYER_MORPHEUS,
    LAYER_SURFACE,
    Lemmatizer,
    bare,
    crasis_components,
    fold_key,
    is_word,
    split_sentences,
    split_words,
    unify_apostrophes,
)
from build_greek_exercises import (  # noqa: E402
    CorpusUnit,
    VocabItem,
    printable_reason,
    split_clauses,
)
from compose_greek_sentences import (  # noqa: E402
    Attestation,
    coverage_report,
    review,
    verify_sentence,
)

# 五種省音號寫法，本 repo 的各份語料裡全都出現過。
KORONIS = "᾽"      # ᾽ Swete 用這個
PSILI = "᾿"        # ᾿ 教父那批用過這個
OXIA = "´"         # ´ 被當省音號誤用
CURLY = "’"        # ’ koine-lexicon 用這個
ASCII_QUOTE = "'"  # ' 教父那批也用過這個


# --------------------------------------------------------------------------
# 正規化
# --------------------------------------------------------------------------

def test_unify_apostrophes_folds_all_five_spellings():
    """🚨 Swete 用 U+1FBD 寫了 5,061 處省音，詞典是拿 U+2019 建的。

    不統一，那 5,061 個 καθ᾽／δι᾽ 一個都查不到，會整批靜默落到最後一層。
    """
    for mark in (KORONIS, PSILI, OXIA, CURLY, ASCII_QUOTE):
        assert unify_apostrophes("καθ" + mark) == "καθ" + CANONICAL_APOSTROPHE


def test_unify_apostrophes_touches_nothing_else():
    assert unify_apostrophes("ψυχῇ, υἱός·") == "ψυχῇ, υἱός·"


def test_bare_keeps_accents_and_drops_punctuation():
    assert bare("θεὸς·") == "θεὸς"
    assert bare("Ἀβραάμ.") == "Ἀβραάμ"


def test_bare_drops_editorial_sigla_but_keeps_the_letters():
    """Swete 的方括號是補字，字要留；SBLGNT 的 ⸀ 是異文記號，不是詞的一部分。"""
    assert bare("πετόμεν[α]") == "πετόμενα"
    assert bare("⸀ἀντέστη") == "ἀντέστη"


def test_fold_key_is_accent_breathing_case_and_sigma_insensitive():
    assert fold_key("ΑΡΧΗ") == fold_key("ἀρχή") == "αρχη"
    assert fold_key("υἱός") == fold_key("υἱοσ")
    assert fold_key("ψυχῇ") == "ψυχη"          # 下標 iota 折掉
    assert fold_key("ἐξ") == fold_key("ἕξ")     # 氣號折掉——所以折疊那層不夠用


def test_is_word_rejects_pure_sigla_and_footnote_numbers():
    assert is_word("θεός")
    assert not is_word("⸂⸆⸃")
    assert not is_word("[1]")
    assert not is_word(",")


def test_split_words_keeps_elided_forms_whole():
    got = split_words("καθ" + KORONIS + " ἡμέραν, ⸂⸆⸃ [3]")
    assert got == ["καθ" + CANONICAL_APOSTROPHE, "ἡμέραν"]


def test_split_sentences_does_not_split_on_ano_teleia():
    """· 做的是分號的事，不是句末。切在它上面得到的是例外子句不是句子。"""
    assert split_sentences("ἦλθεν ὁ υἱός· καὶ εἶδεν. ἀπῆλθεν.") == [
        "ἦλθεν ὁ υἱός· καὶ εἶδεν.",
        "ἀπῆλθεν.",
    ]


def test_crasis_components_splits_what_is_written_as_one_word():
    """🚨 κἀγώ 是 καί ＋ ἐγώ 寫成一個詞——希伯來 maqqef 連寫那個坑的希臘版。"""
    assert crasis_components("κἀγὼ") == ("καί", "ἐγώ")
    assert crasis_components("κἀκείνους") == ("καί", "ἐκεῖνος")
    assert crasis_components("λέγω") == ()


# --------------------------------------------------------------------------
# 三層詞位解析
# --------------------------------------------------------------------------

def tiny_lemmatizer() -> Lemmatizer:
    koine = {
        "exactForms": {"ἐξ": ["ἐκ"], "ἕξ": ["ἕξ"]},
        "forms": {"εξ": ["ἐκ"], "καθ" + CANONICAL_APOSTROPHE: ["κατά"], "λογοσ": ["λόγος"]},
    }
    morpheus = {"forms": {"εγενετο": ["γίγνομαι"]}}
    return Lemmatizer(koine, morpheus)


def test_exact_layer_separates_words_that_folding_merges():
    """ἐξ（從）與 ἕξ（六）折疊後同形；氣號就是整個詞，所以重音敏感那層要先查。"""
    lemmatizer = tiny_lemmatizer()
    assert lemmatizer.candidates("ἐξ") == (["ἐκ"], LAYER_KOINE_EXACT)
    assert lemmatizer.candidates("ἕξ") == (["ἕξ"], LAYER_KOINE_EXACT)


def test_folded_layer_answers_when_the_exact_spelling_is_absent():
    lemmatizer = tiny_lemmatizer()
    assert lemmatizer.candidates("Λόγος") == (["λόγος"], LAYER_KOINE_FOLDED)


def test_elision_resolves_only_after_the_apostrophes_are_unified():
    lemmatizer = tiny_lemmatizer()
    assert lemmatizer.candidates("καθ" + KORONIS) == (["κατά"], LAYER_KOINE_FOLDED)
    assert lemmatizer.candidates("καθ" + ASCII_QUOTE) == (["κατά"], LAYER_KOINE_FOLDED)


def test_morpheus_is_last_before_giving_up_and_is_labelled():
    """⚠️ Morpheus 是雅典方言優先：ἐγένετο 它答 γίγνομαι，不是讀本要教的 γίνομαι。"""
    lemmatizer = tiny_lemmatizer()
    assert lemmatizer.candidates("ἐγένετο") == (["γίγνομαι"], LAYER_MORPHEUS)


def test_unresolved_form_falls_through_to_the_folded_surface():
    lemmatizer = tiny_lemmatizer()
    lemmas, layer = lemmatizer.candidates("θεοτόκος")
    assert (lemmas, layer) == (["θεοτοκοσ"], LAYER_SURFACE)


def test_resolve_counts_each_layer():
    lemmatizer = tiny_lemmatizer()
    for word in ("ἐξ", "Λόγος", "θεοτόκος"):
        lemmatizer.resolve(word)
    assert lemmatizer.counts[LAYER_KOINE_EXACT] == 1
    assert lemmatizer.counts[LAYER_KOINE_FOLDED] == 1
    assert lemmatizer.counts[LAYER_SURFACE] == 1


# --------------------------------------------------------------------------
# 語料證據與三道閘
# --------------------------------------------------------------------------

def unit(ref: str, text: str, pairs) -> CorpusUnit:
    return CorpusUnit(
        ref=ref,
        corpus="test",
        source="test",
        book="Test",
        text=text,
        tokens=tuple((form, lemma, LAYER_KOINE_EXACT) for form, lemma in pairs),
    )


CORPUS = [
    unit(
        "Test.1.1",
        "καὶ εἶπεν ὁ θεὸς τῷ υἱῷ αὐτοῦ·",
        [("καὶ", "καί"), ("εἶπεν", "λέγω"), ("ὁ", "ὁ"), ("θεὸς", "θεός"),
         ("τῷ", "ὁ"), ("υἱῷ", "υἱός"), ("αὐτοῦ", "αὐτός")],
    ),
    unit(
        "Test.1.2",
        "κἀγὼ λέγω ὑμῖν.",
        [("κἀγὼ", "κἀγώ"), ("λέγω", "λέγω"), ("ὑμῖν", "σύ")],
    ),
]
KNOWN = {fold_key(lemma) for row in CORPUS for _, lemma, _ in row.tokens if lemma != "κἀγώ"}
ATTESTED = Attestation.from_units(CORPUS)


def test_gate_one_rejects_a_form_the_corpus_never_wrote():
    report = verify_sentence("ὁ θεὸς ἐλαλησκεν αὐτοῦ", KNOWN, ATTESTED)
    assert report["unattested"] == ["ἐλαλησκεν"]
    assert report["passed"] is False


def test_gate_two_rejects_a_word_that_has_not_been_taught_yet():
    report = verify_sentence("καὶ εἶπεν ὁ θεὸς", KNOWN - {fold_key("θεός")}, ATTESTED)
    assert report["untaught"] == ["θεὸς"]
    assert report["passed"] is False


def test_a_sentence_of_taught_attested_words_passes():
    report = verify_sentence("καὶ εἶπεν ὁ θεὸς", KNOWN, ATTESTED)
    assert (report["unattested"], report["untaught"]) == ([], [])
    assert report["passed"] is True


def test_crasis_passes_when_both_halves_have_been_taught():
    """κἀγώ 本身不在詞表裡，但 καί 與 ἐγώ 都教過了——不拆就會被誤判成沒教過。"""
    known = KNOWN | {fold_key("ἐγώ")}
    report = verify_sentence("κἀγὼ λέγω ὑμῖν.", known, ATTESTED)
    assert report["untaught"] == []
    assert report["passed"] is True


def test_accent_only_difference_is_flagged_not_silently_accepted():
    report = verify_sentence("καὶ ειπεν ὁ θεὸς", KNOWN, ATTESTED)
    assert report["accentVariants"] == ["ειπεν"]
    assert report["passed"] is True


def test_two_words_is_too_short_to_pass():
    assert verify_sentence("ὁ θεὸς", KNOWN, ATTESTED)["passed"] is False


def item(slot: int, lemma: str) -> VocabItem:
    return VocabItem(
        volume=1, lesson=1, slot=slot, ordinal=slot,
        headword=lemma, lemma=lemma, gloss_zh="", pos="",
    )


def test_gate_three_counts_coverage_and_names_what_is_missing():
    items = [item(1, "θεός"), item(2, "λέγω"), item(3, "ἱμάτιον")]
    reports = [verify_sentence("καὶ εἶπεν ὁ θεὸς", KNOWN, ATTESTED)]
    coverage = coverage_report(items, reports)
    assert coverage["practised"] == 2
    assert [row["headword"] for row in coverage["notPractised"]] == ["ἱμάτιον"]
    assert coverage["passed"] is False


def test_gate_three_passes_only_when_nothing_is_left_over():
    items = [item(1, "θεός"), item(2, "λέγω")]
    reports = [verify_sentence("καὶ εἶπεν ὁ θεὸς", KNOWN, ATTESTED)]
    assert coverage_report(items, reports)["passed"] is True


# --------------------------------------------------------------------------
# 🚨 正規化不可污染印出的原文
# --------------------------------------------------------------------------

RAW = "ΕΝ ἀρχῇ καθ" + KORONIS + " ὁ υἱός·"


def test_normalisation_never_reaches_the_printed_text():
    """🚨 正規化只用於比對。寫進 JSON 的 `greek` 必須與作者寫的**一字元不差**。

    大寫沒被小寫化、U+1FBD 沒被換成 U+2019、下標 iota 還在、詞尾 ς 還是 ς、
    句末的 · 還在。這條錯了，印出來的就是一句原文沒有的話。
    """
    result = review(
        volume=1,
        lesson=1,
        payload={"sentences": [{"greek": RAW, "chinese": "中文"}]},
        lesson_items=[],
        known=KNOWN,
        attestation=ATTESTED,
    )
    printed = result["sentences"][0]["greek"]
    assert printed == RAW
    assert printed is RAW  # 連同一個字串物件都沒被換掉
    assert KORONIS in printed and "ῇ" in printed and "ς·" in printed
    assert printed.startswith("ΕΝ")


def test_rejected_words_are_reported_as_written_not_as_folded():
    """退回訊息裡印的也必須是原樣，否則作者看到的是機器的內部形。"""
    report = verify_sentence("ΕΝ ἀρχῇ καθ" + KORONIS, KNOWN, ATTESTED)
    assert report["unattested"] == ["ΕΝ", "ἀρχῇ", "καθ" + CANONICAL_APOSTROPHE]


# --------------------------------------------------------------------------
# 切子句與可印性
# --------------------------------------------------------------------------

def test_split_clauses_keeps_the_printed_text_exact():
    source = unit(
        "Test.2.1",
        "καὶ εἶπεν ὁ θεὸς· τῷ υἱῷ αὐτοῦ.",
        [("καὶ", "καί"), ("εἶπεν", "λέγω"), ("ὁ", "ὁ"), ("θεὸς", "θεός"),
         ("τῷ", "ὁ"), ("υἱῷ", "υἱός"), ("αὐτοῦ", "αὐτός")],
    )
    clauses = split_clauses(source)
    assert [row.text for row in clauses] == ["καὶ εἶπεν ὁ θεὸς·", "τῷ υἱῷ αὐτοῦ."]
    assert "".join(row.text for row in clauses).replace(" ", "") == source.text.replace(" ", "")
    assert [row.word_count for row in clauses] == [4, 3]


def test_split_clauses_gives_up_rather_than_print_a_mismatched_clause():
    """詞數與 token 數對不齊就整個不切：寧可少一個候選，也不要印出湊出來的句子。"""
    broken = unit(
        "Test.2.2",
        "καὶ εἶπεν ὁ θεὸς· τῷ υἱῷ αὐτοῦ.",
        [("καὶ", "καί"), ("εἶπεν", "λέγω")],
    )
    assert split_clauses(broken) == []


def test_printable_reason_rejects_a_clause_that_stops_on_a_comma():
    """🚨 詩歌體一行一句印。停在逗號的是半句，主要動詞在上一行。"""
    hymn = unit(
        "Test.3.1",
        "καὶ Δεσπότην νοοῦντες αὐτόν,",
        [("καὶ", "καί"), ("Δεσπότην", "δεσπότης"), ("νοοῦντες", "νοέω"), ("αὐτόν", "αὐτός")],
    )
    assert printable_reason(hymn) == "沒有停在原文的停頓上"


def test_printable_reason_accepts_a_clause_that_stops_on_an_ano_teleia():
    good = unit(
        "Test.3.2",
        "καὶ εἶπεν ὁ θεὸς·",
        [("καὶ", "καί"), ("εἶπεν", "λέγω"), ("ὁ", "ὁ"), ("θεὸς", "θεός")],
    )
    assert printable_reason(good) is None


def test_printable_reason_rejects_editorial_sigla_and_footnote_numbers():
    marked = unit(
        "Test.3.3",
        "καὶ εἶπεν πετόμεν[α] θεὸς·",
        [("καὶ", "καί"), ("εἶπεν", "λέγω"), ("πετόμενα", "πέτομαι"), ("θεὸς", "θεός")],
    )
    assert printable_reason(marked) == "含校勘符號或數字"
