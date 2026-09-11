# -*- coding: utf-8 -*-
"""西元年份改阿拉伯數字：該改的要改，不該改的一個都不能動。

使用者 2026-09-11 定調。判準是**連續四個漢數字**——中文不會用四個連號漢數字
表示別的東西，所以這一刀既夠準也夠窄。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fix_year_numerals import fix  # noqa: E402


# ── 該改的 ────────────────────────────────────────────────────────────────────
def test_plain_year():
    assert fix("他於一八九三年出版此書。") == "他於1893年出版此書。"


def test_zero_written_as_circle():
    """一九〇〇 的〇是圈不是零。"""
    assert fix("一九〇〇年創刊") == "1900年創刊"


def test_decade():
    assert fix("一九二〇年代的日本") == "1920年代的日本"


def test_range_first_number_has_no_year_marker():
    """「一八九三至一八九六年」——前一個沒有接「年」，單看年字標記抓不到。"""
    assert fix("一八九三至一八九六年間於京都出版") == "1893至1896年間於京都出版"


def test_range_with_dash():
    assert fix("一九四五－一九六〇年") == "1945－1960年"


def test_several_years_in_one_paragraph():
    got = fix("一八六一年生，一九三〇年卒，享年七十。")
    assert got == "1861年生，1930年卒，享年七十。"


# ── 絕不可動的 ────────────────────────────────────────────────────────────────
def test_era_year_is_left_alone():
    """年號紀年是位值寫法（二十四），本來就該用漢數字。"""
    assert fix("明治二十四年一月九日") == "明治二十四年一月九日"
    assert fix("大正十二年二月七日") == "大正十二年二月七日"


def test_duration_is_not_a_year():
    assert fix("本書發行已滿三十年。") == "本書發行已滿三十年。"


def test_ordinal_and_century():
    assert fix("第三章談二十世紀的處境") == "第三章談二十世紀的處境"


# ── 月日：有錨點才改 ──────────────────────────────────────────────────────────
def test_full_date_after_arabic_year():
    assert fix("一八九三年一月二十五日") == "1893年1月25日"


def test_year_and_month_without_day():
    assert fix("一九〇〇年十二月創刊") == "1900年12月創刊"


def test_month_day_pair_without_year():
    """月與日成對出現，本身就是日期。"""
    assert fix("三月十五日的集會") == "3月15日的集會"


def test_month_range_tail():
    assert fix("一八九三年三月至五月") == "1893年3月至5月"


def test_day_range_tail():
    assert fix("三月十五日至二十日") == "3月15日至20日"


def test_positional_tens():
    assert fix("十月三十一日") == "10月31日"
    assert fix("十一月十日") == "11月10日"


# ── 月日：絕不可動的 ──────────────────────────────────────────────────────────
def test_three_days_later_is_a_duration():
    """🚨 福音書滿篇「三日後復活」——三日是三天不是三號，改了就是改壞聖經。"""
    assert fix("第三日從死裡復活") == "第三日從死裡復活"
    assert fix("三日後他就回來了") == "三日後他就回來了"


def test_bare_month_is_left_alone():
    """落單的月份沒有錨點，可能是專名。"""
    assert fix("十月革命之後") == "十月革命之後"
    assert fix("那年五月他離開了") == "那年五月他離開了"


def test_counted_months_are_not_a_date():
    assert fix("他在那裡住了三個月") == "他在那裡住了三個月"


def test_era_year_keeps_kanji_month_and_day():
    """年號紀年整串都該留漢數字——年是漢數字，月日也跟著留。"""
    assert fix("明治二十四年一月九日") == "明治二十四年一月九日"
    assert fix("大正十二年二月七日") == "大正十二年二月七日"


def test_out_of_range_is_left_alone():
    """十三月不是月份，硬改只會把別的東西改壞。"""
    assert fix("十三月十五日") == "十三月十五日"


def test_five_digit_run_is_not_a_year():
    """前後不可再接漢數字，否則會從中間切一段出來當年份。"""
    assert fix("一二三四五") == "一二三四五"


def test_four_digits_not_followed_by_year_is_left():
    """沒有「年」也沒有範圍標記，就不是年份——例如電話或編號。"""
    assert fix("編號一二三四號") == "編號一二三四號"


def test_empty_and_none():
    assert fix("") == ""
    assert fix(None) == ""
