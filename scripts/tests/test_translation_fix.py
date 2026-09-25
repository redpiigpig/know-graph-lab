# -*- coding: utf-8 -*-
"""scripts/translation_fix.py 的規則測試：每條規則都有正例（該改的改了）與
反例（不該動的沒動）。反例比正例重要——這支會拿去批次改全站譯文，誤改一處
就是在幾萬段裡散布新錯字。

規則出處：使用者 2026-09-25 的決定（.claude/skills/ebook-translate/SKILL.md 開頭
「🔢 數字寫法」「📖 譯名依脈絡」兩段）。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import translation_fix as tf  # noqa: E402


# ── 數字 ────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("src,want", [
    ("共有一千兩百三十四人", "共有1,234人"),
    ("一千二百三十四英里", "1,234英里"),
    ("主後一千零三十六年", "主後1036年"),
    ("西元一千零三十六年去世", "西元1036年去世"),
    ("一萬兩千三百名士兵", "12,300名士兵"),
    ("三萬五千零五十卷", "35,050卷"),
    ("十二萬三千四百人", "123,400人"),
    ("活了一千零三十六年之久", "活了1036年之久"),
    ("約一千二百三十多人", "約1,230多人"),
])
def test_numerals_positive(src, want):
    assert tf.fix_numerals(src) == (want, 1)


@pytest.mark.parametrize("src", [
    "四千五百人",                 # 兩位有效數字
    "二十五萬人",                 # 兩位有效數字
    "一千人", "三千年",           # 一位有效數字
    "十九世紀", "六十年代",       # 世紀／年代
    "一九六九年二月十八日",       # 逐位的西元年月日：這次不批改
    "明治二十四年",               # 年號
    "民國一千二百三十四年",       # 非西元紀年（假想的極端例）
    "佛曆二千五百六十三年",       # 非西元紀年
    "第一千二百五十條",           # 序數
    "《一千零一夜》",             # 書名／成語
    "八萬四千法門",               # 佛教慣用語
    "十萬八千里",                 # 成語
    "五百三十人",                 # 不到四位數
    "千百年來", "千萬不要", "萬一",  # 不以數字字開頭
    "三十三天",
])
def test_numerals_negative(src):
    assert tf.fix_numerals(src) == (src, 0)


def test_numerals_skipped_for_scripture_corpus():
    r = tf.fix_segment("以色列人共有六十萬三千五百五十名。", scripture=True)
    assert r.text == "以色列人共有六十萬三千五百五十名。"
    assert "numerals" not in r.hits
    r2 = tf.fix_segment("以色列人共有六十萬三千五百五十名。", scripture=False)
    assert r2.text == "以色列人共有603,550名。"


def test_parse_zh_number():
    assert tf.parse_zh_number("一千零三十六") == 1036
    assert tf.parse_zh_number("兩萬三千") == 23000
    assert tf.parse_zh_number("一九六九") is None
    assert tf.parse_zh_number("十七") == 17


# ── 中間點 ──────────────────────────────────────────────────────────────────
def test_middle_dot_between_han_names():
    assert tf.fix_middle_dot("約翰·衛斯理與查理·衛斯理") == ("約翰‧衛斯理與查理‧衛斯理", 2)
    assert tf.fix_middle_dot("馬丁・路德") == ("馬丁‧路德", 1)


@pytest.mark.parametrize("src", [
    "J·S·Bach 的作品",            # 英文
    "圓周率約 3·14",              # 數字
    "見《論語·學而》",            # 書名號裡的點（書目）
    "〈宗教·哲學〉一文",
    "ヨハネ・ウェスレー",         # 日文（含假名）
    "約翰‧衛斯理",                # 已經是正確的點
])
def test_middle_dot_negative(src):
    assert tf.fix_middle_dot(src) == (src, 0)


# ── 隻能／隻是／隻有 ────────────────────────────────────────────────────────
@pytest.mark.parametrize("src,want", [
    ("他隻能等待", "他只能等待"),
    ("這隻是開始", "這只是開始"),  # 「這隻」後面直接接「是」＝「這只是」被轉壞
])
def test_zhi_mixed(src, want):
    assert tf.fix_zhi(src)[0] == want


@pytest.mark.parametrize("src,want", [
    ("我們隻能如此", "我們只能如此"),
    ("那不過隻是比喻", "那不過只是比喻"),
    ("神隻有一位", "神只有一位"),
    ("你隻要相信", "你只要相信"),
])
def test_zhi_positive(src, want):
    assert tf.fix_zhi(src) == (want, 1)


@pytest.mark.parametrize("src", [
    "每隻要餵兩次",      # 量詞
    "一隻有翅膀的鳥",    # 量詞
    "三隻是白的",
    "幾隻能飛",
    "船隻是唯一的交通",  # 名詞「船隻」
    "隻身前往",          # 不在規則內
])
def test_zhi_negative(src):
    assert tf.fix_zhi(src) == (src, 0)


# ── 頭發 ────────────────────────────────────────────────────────────────────
def test_toufa_positive():
    assert tf.fix_toufa("她的頭發很長") == ("她的頭髮很長", 1)
    assert tf.fix_toufa("頭發都白了") == ("頭髮都白了", 1)


@pytest.mark.parametrize("src", ["他在開頭發表聲明", "帶頭發起運動", "從頭發展", "頭髮很長"])
def test_toufa_negative(src):
    assert tf.fix_toufa(src) == (src, 0)


# ── 字形 ────────────────────────────────────────────────────────────────────
def test_variants_positive():
    assert tf.fix_variants("爲衆人着想") == ("為眾人著想", 3)
    assert tf.fix_variants("在這裏") == ("在這裡", 1)


def test_variants_negative_japanese_and_legit_forms():
    ja = "神の爲に生きる"         # 日文原文照原漢字
    assert tf.fix_variants(ja) == (ja, 0)
    ok = "纔剛到，喫飯了"          # 台灣合法用字，不是本規則對象
    assert tf.fix_variants(ok) == (ok, 0)


# ── 彎引號 ──────────────────────────────────────────────────────────────────
def test_quotes_chinese():
    assert tf.fix_curly_quotes("他說：“我來了。”") == ("他說：「我來了。」", 1)


def test_quotes_nested():
    got, n = tf.fix_curly_quotes("他說：“耶穌說‘我是道路’。”")
    assert got == "他說：「耶穌說『我是道路』。」"
    assert n == 1


@pytest.mark.parametrize("src", [
    'Smith, “The Origins of Gnosticism,” JBL 12 (1990): 3–20.',   # 英文書目
    "見 Rudolph, “Gnosis and Gnosticism” 一文",                  # 英文篇名夾在中文裡
    "作者寫道 “God is love” 一語",                               # 英文引文
    "don’t 與 it’s 是縮寫",                                      # 英文撇號
    "「已經是中文引號」",
])
def test_quotes_negative(src):
    assert tf.fix_curly_quotes(src) == (src, 0)


def test_quotes_single_top_level():
    assert tf.fix_curly_quotes("所謂‘道’者") == ("所謂「道」者", 1)


# ── 章名黏正文 ──────────────────────────────────────────────────────────────
def test_heading_glued_same_line_numeric():
    zh = "#### 第一章當我與一位高盧朋友聚集在一處時，我的朋友波斯圖米亞努斯加入了我們。他剛剛從東方歸來。"
    src = "#### Chapter I.\n\nWhen I and a Gallic friend had assembled in one place..."
    got, n = tf.split_glued_heading(zh, src)
    assert n == 1
    assert got.startswith("#### 第一章\n\n當我與一位高盧朋友")


def test_heading_glued_number_mismatch_untouched():
    """原文是 Chapter IV，譯文標題卻是第三章——對不上就不切。"""
    zh = "#### 第三章於是我便朝著先前從遠處望見的那間小屋走去。在那裡，我看見一位老人，身穿獸皮衣裳。"
    src = "#### Chapter IV.\n\nSo I went to the hut..."
    assert tf.split_glued_heading(zh, src) == (zh, 0)


def test_heading_glued_descriptive_title_untouched_but_reported():
    """原文標題不是純編號，判不出邊界 → 不切，但要列進未解決。"""
    zh = "### 蘇皮修的生平與著作蘇皮修約於主後363年生於阿奎塔尼亞，並如普遍所認為，於主後420年去世。因此他是同時代人。"
    src = "### Life and Writings of Sulpitius Severus.\n\nSulpitius Severus was born..."
    assert tf.split_glued_heading(zh, src) == (zh, 0)
    assert tf.glued_heading_unresolved(zh, src) == 1


def test_heading_single_newline_gets_blank_line():
    zh = "## 第二章\n他們來到城裡。"
    src = "## Chapter II.\n\nThey came to the city."
    r = tf.fix_segment(zh, src)
    assert r.text == "## 第二章\n\n他們來到城裡。"
    assert r.hits.get("heading") == 1


def test_heading_fix_reverted_when_source_also_glued():
    """原文自己也是「標題＋單換行＋正文」一段：切了反而跟原文段序對不齊，不切。"""
    zh = "## 第二章\n他們來到城裡。"
    src = "## Chapter II.\nThey came to the city."
    r = tf.fix_segment(zh, src)
    assert r.text == zh
    assert "heading" not in r.hits


def test_heading_normal_untouched():
    zh = "## 第二章\n\n他們來到城裡。"
    assert tf.split_glued_heading(zh, "## Chapter II.\n\nThey came.") == (zh, 0)


# ── 清空判準 ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("zh,reason", [
    ("請提供完整的文段內容，我才能為您翻譯。", "meta"),
    ("我注意到您提供的「英文原文」實際上是梵文文本，而非英文。", "meta"),
    ("I'm ready to translate the English text from the book.", "meta"),
    ("<think>好，這段要翻成中文", "think"),
    ("雅各的後裔</think>雅各的後裔住在迦南。", "think"),
    ("We need to translate the given English paragraph into Chinese.", "think"),
    ("�們來到耶路撒冷，在那裡住了三天。", "fffd"),
    ("The forms divi, dii, and dei do not enable us to establish an essential "
     "difference between the gods of Greece and those of Italy.", "untranslated"),
    ("これは日本語の文章であり、まだ翻訳されていないものである。", "untranslated"),
    ("Die Religion ist nicht mit der Moral zu verwechseln, und das ist auch der Grund "
     "für die Verwirrung der Begriffe in der Theologie.", "untranslated"),
])
def test_clear_reason_positive(zh, reason):
    assert tf.clear_reason(zh) == reason


@pytest.mark.parametrize("zh", [
    "內村於1893年出版《基督信徒的慰藉》，時年三十二。",
    "抱歉，我來晚了。」彼得說著，走進屋裡。",             # 對白裡的「抱歉」
    "我注意到他臉上的神情變了，便不再說話。",             # 敘事裡的「我注意到」
    "《娑摩吠陀》（Sama-veda）、Charana、Sruti、Smriti、atman、anila。",
    "〈何故に大文學は出ずるや？〉是內村早年的一篇講演。",  # 中文段落裡的日文篇名
    "縱然異邦教法入侵　／　古國の如何なる教え入り來るも",  # 並列體例
    "RUDOLPH, K. Gnosis. Edinburgh: T&T Clark, 1983. PEARSON, B. A. Gnosticism. 1990, pp. 3-20.",
    "",
])
def test_clear_reason_negative(zh):
    assert tf.clear_reason(zh) == ""


def test_clear_wins_over_fixes():
    r = tf.fix_segment("請提供完整的文段內容。他隻能等待。")
    assert r.clear == "meta" and r.text == ""


def test_clear_disabled_when_rule_not_selected():
    r = tf.fix_segment("請提供完整的文段內容。他隻能等待。", rules={"zhi"})
    assert r.clear == "" and r.text == "請提供完整的文段內容。他只能等待。"


def test_parse_rules():
    assert tf.parse_rules("fixes") == set(tf.ALL_FIX)
    assert tf.parse_rules("clear") == set(tf.CLEAR_RULES)
    assert tf.parse_rules("zhi,meta") == {"zhi", "meta"}
    with pytest.raises(SystemExit):
        tf.parse_rules("nope")


# ── lane 保護 ───────────────────────────────────────────────────────────────
def test_lane_locks_work_block(tmp_path):
    (tmp_path / "panikkar_auto.py").write_text(
        'WORKS = {\n'
        '    "rhythm-of-being": {\n        "ebook_id": "55555561-5555-4555-8555-555555555555",\n    },\n'
        '    "vedic-experience": {\n        "ebook_id": "55555568-5555-4555-8555-555555555555",\n    },\n'
        '}\n', encoding="utf-8")
    cmd = r'"python.exe" -X utf8 scripts\panikkar_auto.py --work vedic-experience --backend nvidia'
    ids, slugs = tf.lane_locks_from_cmdline(cmd, tmp_path)
    assert ids == {"55555568-5555-4555-8555-555555555555"}
    assert slugs == {"vedic-experience"}


def test_lane_locks_author_module(tmp_path):
    (tmp_path / "uchimura_auto.py").write_text(
        'AUTHOR_MODULES = {"uchimura": "uchimura_build", "sekine": "sekine_build"}\n',
        encoding="utf-8")
    (tmp_path / "sekine_build.py").write_text(
        'A = "aaaaaaaa-0000-4000-8000-000000000001"\nB = "aaaaaaaa-0000-4000-8000-000000000002"\n',
        encoding="utf-8")
    cmd = r'python.exe -X utf8 scripts\uchimura_auto.py --author sekine --run-queue --shard 0/3'
    ids, slugs = tf.lane_locks_from_cmdline(cmd, tmp_path)
    assert ids == {"aaaaaaaa-0000-4000-8000-000000000001", "aaaaaaaa-0000-4000-8000-000000000002"}
    assert slugs == {"sekine"}


def test_lane_guard_blocks_locked_and_recent(tmp_path):
    lane = tf.Lane("x", 1, "cmd", {"aaaaaaaa-0000-4000-8000-000000000001"}, set())
    g = tf.LaneGuard([lane])
    assert g.why_locked("AAAAAAAA-0000-4000-8000-000000000001")
    f = tmp_path / "b.jsonl"
    f.write_text("{}", encoding="utf-8")
    assert "30 分鐘" in g.why_locked("bbbbbbbb-0000-4000-8000-000000000002", f)
    import os, time
    old = time.time() - 3600
    os.utime(f, (old, old))
    assert g.why_locked("bbbbbbbb-0000-4000-8000-000000000002", f) == ""


# ── 根因：U+FFFD 與輸出關卡 ────────────────────────────────────────────────
def test_engine_finalize_strips_fffd():
    """每條引擎出口都過 _finalize：模型 byte-fallback 多吐的 U+FFFD 不可存進去。"""
    import translate_ebook_to_zh as te
    assert te._finalize("�請聯絡作者。\n") == "請聯絡作者。"
    assert te._finalize("實�踐​") == "實踐"


def test_strip_fffd_only_when_next_char_intact():
    assert tf.strip_fffd("�請聯絡作者") == "請聯絡作者"
    assert tf.strip_fffd("結尾壞掉�") is None
    assert tf.strip_fffd("��連續") is None


def test_lit_review_gate_blocks_four_kinds():
    import ingest_lit_review as ilr
    src = "The healer is not the one who cures."
    assert ilr.output_gate("請提供完整的文段內容，我才能翻譯。", src) == "meta"
    assert ilr.output_gate("<think>先想一下", src) == "think"
    assert ilr.output_gate("�儘管治癒者並非施治之人。", src) == "fffd"
    assert ilr.output_gate("The healer is not the one who cures, and that is the whole of the "
                           "matter which we have been discussing in this chapter.", src) == "untranslated"
    assert ilr.output_gate("", src) == "empty"
    assert ilr.output_gate("治癒者並非施治之人。", src) == ""


def test_gnostic_gate():
    import ingest_gnostic as ig
    assert ig.output_gate("我注意到您提供的文本似乎不完整。", "x") == "meta"
    assert ig.output_gate("耶穌說：「看哪，天國在你們裡面。」", "x") is None
