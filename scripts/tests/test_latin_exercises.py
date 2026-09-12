# -*- coding: utf-8 -*-
"""教會拉丁文一課十題：正規化、附著詞、驗證判定、涵蓋計算的純函式測試。

這批測試釘的是拉丁特有的幾個坑，尤其是**假拆詞**：`itaque` 不是 `ita` ＋ `que`，
而 `armaque` 是 `arma` ＋ `que`，兩者結尾一模一樣。靠字尾規則一定會錯，只能問詞典。
希伯來版踩過的是反過來的坑（maqqef 連寫沒拆，整批正確句子被誤判）。
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_latin_lemma_corpus import (  # noqa: E402
    bridge_spelling,
    clause_pieces,
    comma_pieces,
    cumulative_vocabulary,
    fold,
    split_enclitic,
    tokenise,
    vocabulary_key_order,
    vocabulary_keys,
    VocabEntry,
)
from compose_latin_sentences import (  # noqa: E402
    MAX_WORDS,
    MIN_WORDS,
    part_is_taught,
    practised,
    verify,
    word_reading,
)
from build_latin_exercises import (  # noqa: E402
    Unit,
    first_taught_index,
    looks_like_apparatus,
    part_available,
    printable_reason,
)


# ---------------------------------------------------------------------------
# 正規化：只用於比對，不用於列印
# ---------------------------------------------------------------------------

def test_fold_levels_ligature_j_v_macron_and_case():
    assert fold("cælum") == fold("caelum") == "caelum"
    assert fold("ejus") == fold("eius") == "eius"
    assert fold("vidit") == fold("uidit") == "uidit"
    assert fold("ōrdō") == "ordo"
    assert fold("Deus") == "deus"
    assert fold("cœlum") == "coelum"


def test_tokenise_keeps_the_original_spelling():
    """折疊只在比對時發生；印出來必須是原樣。"""
    assert tokenise("In principio creavit Deus cælum") == [
        "In", "principio", "creavit", "Deus", "cælum"
    ]


def test_tokenise_drops_html_entities_left_in_the_readings():
    """下冊讀物有十一處殘留 &lt;h&gt;ymni；不處理就會多出 lt、gt 兩個假詞。"""
    assert tokenise("dicuntur &lt;h&gt;ymni vel antiphonae") == [
        "dicuntur", "hymni", "vel", "antiphonae"
    ]


# ---------------------------------------------------------------------------
# 附著詞：本檔最重要的一條
# ---------------------------------------------------------------------------

# 一份小詞典就夠判：真正的詞在裡面，拼出來的宿主也在裡面。
LEXICON = {
    "itaque", "neque", "namque", "quisque", "denique", "atque", "utique",
    "usque", "ubique", "quoque", "cumque", "nonne", "bene", "sane", "omnis",
    "ita", "nam", "quis", "arma", "populus", "dixit", "factum", "que", "ne",
    "omne", "sive", "nomine",
}


def test_itaque_is_never_split_into_ita_plus_que():
    """🚨 假拆詞。`ita` 在詞典裡、`itaque` 結尾是 que，規則型拆詞一定拆錯。

    itaque 是「所以」，ita ＋ que 是「而且如此」——拆了以後句意變了，而三道閘
    全都會放行，因為兩半都是真詞也都教過。這是看起來成功的失敗。
    """
    assert split_enclitic("itaque", LEXICON) is None


def test_other_whole_words_ending_in_an_enclitic_are_left_alone():
    for word in ("neque", "namque", "quisque", "denique", "atque", "utique",
                 "usque", "ubique", "quoque", "cumque", "nonne"):
        assert split_enclitic(word, LEXICON) is None, word


def test_real_enclitics_are_split():
    assert split_enclitic("armaque", LEXICON) == ("arma", "que")
    assert split_enclitic("populusque", LEXICON) == ("populus", "que")
    assert split_enclitic("dixitque", LEXICON) == ("dixit", "que")
    assert split_enclitic("factumque", LEXICON) == ("factum", "que")


def test_words_merely_ending_in_ne_or_ve_are_not_split():
    """-ne 與 -ve 的誤拆風險比 -que 高得多：bene、omne、sive 都不是主詞＋附著詞。"""
    for word in ("bene", "omne", "sive", "sane", "nomine"):
        assert split_enclitic(word, LEXICON) is None, word


def test_a_split_needs_a_host_of_at_least_two_letters():
    """`ne` 本身結尾是 ne，宿主會是空字串；`ave` 的宿主 `a` 也太短。"""
    assert split_enclitic("ne", LEXICON) is None
    assert split_enclitic("ave", LEXICON | {"a"}) is None


def test_split_is_case_and_orthography_insensitive():
    assert split_enclitic("Armaque", LEXICON) == ("arma", "que")
    assert split_enclitic("Dixítque", LEXICON) == ("dixit", "que")


def test_whole_may_be_wider_than_attested():
    """語料沒印過 itaque，不表示可以把它拆開——判「是不是詞」要看整本詞典。"""
    corpus = {"ita", "que", "arma"}
    assert split_enclitic("itaque", corpus) == ("ita", "que")  # 只看語料會拆錯
    assert split_enclitic("itaque", corpus, whole=corpus | {"itaque"}) is None
    assert split_enclitic("armaque", corpus, whole=corpus | {"itaque"}) == ("arma", "que")


def test_unknown_word_is_not_forced_into_a_split():
    assert split_enclitic("psalmicus", LEXICON) is None


# ---------------------------------------------------------------------------
# 切句與拼字橋
# ---------------------------------------------------------------------------

def test_clause_pieces_cuts_only_at_strong_stops():
    text = "Dixitque Deus: Fiat lux. Et facta est lux."
    assert clause_pieces(text) == ["Dixitque Deus", "Fiat lux", "Et facta est lux"]


def test_clause_pieces_strips_stray_quotation_marks():
    assert clause_pieces('"Quaero vultum tuum.') == ["Quaero vultum tuum"]


def test_comma_pieces_is_the_fallback_cut():
    assert comma_pieces("Terra autem erat inanis et vacua, et tenebræ erant") == [
        "Terra autem erat inanis et vacua", "et tenebræ erant"
    ]


def test_bridge_only_lands_on_a_word_already_in_the_table():
    table = {"caelum": "caelum", "mihi": "ego"}
    assert bridge_spelling("celum", table) == "caelum"
    assert bridge_spelling("michi", table) == "ego"
    assert bridge_spelling("zzzque", table) is None


# ---------------------------------------------------------------------------
# 詞表
# ---------------------------------------------------------------------------

def test_vocabulary_keys_folds_headword_and_principal_parts():
    keys = vocabulary_keys({"headword": "ōrdō", "forms": "ōrdō, ōrdinis, m."})
    assert "ordo" in keys and "ordinis" in keys


def test_vocabulary_keys_covers_a_phrase_entry():
    keys = vocabulary_keys({"headword": "grātiās agere", "forms": "grātiās agere"})
    assert keys == {"gratias", "agere"}


def test_vocabulary_keys_drops_the_leading_hyphen_of_an_enclitic():
    assert vocabulary_keys({"headword": "-que", "forms": "-que"}) == {"que"}


def make_entry(volume, lesson, ordinal, headword, lemmas, keys=None):
    row = {
        "volume": "上冊" if volume == 1 else "下冊",
        "lesson": lesson,
        "ordinal": ordinal,
        "headword": headword,
        "forms": headword,
        "glossZh": "",
    }
    return VocabEntry(row, set(lemmas), set(keys or {fold(headword)}))


def test_cumulative_vocabulary_carries_the_upper_volume_into_the_lower():
    entries = [
        make_entry(1, 1, 1, "et", {"et"}),
        make_entry(1, 50, 2, "hostis", {"hostis"}),
        make_entry(2, 1, 3, "que", {"que"}),
        make_entry(2, 9, 4, "campus", {"campus"}),
    ]
    targets, lemmas, _ = cumulative_vocabulary(entries, volume=2, lesson=1)
    assert [entry.headword for entry in targets] == ["que"]
    assert lemmas == {"et", "hostis", "que"}
    assert "campus" not in lemmas


def test_cumulative_vocabulary_does_not_look_ahead_inside_a_volume():
    entries = [make_entry(1, 1, 1, "et", {"et"}), make_entry(1, 2, 2, "liber", {"liber"})]
    _, lemmas, _ = cumulative_vocabulary(entries, volume=1, lesson=1)
    assert lemmas == {"et"}


def test_an_entry_with_no_treebank_lemma_says_so():
    """Kyrie、eléison、片語這類四十七條對不上詞位，必須標出來而不是當成已涵蓋。"""
    entry = make_entry(1, 16, 300, "Kyrie", set())
    assert entry.resolved is False
    assert entry.public_record()["lemmas"] == []


# ---------------------------------------------------------------------------
# 驗證判定
# ---------------------------------------------------------------------------

class FakeCorpus:
    """只有六個詞的語料，夠測三道閘。"""

    FORMS = {
        "deus": {"surfaces": ["Deus"], "lemmas": ["deus"]},
        "est": {"surfaces": ["est"], "lemmas": ["sum"]},
        "in": {"surfaces": ["in"], "lemmas": ["in"]},
        "caelo": {"surfaces": ["cælo"], "lemmas": ["caelum"]},
        "populus": {"surfaces": ["populus"], "lemmas": ["populus"]},
        "arma": {"surfaces": ["arma"], "lemmas": ["arma"]},
        "ita": {"surfaces": ["ita"], "lemmas": ["ita"]},
        "itaque": {"surfaces": ["itaque"], "lemmas": ["itaque"]},
        "misit": {"surfaces": ["misit"], "lemmas": ["mitto"]},
        "missa": {"surfaces": ["missa"], "lemmas": ["missa", "mitto"]},
        "terram": {"surfaces": ["terram"], "lemmas": ["terra"]},
        "angelum": {"surfaces": ["angelum"], "lemmas": ["angelus"]},
        "angelus": {"surfaces": ["Angelus"], "lemmas": ["Angelus", "angelus"]},
        "que": {"surfaces": ["que"], "lemmas": ["que"]},
        # 語料裡有這個形、詞位欄卻是空的——武加大有九萬多個 token 是這樣，
        # 詞位與字形兩條路都到不了，只剩詞幹那一條。
        "annuntiauit": {"surfaces": ["annuntiavit"], "lemmas": []},
    }

    names = ["fake"]

    @property
    def keys(self):
        return set(self.FORMS)

    def attested(self, key):
        return key in self.FORMS

    def spelling(self, key):
        row = self.FORMS.get(key)
        return row["surfaces"][0] if row else ""

    def lemmas(self, key):
        row = self.FORMS.get(key)
        return set(row["lemmas"]) if row else set()


class FakeTagger:
    attested = set(FakeCorpus.FORMS) | {"itaque"}

    def lemmas_for_key(self, key):
        return set(FakeCorpus.FORMS.get(key, {}).get("lemmas", ()))


CORPUS = FakeCorpus()
TAGGER = FakeTagger()
TAUGHT_LEMMAS = {"deus", "sum", "in", "caelum", "populus", "que"}
TAUGHT_KEYS = {"deus", "est", "in", "caelo", "populus", "que"}


def test_verify_passes_a_sentence_whose_words_are_all_attested_and_taught():
    report = verify("Deus est in cælo", CORPUS, TAGGER, TAUGHT_LEMMAS, TAUGHT_KEYS)
    assert report["passed"] is True
    assert report["unattested"] == [] and report["untaught"] == []


def test_verify_reports_an_invented_form_with_its_original_spelling():
    report = verify("Psalmicus est Deus", CORPUS, TAGGER, TAUGHT_LEMMAS, TAUGHT_KEYS)
    assert report["unattested"] == ["Psalmicus"]
    assert report["passed"] is False


def test_verify_rejects_a_taught_check_that_the_enclitic_would_otherwise_pass():
    """🚨 -que 第一課就教了。若把主詞和附著詞併在一起判，任何名詞黏上 que 都會過關。"""
    report = verify("Armaque Deus est", CORPUS, TAGGER, TAUGHT_LEMMAS, TAUGHT_KEYS)
    assert report["untaught"] == ["Armaque"]
    assert report["passed"] is False


def test_verify_accepts_a_real_enclitic_whose_host_has_been_taught():
    report = verify("Populusque Deus est", CORPUS, TAGGER, TAUGHT_LEMMAS, TAUGHT_KEYS)
    assert report["untaught"] == []
    assert report["enclitics"] == [{"word": "Populusque", "enclitic": "que"}]
    assert report["passed"] is True


def test_verify_does_not_split_itaque_and_so_calls_it_untaught():
    """語料裡有 itaque、`ita` 和 `que` 也都教過，但 itaque 本身沒教過就是沒教過。

    這句若被拆成 ita ＋ que，兩半都教過，整句會過關——過的是一句不存在的話。
    """
    report = verify("Itaque Deus est", CORPUS, TAGGER, TAUGHT_LEMMAS, TAUGHT_KEYS)
    assert report["untaught"] == ["Itaque"]
    assert report["enclitics"] == []
    assert report["passed"] is False


def test_verify_enforces_the_length_rule():
    short = verify("Deus est", CORPUS, TAGGER, TAUGHT_LEMMAS, TAUGHT_KEYS)
    assert short["lengthOk"] is False and short["passed"] is False
    assert MIN_WORDS == 3 and MAX_WORDS == 8


def test_word_reading_returns_two_parts_for_an_enclitic():
    row = word_reading("Populusque", CORPUS, TAGGER)
    assert [part["key"] for part in row["parts"]] == ["populus", "que"]


def test_part_is_taught_accepts_either_the_lemma_or_the_written_form():
    by_lemma = {"key": "zzz", "lemmas": {"deus"}}
    by_form = {"key": "caelo", "lemmas": set()}
    neither = {"key": "zzz", "lemmas": {"hostis"}}
    assert part_is_taught(by_lemma, TAUGHT_LEMMAS, TAUGHT_KEYS) is True
    assert part_is_taught(by_form, TAUGHT_LEMMAS, TAUGHT_KEYS) is True
    assert part_is_taught(neither, TAUGHT_LEMMAS, TAUGHT_KEYS) is False


# ---------------------------------------------------------------------------
# 涵蓋計算
# ---------------------------------------------------------------------------

def target(ordinal, *, lemmas=frozenset(), keys=frozenset(), stems=frozenset(), phrase=False):
    """A coverage target with all three credit routes stated explicitly.

    ``practised`` asks for the lemma, then the written form, then the stem, so a
    fake that only carries the first two silently exercises a different function
    from the one the reader calls.
    """
    return SimpleNamespace(
        ordinal=ordinal,
        credit_lemmas=set(lemmas),
        credit_keys=set(keys),
        written_keys=set(keys),
        credit_stems=set(stems),
        phrase=phrase,
    )


def test_practised_counts_a_word_reached_through_an_inflected_form():
    hits = practised(["Deus est in cælo"], [target(1, lemmas={"caelum"})], CORPUS, TAGGER)
    assert hits[1] == ["caelum"]


def test_practised_falls_back_to_the_written_form_for_an_unresolved_entry():
    hits = practised(["Deus est ita"], [target(2, keys={"ita"})], CORPUS, TAGGER)
    assert hits[2] == ["ita"]


def test_practised_leaves_out_a_word_no_sentence_used():
    assert practised(["Deus est in cælo"], [target(3, lemmas={"hostis"})], CORPUS, TAGGER) == {}


def test_practised_reaches_an_unlemmatised_word_through_a_long_enough_stem():
    """🚨 第三條路線。語料裡 annuntiavit 這個形沒有詞位，詞位與字形兩條路都到不了，
    只剩詞幹。九十一個詞卡在這裡，而「本課二十詞全數入題」對它們永遠不可能成立。"""
    hits = practised(
        ["annuntiavit Deus"], [target(4, stems={"annunti"})], CORPUS, TAGGER
    )
    assert hits[4] == ["annuntiauit"]


def test_a_short_word_gets_no_stem_route_at_all():
    """🚨 詞幹長度下限就是為了這一格：missa 的五字母詞幹會把別的詞算成練到。

    `credit_stems` 在 VocabEntry 那邊就已經把不足六字母的濾掉，這裡釘的是
    `practised` 不會自己補一條——給空的詞幹集合，就真的一條都不走。"""
    assert practised(["missus est Deus"], [target(5, stems=set())], CORPUS, TAGGER) == {}


def entry_with_lemmas(headword, lemmas, forms=None, lesson=2, ordinal=90):
    row = {
        "volume": "上冊", "lesson": lesson, "ordinal": ordinal,
        "headword": headword, "forms": forms or headword, "glossZh": "",
    }
    return VocabEntry(row, set(lemmas), vocabulary_keys(row))


def test_missa_is_not_practised_by_a_participle_of_mitto():
    """🚨 同形異詞，拉丁版。`missa` 既是彌撒，也是 mitto 的陰性完成分詞。

    查形表會把兩個詞位都掛到「彌撒」這條詞上，於是「他差遣了」一句
    `et misit in terram` 就把彌撒記成練到了——閘全綠，帳是錯的。
    希伯來版踩的是同一個坑：撒上 4:18 的形容詞 H3515 被當成動詞 H3513。
    """
    missa = entry_with_lemmas("missa", {"missa", "mitto"}, "missa, missae, f.")
    assert missa.credit_lemmas == {"missa"}
    assert practised(["et misit in terram"], [missa], CORPUS, TAGGER) == {}
    assert practised(["missa est"], [missa], CORPUS, TAGGER) == {90: ["missa"]}


def test_case_variants_of_the_same_word_still_count():
    """🚨 反例，不可一併擋掉：`Angelus`→`angelus` 折疊後相等，是同一個詞。"""
    angelus = entry_with_lemmas("angelus", {"Angelus", "angelus"}, "angelus, angelī, m.")
    assert angelus.credit_lemmas == {"Angelus", "angelus"}
    assert practised(["misit angelum"], [angelus], CORPUS, TAGGER) == {90: ["angelus"]}


def test_a_proper_name_variant_does_not_credit_the_common_noun():
    """`festum`（慶節）不該被人名 `Festus`（非斯都）記到。"""
    festum = entry_with_lemmas("festum", {"Festus", "festum", "festus"}, "festum, festī, n.")
    assert festum.credit_lemmas == {"festum"}


def test_a_derived_word_does_not_credit_its_root():
    """`praeceptum`（誡命）不該被動詞 `praecipio` 記到；`nōn` 不該被 `nonnullus` 記到。"""
    assert entry_with_lemmas(
        "praeceptum", {"praeceptum", "praecipio"}).credit_lemmas == {"praeceptum"}
    assert entry_with_lemmas(
        "nōn", {"non", "nonnihil", "nonnullus"}).credit_lemmas == {"non"}


def test_the_form_route_is_closed_once_a_lemma_fits():
    """詞位對得上就只走詞位；形表那條路只留給對不上詞位的詞條。"""
    missa = entry_with_lemmas("missa", {"missa", "mitto"}, "missa, missae, f.")
    assert missa.credit_keys == set()
    electus = entry_with_lemmas("ēlēctus", {"eligo"}, "ēlēctus, -a, -um")
    assert electus.credit_lemmas == set()
    assert electus.credit_keys == {"electus"}


def test_vocabulary_keys_drops_endings_and_gender_abbreviations():
    """🚨 `ēlēctus, -a, -um` 的 -a 讓詞條解到 `ad`／`hic`，`f.` 讓 liturgia 解到詞位 `f`。"""
    assert vocabulary_keys({"headword": "ēlēctus", "forms": "ēlēctus, -a, -um"}) == {"electus"}
    assert vocabulary_keys(
        {"headword": "liturgia", "forms": "liturgia, liturgiae, f."}
    ) == {"liturgia", "liturgiae"}
    assert vocabulary_keys(
        {"headword": "piāculum", "forms": "piāculum, piāculī, n."}
    ) == {"piaculum", "piaculi"}


def test_vocabulary_keys_still_keeps_a_one_letter_headword():
    assert vocabulary_keys({"headword": "ā", "forms": "ā (ab, abs)"}) == {"a", "ab", "abs"}


def test_a_phrase_entry_is_practised_only_when_all_of_it_appears():
    """🚨 `in saecula` 若可由單一個 `in` 記成已練，二十詞涵蓋這道閘就形同虛設。"""
    phrase = SimpleNamespace(
        ordinal=6, credit_lemmas=set(), credit_keys={"in", "caelo"}, phrase=True
    )
    assert practised(["Deus est in cælo"], [phrase], CORPUS, TAGGER) == {6: ["caelo", "in"]}
    assert practised(["Deus est in arma"], [phrase], CORPUS, TAGGER) == {}


def test_a_phrase_entry_carries_no_lemma_of_its_own():
    entry = VocabEntry(
        {"volume": "上冊", "lesson": 4, "ordinal": 70, "headword": "in saecula",
         "forms": "in saecula", "glossZh": ""},
        {"in"}, {"in", "saecula"},
    )
    assert entry.phrase is True
    assert entry.lemmas == set() and entry.resolved is False


def test_practised_credits_the_host_of_an_enclitic_not_only_the_enclitic():
    targets = [
        SimpleNamespace(ordinal=4, credit_lemmas={"populus"}, credit_keys=set()),
        SimpleNamespace(ordinal=5, credit_lemmas={"que"}, credit_keys=set()),
    ]
    hits = practised(["Populusque Deus est"], targets, CORPUS, TAGGER)
    assert set(hits) == {4, 5}


# ---------------------------------------------------------------------------
# 挖句器
# ---------------------------------------------------------------------------

def make_unit(text, kind="clause", verse=1):
    words = tuple(tokenise(text))
    return Unit(
        uid="X.1.1#1", ref="X.1.1", source="X.1.1", kind=kind, part=1, part_count=2,
        text=text, words=words, book="X", chapter=1, verse=verse, lesson=0,
    )


def test_printable_rejects_a_prepositional_phrase_with_no_verb():
    """🚨 逗號切出來的「et ad Saram」每個詞都教過、長度也合格，但那不是句子。"""
    unit = make_unit("et ad Saram")
    reason = printable_reason(unit, [frozenset(), frozenset(), frozenset()],
                              [False, False, True], [False, False, False])
    assert reason == "無謂語"


def test_printable_accepts_a_clause_with_a_verb():
    unit = make_unit("Et misit Dominus angelum")
    assert printable_reason(
        unit,
        [frozenset({"et"}), frozenset({"mitto"}), frozenset({"dominus"}), frozenset({"angelus"})],
        [False, False, False, False],
        [False, True, False, False],
    ) is None


def test_printable_rejects_a_list_of_names():
    unit = make_unit("Abraham genuit Isaac Iacob")
    reason = printable_reason(
        unit,
        [frozenset({"Abraham"}), frozenset({"gigno"}), frozenset({"Isaac"}), frozenset({"Iacob"})],
        [True, False, True, True],
        [False, True, False, False],
    )
    assert reason == "專名列舉"


def test_printable_rejects_a_fragment_that_is_too_short_or_too_long():
    assert printable_reason(make_unit("Deus est"), [frozenset()] * 2,
                            [False] * 2, [False, True]) == "長度不合"
    long_text = " ".join(["verbum"] * 9)
    assert printable_reason(make_unit(long_text), [frozenset()] * 9,
                            [False] * 9, [True] * 9) == "長度不合"


def test_printable_rejects_leftover_editorial_brackets():
    unit = make_unit("dicuntur &lt;h&gt;ymni vel antiphonae")
    reason = printable_reason(unit, [frozenset()] * 4, [False] * 4, [True, False, False, False])
    assert reason == "含校勘符號"


def test_looks_like_apparatus():
    assert looks_like_apparatus("ex ratione quo+&gt;") is True
    assert looks_like_apparatus("In principio creavit Deus") is False


def test_first_taught_index_takes_the_earliest_lesson_and_frees_the_appendix():
    entries = [
        make_entry(1, 3, 1, "caelum", {"caelum"}, {"caelum"}),
        make_entry(2, 4, 2, "caelum", {"caelum"}, {"caelum"}),
    ]
    lemma_first, key_first, lemma_entries, _ = first_taught_index(entries, {"abraham"})
    assert lemma_first["caelum"] == (1, 3)
    assert key_first["abraham"] == (0, 0)
    assert lemma_entries["caelum"] == {(1, 1), (2, 2)}


def test_part_available_prefers_whichever_route_comes_first():
    lemma_first = {"caelum": (1, 3)}
    key_first = {"caelo": (2, 7)}
    assert part_available({"key": "caelo", "lemmas": {"caelum"}}, lemma_first, key_first) == (1, 3)


def test_part_available_reports_a_word_no_lesson_teaches():
    assert part_available({"key": "zzz", "lemmas": {"zzz"}}, {}, {}) == (99, 99)
