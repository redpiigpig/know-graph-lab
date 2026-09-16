"""國小英語課本生成器的品質閘。

這四道閘都是 2026-09-16 使用者翻紙本課本抓出來、而當時所有自動檢查都是綠的。
每一條測試對應一個真實踩到的案例，案例原文寫在測試名稱與註解裡。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gen():
    sys.path.insert(0, str(ROOT / "scripts"))
    return _load("build_english_course50", ROOT / "scripts" / "build_english_course50.py")


@pytest.fixture(scope="module")
def vocab():
    return _load("reorder_english_vocab", ROOT / "scripts" / "reorder_english_vocab.py")


# ---------------------------------------------------------------- 中英方向

def test_english_stem_asking_for_english_is_rejected(gen):
    """L03 前十題：「wink 的英文是？」——題幹已經是英文，答案寫在題目上。"""
    ex = {"mcq": [{"q": "wink 的英文是？", "opts": ["wink", "whisper", "greeting", "introduce"],
                   "ans": "wink"}]}
    errs = gen.validate_direction(ex)
    assert any("答案寫在題目上" in e for e in errs)


def test_chinese_stem_with_chinese_options_is_rejected(gen):
    """L45：「她______一名士兵。」選項是「是／不是／會／能」，整題沒有一個英文字。"""
    ex = {"mcq": [{"q": "她______一名士兵。", "opts": ["是", "不是", "會", "能"], "ans": "是"}]}
    errs = gen.validate_direction(ex)
    assert any("選項是中文" in e for e in errs)


def test_proper_direction_passes(gen):
    """正常方向：中文題幹→選英文。"""
    ex = {"mcq": [{"q": "士兵 的英文是？", "opts": ["soldier", "king", "nurse", "writer"],
                   "ans": "soldier"}]}
    assert gen.validate_direction(ex) == []


def test_translate_must_be_zh_to_en(gen):
    ex = {"translate": [{"q": "He is a policeman.", "ans": "他是一名警察。"}]}
    errs = gen.validate_direction(ex)
    assert any("題幹不是中文" in e for e in errs)
    assert any("答案不是英文" in e for e in errs)


# ---------------------------------------------------------------- 選項多樣性

def test_repeated_option_set_is_rejected(gen):
    """am/is/are/be 這一組全書出現 27 次、橫跨 5 課。一課只准出現一次。"""
    same = ["am", "is", "are", "be"]
    ex = {"mcq": [{"q": f"{s} ___ here.", "opts": same, "ans": "is"}
                  for s in ("He", "She", "It")]}
    errs = gen.validate_variety(ex)
    assert errs and "3 題共用同一組選項" in errs[0]


def test_distinct_option_sets_pass(gen):
    ex = {"mcq": [{"q": "a", "opts": ["am", "is", "are", "be"], "ans": "is"},
                  {"q": "b", "opts": ["cat", "dog", "pig", "hen"], "ans": "cat"}]}
    assert gen.validate_variety(ex) == []


# ---------------------------------------------------------------- 四區不可以考同一件事

def test_translate_and_unscramble_sharing_answers_is_rejected(gen):
    """50 課裡有 24 課兩區答案 100% 相同——同樣幾句話寫兩遍，整區白放。"""
    same = ["I am fine.", "You are sure.", "He is OK.", "She is welcome."]
    ex = {"translate": [{"q": "中文", "ans": s} for s in same],
          "unscramble": [{"q": "打散", "ans": s} for s in same]}
    errs = gen.validate_overlap(ex)
    assert any("100% 的答案是同一句" in e for e in errs)


def test_different_sentences_in_each_section_pass(gen):
    ex = {"translate": [{"q": "中文", "ans": s} for s in
                        ("I am fine.", "You are sure.", "He is OK.")],
          "unscramble": [{"q": "打散", "ans": s} for s in
                         ("We are here.", "They are happy.", "It is a cat.")]}
    assert gen.validate_overlap(ex) == []


def test_fill_with_one_repeated_answer_is_rejected(gen):
    """L43 有九題填空答案都一樣、L21 有八題。"""
    ex = {"fill": [{"q": f"q{i} ____", "ans": "is"} for i in range(9)]
                  + [{"q": "q9 ____", "ans": "are"}]}
    errs = gen.validate_overlap(ex)
    assert any("9/10 題答案都是「is」" in e for e in errs)


def test_drill_lessons_are_exempt_from_tail_variety(gen):
    """🚨 最前面幾課本來就該重複結尾。

    那幾課的 20 個字全是代名詞與招呼語，整課的重點就是操練 am／is／are。
    硬套「結尾詞要分散」的結果是模型用 Hi／OK／Hello 墊句首湊變化，
    寫出「OK She is sorry.」「Hello We are fine.」這種句中大寫的東西。
    """
    ex = {"translate": [{"q": "中文", "ans": f"{s} fine."} for s in
                        ("I am", "He is", "She is", "We are", "They are", "You are")]}
    gen.CURRENT_LESSON = 1
    try:
        assert gen.validate_overlap(ex) == []
        gen.CURRENT_LESSON = 20
        assert any("都以「fine」結尾" in e for e in gen.validate_overlap(ex))
    finally:
        gen.CURRENT_LESSON = 0


def test_translate_all_ending_in_same_word_is_rejected(gen):
    """重出的 L01 造句八題有七題是「X is fine.」，句型指紋看不出來（第二個字
    分散在 am/is/are），看結尾那個字才看得出來。"""
    ex = {"translate": [{"q": "中文", "ans": f"{s} fine."} for s in
                        ("I am", "He is", "She is", "It is", "We are",
                         "You are", "They are")]
                       + [{"q": "謝謝。", "ans": "Thank you."}]}
    errs = gen.validate_overlap(ex)
    assert any("7/8 句都以「fine」結尾" in e for e in errs)


def test_degenerate_unscramble_items_are_rejected(gen):
    """🚨 「結尾詞要分散」那道閘會被用「把句子縮短」繞過去。

    L01 重出時重組題變成「Sorry.」「I have.」，甚至「Thank you please.」。
    """
    ex = {"unscramble": [{"q": ". / Sorry", "ans": "Sorry."},
                         {"q": ". / Hello", "ans": "Hello."},
                         {"q": "I / . / have", "ans": "I have."},
                         {"q": "We / . / have", "ans": "We have."},
                         {"q": "am / I / fine / .", "ans": "I am fine."},
                         {"q": "are / . / We / here", "ans": "We are here."}]}
    errs = gen.validate_overlap(ex)
    assert any("不是完整句子" in e for e in errs)


def test_varied_sentence_endings_pass(gen):
    ex = {"translate": [{"q": "中文", "ans": s} for s in
                        ("I am fine.", "He is a student.", "She is kind.",
                         "We are here.", "They are my friends.", "Thank you.")]}
    assert gen.validate_overlap(ex) == []


def test_chinese_sentence_with_english_blank_is_rejected(gen):
    """L23 與 L42 各有 20 題長這樣，學生看不出要填什麼詞類。"""
    ex = {"mcq": [{"q": "請選擇正確的英文動詞來完成句子：我 ___ 學生。",
                   "opts": ["am", "is", "are", "be"], "ans": "am"}]}
    errs = gen.validate_overlap(ex)
    assert any("中文句子夾一個英文空格" in e for e in errs)


def test_blank_stem_without_chinese_hint_is_rejected(gen):
    """L41：「He ______ jump.」選項有 can 也有 can't，兩個填進去都是通順的英文。"""
    ex = {"mcq": [{"q": "He ______ jump.", "opts": ["go", "can", "can't", "hit"],
                   "ans": "can"}]}
    errs = gen.validate_overlap(ex)
    assert any("答案會不只一個" in e for e in errs)


