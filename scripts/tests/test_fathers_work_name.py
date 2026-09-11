# -*- coding: utf-8 -*-
"""work_name 的邊界：修完 chapter_path 之後冒出來的中文數字章號後綴。"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fathers_original", ROOT / "scripts" / "fathers_original.py")
FO = importlib.util.module_from_spec(spec)
sys.modules["fathers_original"] = FO
spec.loader.exec_module(FO)


def test_strips_ascii_chapter_suffix():
    assert FO.work_name("第六卷 第22章") == "第六卷"
    assert FO.work_name("希波呂圖《駁諸異端》 第3章") == "希波呂圖《駁諸異端》"


def test_strips_chinese_numeral_chapter_suffix():
    """修好的路徑帶的是章名原樣的中文數字。"""
    assert FO.work_name("第一卷 第一章") == "第一卷"
    assert FO.work_name("第十二卷 第二十二章") == "第十二卷"
    assert FO.work_name("第六卷 第一至十章") == "第六卷"


def test_does_not_eat_the_prefix_itself():
    """🚨 「第一卷」自己也長得像章號。少了「前面要有空白」這個條件，它會被剝成
    空字串，本來對得上的那幾段反而全斷。"""
    for p in ("第一卷", "第六卷", "第十二卷"):
        assert FO.work_name(p) == p


def test_does_not_behead_clean_paths_that_merely_start_with_a_numeral():
    """🚨 少了「結尾是章或節」這個條件，這種乾淨路徑會被砍頭。"""
    assert FO.work_name("第三十九至二十六條") == "第三十九至二十六條"
    assert FO.work_name("第六十至七十四節") == "第六十至七十四節"


def test_strips_volume_suffix_as_before():
    assert FO.work_name("懺悔錄 卷二") == "懺悔錄"
    assert FO.work_name("懺悔錄 卷一 第1-10章") == "懺悔錄"


def test_blank():
    assert FO.work_name("") == ""
