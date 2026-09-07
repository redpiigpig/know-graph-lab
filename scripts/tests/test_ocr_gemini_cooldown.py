# -*- coding: utf-8 -*-
"""Gemini cooldown 要對齊額度真正重置的時刻，不是隨便一個固定時長。

這支存在的理由是一次實際的損失：cooldown 原本寫死 6 小時，而 Gemini 免費層是
每日額度、在美西午夜重置。2026-09-06 14:27（台灣）耗盡 → 擋到 20:27，但額度
15:00 就回來了，17:31 那一輪明明有額度卻被自己擋掉、整輪退去 Haiku。

邊界算錯一小時的代價是不對稱的：算晚了只是少用幾小時，算早了會讓腳本在額度還
沒回來時試一次、失敗後把 cooldown 重寫到「再下一個午夜」——直接跳掉一整天。
所以 DST 的邊界要抓準，不能用固定 offset 湊。
"""
import datetime as dt

import ocr_with_gemini as O

UTC = dt.timezone.utc


def _utc(y, m, d, h=0, mi=0):
    return dt.datetime(y, m, d, h, mi, tzinfo=UTC).timestamp()


class TestPacificOffset:
    def test_summer_is_pdt(self):
        assert O._pacific_utc_offset(_utc(2026, 7, 1)) == 7

    def test_winter_is_pst(self):
        assert O._pacific_utc_offset(_utc(2026, 1, 15)) == 8

    def test_december_is_pst(self):
        assert O._pacific_utc_offset(_utc(2026, 12, 25)) == 8

    def test_dst_starts_second_sunday_of_march(self):
        # 2026-03-08 是三月第二個週日；10:00 UTC 是切換點。
        assert O._pacific_utc_offset(_utc(2026, 3, 8, 9)) == 8
        assert O._pacific_utc_offset(_utc(2026, 3, 8, 10)) == 7

    def test_dst_ends_first_sunday_of_november(self):
        # 2026-11-01 是十一月第一個週日；09:00 UTC 是切換點。
        assert O._pacific_utc_offset(_utc(2026, 11, 1, 8)) == 7
        assert O._pacific_utc_offset(_utc(2026, 11, 1, 9)) == 8


class TestNextQuotaReset:
    def test_pdt_reset_is_0700_utc(self):
        # 夏令時間，美西午夜 = 07:00 UTC。
        r = O._next_quota_reset(_utc(2026, 9, 6, 8))
        assert dt.datetime.fromtimestamp(r, UTC) == dt.datetime(2026, 9, 7, 7, tzinfo=UTC)

    def test_pst_reset_is_0800_utc(self):
        # 冬令時間，美西午夜 = 08:00 UTC。
        r = O._next_quota_reset(_utc(2026, 1, 15, 9))
        assert dt.datetime.fromtimestamp(r, UTC) == dt.datetime(2026, 1, 16, 8, tzinfo=UTC)

    def test_the_incident_that_prompted_this(self):
        # 2026-09-06 14:27 台灣 = 06:27 UTC。額度重置在同日 07:00 UTC
        # （= 台灣 15:00），所以 cooldown 只該擋 33 分鐘，不是 6 小時。
        exhausted = _utc(2026, 9, 6, 6, 27)
        r = O._next_quota_reset(exhausted)
        assert dt.datetime.fromtimestamp(r, UTC) == dt.datetime(2026, 9, 6, 7, tzinfo=UTC)
        assert r - exhausted < 6 * 3600

    def test_reset_is_always_ahead_and_within_a_day(self):
        for day in range(1, 366, 7):
            now = _utc(2026, 1, 1) + day * 86400
            gap = O._next_quota_reset(now) - now
            assert 0 < gap <= 24 * 3600, f"day {day}: gap {gap / 3600:.1f}h"

    def test_just_before_reset_does_not_skip_a_whole_day(self):
        # 重置前一分鐘耗盡 → 只該再等一分鐘，不是等到明天。
        now = _utc(2026, 9, 7, 6, 59)
        assert O._next_quota_reset(now) - now == 60