def test_english_stem_with_blank_passes(gen):
    ex = {"mcq": [{"q": "I ___ a student.（我是學生）",
                   "opts": ["am", "is", "are", "be"], "ans": "am"}]}
    assert gen.validate_overlap(ex) == []


# ---------------------------------------------------------------- 答案位置

def test_answer_positions_are_spread(gen):
    """原本 1355 題裡 1005 題答案排第一個（74%），而兩邊都沒洗牌就印出去。"""
    ex = {"mcq": [{"q": f"q{i}", "opts": [f"ans{i}", f"x{i}", f"y{i}", f"z{i}"],
                   "ans": f"ans{i}"} for i in range(20)]}
    gen.shuffle_options(ex, seed=7)
    positions = [item["opts"].index(item["ans"]) for item in ex["mcq"]]
    assert sorted(positions) == sorted(list(range(4)) * 5)
    for item in ex["mcq"]:
        assert len(set(item["opts"])) == 4


def test_shuffle_is_deterministic(gen):
    make = lambda: {"mcq": [{"q": f"q{i}", "opts": [f"a{i}", f"b{i}", f"c{i}", f"d{i}"],
                             "ans": f"a{i}"} for i in range(12)]}
    one, two = make(), make()
    gen.shuffle_options(one, seed=3)
    gen.shuffle_options(two, seed=3)
    assert one == two


