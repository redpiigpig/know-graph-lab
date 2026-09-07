# -*- coding: utf-8 -*-
"""結構完美、內容是胡謅的書 —— 品質閘門原本完全看不見這一類。

2026-09-07 稽核：抽 60 本已上架的書，4 本（6.7%）的內容含 LLM 視覺 OCR 的
退化迴圈 —— 模型讀不動某一頁時卡在一句話上一直重印。這種書結構無懈可擊
（chunk 數對、目錄齊、頁面覆蓋率足），於是純結構評分給出：

    《東方化革命》                98 分 → 已上線
    《海德格爾式的現代神學》       94 分 → 已上線
    《A History of Zoroastrianism, Vol. III》  93 分 → 已上線（51/80 頁是迴圈）
    《東南亞的歷史與宗教》         90 分 → 已上線

空書讀者一眼看得出來，這種書看不出來。所以罰則要重到足以擋下閘門，而不是
只記一個 flag。fixture 取自《東方化革命》page 77 那 11 個連續 chunk 的真實內容。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quality_sweep import (  # noqa: E402
    BookSignals, score_book_quality, looks_looping, repetition_rate,
)

# 真實資料：模型卡在這一句上反覆重印
_SENT = "髒卜術的詞源和詞形變化也與兩河流域的術語有相似之處。"
LOOP = _SENT * 4
CLEAN = ("東方化革命 50 完全相同；亞述流派對羊肝十個部分的觀察有嚴格的順序，"
         "西方則沒有類似規定。但是，希臘語中有髒卜的術語，如脾臟、肝臟、肺部、胃部等。")


def sig(**kw) -> BookSignals:
    base = dict(n_chunks=100, blank_rate=0.0, no_toc_rate=0.0, tiny_rate=0.0,
                giant_n=0, mess_wo_toc=0.0, per_page_only=False, needs_ocr=False,
                path_broken=False, standardized=True, page_coverage=1.0,
                repeat_rate=0.0)
    base.update(kw)
    return BookSignals(**base)


class TestLooksLooping:
    def test_the_real_degenerate_loop(self):
        assert looks_looping(LOOP) is True

    def test_normal_prose_is_not_a_loop(self):
        assert looks_looping(CLEAN) is False

    def test_short_text_is_never_a_loop(self):
        # 書眉、頁碼這類短字串不足以判定，寧可放過。
        assert looks_looping("第一章") is False
        assert looks_looping("") is False

    def test_two_repeats_are_not_enough(self):
        # 一句話講兩次可能是原文就這樣（詩歌、禮文）；三次才算迴圈。
        assert looks_looping(_SENT * 2) is False

    def test_a_loop_cut_off_mid_sentence_still_counts(self):
        # preview 截在 100 字，最後一輪必然不完整。
        assert looks_looping((_SENT * 4)[:100]) is True


class TestRepetitionRate:
    def test_clean_book_is_zero(self):
        assert repetition_rate([{"content": CLEAN + str(i)} for i in range(20)]) == 0.0

    def test_counts_looping_chunks(self):
        chunks = [{"content": CLEAN + str(i)} for i in range(9)] + [{"content": LOOP}]
        assert repetition_rate(chunks) == 0.1

    def test_counts_verbatim_repeats_of_the_previous_chunk(self):
        # 另一個面貌：不是在 chunk 內繞圈，而是整塊重吐上一塊。
        chunks = [{"content": CLEAN}, {"content": CLEAN}, {"content": CLEAN + "尾"}]
        assert repetition_rate(chunks) > 0

    def test_empty_input(self):
        assert repetition_rate([]) == 0.0


class TestScoringBlocksTheGate:
    GATE = 80  # server/utils/ebook-quality-gate.ts 的 EBOOK_QUALITY_PASS

    def test_a_structurally_perfect_book_still_scores_full_marks(self):
        score, flags, _ = score_book_quality(sig())
        assert score == 100 and "REPETITION_LOOP" not in flags

    def test_the_dongfanghua_case_no_longer_passes(self):
        # 《東方化革命》：11/86 chunk 是迴圈 ≈ 12.8%，原本 98 分。
        score, flags, _ = score_book_quality(sig(repeat_rate=11 / 86))
        assert "REPETITION_LOOP" in flags
        assert score < self.GATE, f"仍然會上線（{score} 分）"

    def test_ten_percent_is_enough_to_block_a_perfect_book(self):
        score, _, _ = score_book_quality(sig(repeat_rate=0.10))
        assert score < self.GATE

    def test_a_mostly_looping_book_is_crushed(self):
        # 祆教史第三卷 64%
        score, flags, _ = score_book_quality(sig(repeat_rate=0.64))
        assert score <= 40 and "REPETITION_LOOP" in flags

    def test_a_single_stray_chunk_does_not_sink_a_good_book(self):
        # 1/100 —— 罰 2 分，不該讓整本下架。
        score, flags, _ = score_book_quality(sig(repeat_rate=0.01))
        assert score >= self.GATE and "REPETITION_LOOP" not in flags
