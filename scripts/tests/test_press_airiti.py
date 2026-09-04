# -*- coding: utf-8 -*-
"""press_airiti 的靜默失敗防線。

這支管線的錯法都不會拋例外：漏掉一份刊只是那份刊永遠不會被排到，
篇名正規化過頭只是兩篇不同的文章被當成同一篇。所以測的是清單本身。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import press_airiti as pa  # noqa: E402


def test_priority_covers_every_journal():
    # 沒排進 PRIORITY 的刊，--batch 永遠掃不到——不會報錯，只是那份刊一篇都不會下
    assert [k for k in pa.JOURNALS if k not in pa.PRIORITY] == []


def test_priority_has_no_ghost_slug():
    assert [k for k in pa.PRIORITY if k not in pa.JOURNALS] == []


def test_priority_has_no_duplicates():
    assert len(pa.PRIORITY) == len(set(pa.PRIORITY))


@pytest.mark.parametrize("a,b", [
    ("〈廢除八敬法〉", "廢除八敬法"),
    ("性別倫理的震撼教育", "性別倫理的　震撼教育"),
    ("論全球入世佛教之發展進路——兼論其政治取向", "論全球入世佛教之發展進路―兼論其政治取向"),
    ("Ｂ５ 版式", "B5版式"),
])
def test_norm_title_ignores_punctuation_and_width(a, b):
    assert pa.norm_title(a) == pa.norm_title(b)


def test_norm_title_does_not_merge_different_articles():
    # 🚨 正規化只能去標點與全半形。若哪天有人加上繁簡轉換或去掉虛詞，
    #    不同的兩篇就會被折成同一篇，而症狀是「下載到的不是我要的那篇」
    assert pa.norm_title("人間佛教的當代實踐") != pa.norm_title("人间佛教的当代实践")
    assert pa.norm_title("印順的人間佛教") != pa.norm_title("太虛的人間佛教")


def test_safe_name_strips_path_separators():
    assert "/" not in pa.safe_name("宗教／文化")
    assert "\\" not in pa.safe_name("a\\b")
    # 尾端的點在 Windows 上會被吃掉，變成跟別的檔同名
    assert not pa.safe_name("結論...").endswith(".")


def test_site_held_skips_only_the_issues_we_have():
    # 玄奘佛學研究站內 45 期全份，整刊掃描應該全跳過
    assert pa.already_on_site("hcu-buddhist", "45期 (2026/03)")
    assert pa.already_on_site("hcu-buddhist", "1期 (2003/07)")
    # 弘誓站內只有 80–200（缺 85、177–180）；缺的與 80 之前、201 之後都還要下
    assert pa.already_on_site("hongshi", "120期 (2013/04)")
    assert not pa.already_on_site("hongshi", "85期 (2007/02)")
    assert not pa.already_on_site("hongshi", "179期 (2022/10)")
    assert not pa.already_on_site("hongshi", "12期 (1994/12)")
    assert not pa.already_on_site("hongshi", "201期 (2026/06)")
    # 沒登記的刊一律照下，不要因為查表沒中就誤判成「已有」
    assert not pa.already_on_site("campus", "68卷2期 (2026/04)")


def test_site_held_slugs_exist():
    assert [k for k in pa.SITE_HELD if k not in pa.JOURNALS] == []


def test_download_delay_not_lowered():
    # 節流是對機構 IP 的承諾，不是效能參數
    assert pa.DELAY_DL >= 6.0
