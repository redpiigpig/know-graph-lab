"""Tests for translation_dashboard pure helpers: status buckets, done-retention,
and the ACCS junk-file skip that caused 民數記 to appear twice."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translation_dashboard import (
    state_category, is_stale_done, DONE_RETENTION_DAYS,
)

DAY = 86400


def test_state_category_buckets():
    assert state_category("執行中") == "running"
    assert state_category("完成") == "complete"
    assert state_category("錯誤") == "attention"
    assert state_category("疑似停滯") == "attention"
    assert state_category("待匯入/檢查") == "attention"
    assert state_category("已暫停") == "paused"
    assert state_category("未開始") == "paused"


def test_stale_done_only_hides_old_completed():
    now = 1_000 * DAY
    assert is_stale_done("完成", now - 4 * DAY, now) is True     # 4 天前完成 → 隱藏
    assert is_stale_done("完成", now - 1 * DAY, now) is False    # 昨天完成 → 顯示
    assert is_stale_done("執行中", now - 9 * DAY, now) is False  # 執行中永不隱藏
    assert is_stale_done("完成", None, now) is False             # 無時間戳 → 不隱藏
    assert DONE_RETENTION_DAYS == 3
