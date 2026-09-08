#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""長跑腳本執行期間不讓機器進 Modern Standby。

為什麼需要這支
--------------
這台是 S0 Modern Standby 筆電。一進待機，掛在主控台的行程會同時收到
STATUS_CONTROL_C_EXIT（0xC000013A），排程器記成「工作被中止」。2026-09-08 稽核
30 小時的排程事件：**40 次**這種死法，特徵是兩三支在同幾秒內一起死（例如 09-08
07:38:30 進 Modern Standby，07:38:41–42 三支排程接連陣亡）。

不是電池設定造成的——Airiti 與三支 OCR 的電池旗標本來就是 False，照死不誤。
也不是閒置逾時——`powercfg` 查過 standby-timeout 的 AC/DC 都已經是 0（永不）。
真正的觸發是**闔蓋或人離開**：S0 待機不看逾時設定也會進。

而 `powercfg /requests` 顯示**沒有任何行程在阻止睡眠**——這些管線跑再久，
Windows 都認為機器閒著。這支就是去補那一格。

為什麼不用 S4U（「不論使用者登入與否均執行」）
-----------------------------------------------
🚨 那條路會壞得更難看。Google Drive 的 `G:` 是**掛在使用者互動工作階段**的虛擬磁碟，
S4U 工作跑在另一個登入工作階段，看不到 `G:`。而這些排程沒有一支不碰
`G:\我的雲端硬碟\...`——華藝把 PDF 寫進去、OCR 從那裡讀掃描檔。改成 S4U 會讓
「排程正常結束、log 也漂亮」但檔案全部落空，正是最難察覺的那種失敗。

用法
----
    from keep_awake import keep_awake
    keep_awake()                      # 行程活著就不讓系統睡，結束自動解除

    with keep_awake():                # 想限定範圍就用 context manager
        ...

    python scripts/keep_awake.py --hold   # 獨立佔用，Ctrl+C 結束（給 .bat 包用）

非 Windows 或呼叫失敗一律靜默 no-op——這是加分項，不該讓它擋住主流程。
"""
from __future__ import annotations

import sys
import time

# SetThreadExecutionState 旗標（WinBase.h）
ES_CONTINUOUS = 0x80000000        # 持續生效，直到再次呼叫改回來
ES_SYSTEM_REQUIRED = 0x00000001   # 系統別睡（螢幕仍可關，我們不需要 ES_DISPLAY_REQUIRED）
ES_AWAYMODE_REQUIRED = 0x00000040 # Away Mode：闔蓋也繼續跑

_held = False


def _set(flags: int) -> bool:
    if not sys.platform.startswith("win"):
        return False
    try:
        import ctypes
        # 回傳 0 代表失敗；別讓它拋例外打斷主流程
        return bool(ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint(flags)))
    except Exception:
        return False


class _Holder:
    """context manager 用；直接呼叫 keep_awake() 則靠行程生命週期。"""

    def __enter__(self) -> "_Holder":
        return self

    def __exit__(self, *exc) -> None:
        release()


def keep_awake(away_mode: bool = True) -> _Holder:
    """宣告「我還在跑，別睡」。可重複呼叫，冪等。

    away_mode 預設開：闔蓋是這台進待機最常見的原因，不擋它等於白做。
    """
    global _held
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    if away_mode:
        flags |= ES_AWAYMODE_REQUIRED
    if _set(flags):
        _held = True
    elif away_mode:
        # 有些機器不吃 AWAYMODE，退回只要求系統不睡，總比完全沒有好
        _held = _set(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    return _Holder()


def release() -> None:
    """解除宣告，讓系統恢復正常的睡眠判斷。"""
    global _held
    if _held:
        _set(ES_CONTINUOUS)
        _held = False


def held() -> bool:
    return _held


if __name__ == "__main__":
    if "--hold" in sys.argv:
        keep_awake()
        print("holding wake lock; Ctrl+C to release", flush=True)
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass
        finally:
            release()
    else:
        print(__doc__)