def test_fill_with_only_three_distinct_answers_is_rejected(gen):
    """最多的那個只佔 40% 剛好過關，但十題其實只考了 am/are/is 三個字。"""
    ex = {"fill": [{"q": f"q{i} ____", "ans": a} for i, a in enumerate(
        ["is", "is", "is", "is", "are", "are", "are", "are", "am", "am"])]}
    errs = gen.validate_overlap(ex)
    assert any("只有 3 個不同答案" in e for e in errs)


# ---------------------------------------------------------------- 課文要是故事

def test_one_padded_sentence_cannot_rescue_the_average(gen):
    """🚨 L41 拿最後一句 39 個字把平均撐過門檻，前面九句照樣短。

    所以門檻看中位數不看平均——塞一句長的沒有用。
    """
    short = ["She can climb.", "She can jump.", "She can skate.",
             "She can hide.", "She can swing.", "She can rest."]
    padded = ("She feels slow when she is tired, but she gets quick after a rest, "
              "and she can stand on one foot for a few seconds, but she cannot "
              "break the glass window.")
    sentences = [{"en": s, "zh": ""} for s in short + [padded]]
    counts = [len(s["en"].split()) for s in sentences]
    assert sum(counts) / len(counts) > 6, "這組的平均本來就過得了關"
    errs = gen.validate_reading(sentences)
    assert any("一半以上的句子" in e for e in errs)
    assert any("國小生讀不動" in e for e in errs)


def test_reading_of_three_word_sentences_is_rejected(gen):
    """重出的 L01：十句都是「He is fine.」，句數夠、單字覆蓋 100%，但那不是課文。"""
    sentences = [{"en": s, "zh": ""} for s in (
        "Hello! I am OK.", "Hi! You are welcome.", "He is fine.", "She is sure.",
        "It is OK.", "We are fine.", "They are welcome.", "No, I am fine.")]
    errs = gen.validate_reading(sentences)
    assert any("太短不成故事" in e for e in errs)


def test_reading_with_one_repeated_shape_is_rejected(gen):
    sentences = [{"en": f"{s} is a very kind and happy person.", "zh": ""}
                 for s in ("He", "She", "Tom", "Mei", "Lily", "Ann")]
    errs = gen.validate_reading(sentences)
    assert any("同一個句型" in e for e in errs)


def test_real_story_reading_passes(gen):
    sentences = [{"en": s, "zh": ""} for s in (
        "Mei walks into the classroom and sees a new guest.",
        "Hello! I am Mei, and this is my neighbor Tom.",
        "The guest smiles because she knows his nickname.",
        "Tom is not shy, so he shakes hands with her.",
        "Are you our new teacher? Yes, I am.",
        "Everyone claps, and the lesson begins with a warm greeting.")]
    assert gen.validate_reading(sentences) == []


# ---------------------------------------------------------------- 台灣用語

@pytest.mark.parametrize("bad, good", [
    ("早上好，我是小明。", "早安"),
    ("土豆很熱。", "馬鈴薯"),
    ("黑板下有一塊橡皮。", "橡皮擦"),
    ("一支棕色的尺子。", "尺"),
])
def test_mainland_usage_is_rejected(gen, bad, good):
    """繁體字都對，但不是台灣說法——check_simplified 逐字比對抓不到。"""
    errs = gen.check_usage({"q": bad})
    assert any(good in e for e in errs)


def test_eraser_with_proper_suffix_passes(gen):
    assert gen.check_usage({"q": "黑板下有一塊橡皮擦。"}) == []


def test_youre_welcome_must_not_be_literal(gen):
    """重出的 L01 把 You are welcome. 譯成「你很受歡迎」，fill 的提示還寫「你歡迎」。"""
    errs = gen.check_usage({"en": "You are welcome.", "zh": "你很受歡迎。"})
    assert any("不客氣" in e for e in errs)
    assert gen.check_usage({"en": "You are welcome.", "zh": "不客氣。"}) == []


def test_idiom_check_is_pair_scoped(gen):
    """🚨 不可以拿整份 JSON 當一個字串掃——L01 連退四次就是這樣卡住的。

    課文那句譯對了，就不該因為別處也出現 welcome 而整份被退；
    反過來，別處出現「不客氣」也不該讓譯錯的那句蒙混過關。
    """
    ok = {"reading": {"sentences": [{"en": "You are welcome.", "zh": "不客氣。"},
                                    {"en": "Welcome to my class!", "zh": "歡迎來到我的班級！"}]}}
    assert gen.check_usage(ok) == []

    bad = {"reading": {"sentences": [{"en": "You are welcome.", "zh": "你很受歡迎。"}]},
           "exercises": {"translate": [{"q": "不客氣。", "ans": "You are welcome."}]}}
    assert any("不客氣" in e for e in gen.check_usage(bad))


