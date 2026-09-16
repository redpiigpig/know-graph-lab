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
