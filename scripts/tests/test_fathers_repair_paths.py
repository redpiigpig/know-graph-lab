# -*- coding: utf-8 -*-
"""chapter_path 修復的純函式測試。樣本取自希拉里《論三位一體》實檔
（709f43f9…，401 段裡 211 段的 chapter_path 被正文吞掉）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fathers_repair_chapter_paths import (  # noqa: E402
    headings_of, propagate_book, repair_chunks, structural_trim, truncate_path,
)

SWALLOWED = (
    "第一章 — 希拉里的生平與著述希拉里是西方教會中最偉大卻研究最不足的教父之一。"
    "他之所以遭到忽視，部分原因在於其著述風格的某種晦澀性，以及他所試圖傳達之思想的困難性。"
)
HEADING_LINE = "## 第一章 — 希拉里的生平與著述\n\n希拉里是西方教會中最偉大卻研究最不足的教父之一。"


# ── headings_of ─────────────────────────────────────────────────────────────

def test_headings_of_picks_markdown_headings():
    assert headings_of(HEADING_LINE) == ["第一章 — 希拉里的生平與著述"]


def test_headings_of_blank():
    assert headings_of("") == []
    assert headings_of("沒有標題的一段正文。") == []


# ── truncate_path ───────────────────────────────────────────────────────────

def test_truncate_cuts_swallowed_body():
    assert truncate_path(SWALLOWED, ["第一章 — 希拉里的生平與著述"]) == "第一章 — 希拉里的生平與著述"


def test_truncate_prefers_the_longest_matching_heading():
    """🚨 取最長的。短的那個會把副標切掉，路徑就從「第一章 — 生平與著述」
    變成光禿禿的「第一章」，十二卷裡每卷都有一個「第一章」，等於自己製造碰撞。"""
    got = truncate_path(SWALLOWED, ["第一章", "第一章 — 希拉里的生平與著述"])
    assert got == "第一章 — 希拉里的生平與著述"


def test_truncate_leaves_clean_paths_alone():
    for p in ("第六卷", "上帝之城 卷十七 第1-10章", "第三十九至二十六條", "封面"):
        assert truncate_path(p, ["第六卷"]) == p


def test_truncate_gives_up_when_no_heading_matches():
    """認不出來就原樣留著。硬切（例如切到第一個句號）會切出半個章名，
    那比留著更難查——留著至少一眼看得出是壞的。"""
    long_unknown = "尤傑紐斯僭主，被任命為瓦倫提尼安二世的首席秘書，導致其主人被絞死並自行掌權，135 ; 被狄奧多西擊敗"
    assert truncate_path(long_unknown, ["完全不相干的標題"]) == long_unknown


def test_truncate_blank():
    assert truncate_path("", []) == ""


# ── propagate_book ──────────────────────────────────────────────────────────

def test_propagate_adds_book_to_repaired_paths():
    entries = [
        {"path": "第六卷", "repaired": False},
        {"path": "第22章", "repaired": True},
        {"path": "第23章", "repaired": True},
    ]
    assert propagate_book(entries) == ["第六卷", "第六卷 第22章", "第六卷 第23章"]


def test_propagate_leaves_clean_paths_untouched():
    """🚨 只補修過的段。本來就乾淨的路徑一律不動——否則「第六卷 第1-10章」
    會被加成「第六卷 第六卷 第1-10章」。"""
    entries = [
        {"path": "第六卷", "repaired": False},
        {"path": "第1-10章", "repaired": False},
    ]
    assert propagate_book(entries) == ["第六卷", "第1-10章"]


def test_propagate_switches_book_at_the_next_volume():
    entries = [
        {"path": "第六卷", "repaired": False},
        {"path": "第22章", "repaired": True},
        {"path": "第七卷", "repaired": False},
        {"path": "第3章", "repaired": True},
    ]
    assert propagate_book(entries) == ["第六卷", "第六卷 第22章", "第七卷", "第七卷 第3章"]


def test_propagate_does_not_double_prefix():
    entries = [
        {"path": "第六卷", "repaired": False},
        {"path": "第六卷 第22章", "repaired": True},
    ]
    assert propagate_book(entries) == ["第六卷", "第六卷 第22章"]


def test_propagate_before_any_volume_seen():
    """導論那一段在任何「第N卷」之前，沒有卷次可補，就別亂補。"""
    entries = [{"path": "第一章 — 希拉里的生平與著述", "repaired": True}]
    assert propagate_book(entries) == ["第一章 — 希拉里的生平與著述"]


# ── repair_chunks（端到端）──────────────────────────────────────────────────

def test_repair_chunks_end_to_end():
    chunks = [
        {"chunk_index": 0, "chapter_path": "第六卷", "content": "{{p:98}}第六卷  1. 我滿懷著…"},
        {"chunk_index": 1, "chapter_path": "第22章但這種荒唐的言談必須停止；揭露異端愚蠢的修辭必須讓位於建立論證的辛苦工作。所以我相信",
         "content": "## 第22章\n\n但這種荒唐的言談必須停止；"},
        {"chunk_index": 2, "chapter_path": "第六卷", "content": "7. 誰看不出這裡蛇爬過的黏滑痕跡"},
    ]
    paths, changed = repair_chunks(chunks)
    assert paths == ["第六卷", "第六卷 第22章", "第六卷"]
    assert changed == 1


def test_repair_chunks_reports_no_change_when_clean():
    chunks = [{"chunk_index": 0, "chapter_path": "第六卷", "content": "正文"}]
    paths, changed = repair_chunks(chunks)
    assert changed == 0 and paths == ["第六卷"]


# ── structural_trim（第二道：標題自己就被吞掉的那一半）──────────────────────

def test_structural_trim_cuts_body_glued_straight_onto_the_chapter_number():
    """🚨 實檔 211 段裡有 104 段的 `## ` 標題自己就被吞了
    （「## 第一章亞流主義的一般歷史及其時代基督教思想的傾向」），
    只比對標題等於沒截——所以要有這第二道。"""
    assert structural_trim("第一章亞流主義的一般歷史及其時代基督教思想的傾向") == "第一章"
    assert structural_trim("第一節這裡再次充滿了值得注意的內容。") == "第一節"


def test_structural_trim_keeps_real_subtitles():
    """有分隔符的是真副標，一律留著。"""
    for p in ("第四章 《論三位一體》的構成與特質", "第二章 — 聖希拉里的神學",
              "第一章 — 希拉里的生平與著述"):
        assert structural_trim(p) == p


def test_structural_trim_leaves_non_chapter_paths_alone():
    for p in ("第六卷", "封面", "導言", "第三十九至二十六條", "上帝之城 卷十七 第1-10章"):
        assert structural_trim(p) == p


def test_structural_trim_bare_chapter_number():
    assert structural_trim("第一章") == "第一章"


def test_truncate_keeps_legitimate_path_suffixes():
    """🚨 「索引」「論基督教教義」「前言」本身就是某一段的 `## ` 標題，只比對前綴
    會把合法後綴當成黏上的正文切掉——把好路徑改壞，比沒修更糟。實檔三本 dry-run
    時這樣誤砍了 11 段。"""
    heads = ["索引", "論基督教教義", "前言", "懺悔錄"]
    for p in ("索引 第3章", "論基督教教義 第1-4章", "前言 第5章", "懺悔錄 卷一 第1-10章"):
        assert truncate_path(p, heads) == p


def test_truncate_still_cuts_when_the_remainder_is_prose():
    heads = ["第二章——論上帝對迦南地的應許何時得以應驗"]
    swallowed = heads[0] + "，即使肉體上的以色列人也已獲得其所有在前一本書中，我們曾說過"
    assert truncate_path(swallowed, heads) == heads[0]


def test_repair_chunks_uses_a_book_wide_heading_pool():
    """🚨 一章橫跨好幾段，`## ` 標題只在第一段。只看自己的話，接續段永遠找不到
    候選——實檔 211 段裡有 71 段就是這樣留在原地，而它們正是原典欄整卷重複的大宗。"""
    head = "第一章 — 希拉里的生平與著述"
    chunks = [
        {"chunk_index": 0, "chapter_path": head + "希拉里是西方教會中最偉大卻研究最不足的教父之一。",
         "content": f"## {head}\n\n希拉里是西方教會中…"},
        {"chunk_index": 1, "chapter_path": head + "希拉里是西方教會中最偉大卻研究最不足的教父之一。",
         "content": "他大約生於公元三百年左右，幾乎可以確定地說…"},   # 接續段，沒有標題
    ]
    paths, changed = repair_chunks(chunks)
    assert paths == [head, head]
    assert changed == 2


def test_propagate_resets_at_volume_boundaries():
    """🚨 同一個檔案裡不只一部著作（希拉里那冊有導論／論會議／論三位一體／詩篇講道／
    正統信仰詳解）。卷次不在 volume 換的時候歸零，會一路傳到隔壁那部去——對齊器
    照樣配得上、命中率照樣好看，配到的卻是別部的原文。實測卷一因此掉到 0/48。"""
    entries = [
        {"path": "第一卷", "repaired": False, "volume": "論三位一體"},
        {"path": "第二章", "repaired": True, "volume": "論三位一體"},
        {"path": "第一章", "repaired": True, "volume": "詩篇講道"},
    ]
    assert propagate_book(entries) == ["第一卷", "第一卷 第二章", "第一章"]