def test_translate_pairs_are_checked_in_reverse(gen):
    """translate 是 q 中文、ans 英文，方向跟課文相反。"""
    bad = {"translate": [{"q": "你很受歡迎。", "ans": "You are welcome."}]}
    assert any("不客氣" in e for e in gen.check_usage(bad))


# ---------------------------------------------------------------- 文法大綱

def test_syllabus_has_fifty_distinct_points(gen):
    import json
    plan = json.loads((ROOT / "data" / "english" / "course50-syllabus.json")
                      .read_text(encoding="utf-8"))["lessons"]
    assert [l["no"] for l in plan] == list(range(1, 51))
    assert len({l["focus"] for l in plan}) == 50, "文法點有重複"
    assert all(l["grammar"] and l["patterns"] and len(l["points"]) == 2 for l in plan)


def test_lessons_carry_their_own_grammar(gen):
    """🚨 舊版是按主題抓文法，同主題 2–3 課共用一條，50 課只有 17 個點。"""
    lessons = gen.load_lessons()
    assert len({l["grammar"] for l in lessons}) == 50
    assert lessons[2]["taught"] == [lessons[0]["focus"], lessons[1]["focus"]]


# ---------------------------------------------------------------- 不可以偷用後面的文法

def test_future_grammar_is_rejected(gen):
    """L31（虛主詞 it 說天氣）出過「It ______ rainy yesterday.」答案 was，
    但過去式是第 49、50 課才教的。大綱訂了進程，題目卻會偷用後面的東西。"""
    item = {"q": "It ______ rainy yesterday. (昨天下雨)", "ans": "was"}
    assert any("第 50 課才教" in e for e in gen.validate_syllabus_order(31, item))
    assert gen.validate_syllabus_order(50, item) == []


def test_can_before_its_lesson_is_rejected(gen):
    assert any("第 41 課才教" in e for e in
               gen.validate_syllabus_order(20, {"q": "I can jump."}))
    assert gen.validate_syllabus_order(41, {"q": "I can jump."}) == []


def test_marker_check_does_not_match_inside_words(gen):
    """candy／cannonball 裡面有 can，不可以誤判。"""
    assert gen.validate_syllabus_order(20, {"q": "I like candy and cannonball."}) == []


def test_prompt_lists_the_forbidden_markers(gen):
    lessons = gen.load_lessons()
    text = gen.prompt_intro(lessons[30])          # 第 31 課
    assert "was（第 50 課）" in text
    assert "後面的課" in text
    assert gen._ahead_note(50) == "", "最後一課沒有『後面的課』"


# ---------------------------------------------------------------- 單字重排

def test_reorder_keeps_every_word_and_theme(vocab):
    import json
    entries = json.loads(vocab.VOCAB.read_text(encoding="utf-8"))["entries"]
    after = vocab.reorder(entries)
    assert len(after) == 1000
    assert {w["en"] for w in after} == {w["en"] for w in entries}
    assert len({w["en"] for w in after}) == 1000, "有字被複製又遺失"
    # 主題歸屬與主題順序都不可以被動到
    assert [w["theme"] for w in after] == [w["theme"] for w in entries]


def test_sequences_stay_whole_and_in_order(vocab):
    """one..ten、月份、方位介系詞不可以被拆到兩課，也不可以被難度打亂順序。"""
    import json
    entries = json.loads(vocab.VOCAB.read_text(encoding="utf-8"))["entries"]
    after = vocab.reorder(entries)
    words = [w["en"] for w in after]
    for block in (("one", "two", "three", "four", "five", "six", "seven",
                   "eight", "nine", "ten"),
                  ("January", "February", "March", "April", "May", "June"),
                  ("Monday", "Tuesday", "Wednesday", "Thursday")):
        at = [words.index(w) for w in block]
        assert at == sorted(at), f"{block[0]} 這組順序被打亂"
        assert at[-1] - at[0] == len(block) - 1, f"{block[0]} 這組不連續"
        assert len({i // 20 for i in at}) == 1, f"{block[0]} 這組被拆到兩課"


def test_difficulty_curve_is_smoother_than_before(vocab):
    import json
    entries = json.loads(vocab.VOCAB.read_text(encoding="utf-8"))["entries"]
    after = vocab.reorder(entries)
    means = [sum(vocab.score(w["en"]) for w in after[i:i + 20]) / 20
             for i in range(0, 1000, 20)]
    assert means[0] == min(means), "第一課必須是全書最簡單的"
    assert max(means) < 9.0, "不可以再有 L20 那種 12.2 的尖峰"
