# -*- coding: utf-8 -*-
"""讀 Drive 上的 `_chunks/{ebook_id}.jsonl` —— 全文正本的唯一入口。

2026-09-16 `ebook_chunks` 退場（1,005,363 列在 Supabase 免費層獨自佔 503 MB，
而它只存每段前 100 字），所有要看 chunk 的腳本都改讀這裡。
見 database/drop-ebook-chunks-2026-09-16.sql。

會抽成一支共用模組，是因為「讀不到檔案」有兩種完全不同的意思，而搞混過不只一次：

  沒有這本的 .jsonl        → 這本真的還沒轉錄，可以跳過
  整個 _chunks 目錄不見了  → **Drive 卡住**，跟書無關；再掃下去會把全館判成空白

所以 `require_dir()` 對後者直接拋例外中止，`scan()` 一定印分母（讀到幾本／共幾本），
全軍覆沒也拋例外。見 [[feedback_silent_zero_is_a_bug]] 與 [[reference_drive_g_unmount_fix]]。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or "G:/我的雲端硬碟/資料/知識圖工作室/_chunks")


def require_dir() -> Path:
    """確認 _chunks 目錄在。不在就中止 —— 那是 Drive 卡住，不是資料沒了。"""
    if not CHUNKS_DIR.exists():
        raise RuntimeError(
            f"讀不到 {CHUNKS_DIR} —— Drive 卡住了。先 Test-Path 'G:\\我的雲端硬碟'，"
            "不通就 Stop-Process GoogleDriveFS 再跑 launch.bat（約 20 秒掛回來）。"
            "中止：讀不到檔案會讓每一本都看起來是空的。")
    return CHUNKS_DIR


def path_for(ebook_id: str) -> Path:
    return CHUNKS_DIR / f"{ebook_id}.jsonl"


def load(ebook_id: str) -> list[dict] | None:
    """一本書的 chunks，依檔案順序。

    回傳 None＝這本沒有 .jsonl（還沒轉錄）；回傳 [] ＝檔案在但內容是空的。
    兩者不可混為一談，所以不用 `or []` 收斂。
    """
    require_dir()
    p = path_for(ebook_id)
    if not p.exists():
        return None
    out: list[dict] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue          # 單行壞掉不該拖垮整本
    return out


def scan(ebook_ids, *, quiet: bool = False) -> dict[str, list[dict]]:
    """一批書 → {ebook_id: chunks}。沒有 .jsonl 的書不會出現在結果裡。

    🚨 一定印分母。稽核回「0 筆」有一半機率是迴圈根本沒跑到。
    """
    require_dir()
    ids = list(ebook_ids)
    got: dict[str, list[dict]] = {}
    for bid in ids:
        rows = load(bid)
        if rows:
            got[bid] = rows
    if not quiet:
        print(f"  讀了 {len(got):,}/{len(ids):,} 本的 JSONL"
              f"（{len(ids) - len(got):,} 本沒有檔案或是空的）", flush=True)
    if ids and not got:
        raise RuntimeError(
            f"{len(ids):,} 本一本都讀不到 JSONL —— 這是環境問題不是書的問題，中止。")
    return got


def all_ids() -> list[str]:
    """_chunks 目錄裡所有 ebook_id（檔名去副檔名）。"""
    return sorted(p.stem for p in require_dir().glob("*.jsonl"))
