#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依 accs_volume_config.json 逐卷 OCR（呼叫 ingest_accs_genesis.py）。

預設只跑 status=ready（單書卷）；NT 優先。多書卷（needs_boundaries）待定界後另跑。
  python -X utf8 scripts/accs_ocr_run.py --engine gemini --batch 4 [--testament NT] [--only mat]
每卷 --resume。

額度政策＝**兩次連續失敗才退**（使用者定調）：單卷退出非 0 先跳過換下一卷，連續兩卷都
失敗才視為 provider 整體乾掉、停整批交給外層 runner 重探。2026-08-17 前是「一卷失敗就停
整批」，結果約翰福音額度乾之後，排在它後面的希伯來書／以賽亞書等於永遠排不到（DB 0 筆）。
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "accs_volume_config.json"

# book_code → 繁中書名（source_vol 用；對齊 bible_books.name_zh）
NAME = {
    "mat": "馬太福音", "mrk": "馬可福音", "luk": "路加福音", "jhn": "約翰福音",
    "act": "使徒行傳", "rom": "羅馬書", "heb": "希伯來書", "rev": "啟示錄",
    "job": "約伯記", "psa": "詩篇", "isa": "以賽亞書",
}


def _range_pages(spec: str) -> int:
    """把 "43-300,412" 這種頁碼字串算成頁數。"""
    n = 0
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            n += int(b) - int(a) + 1
        else:
            n += 1
    return n


def _effective_pages(spec: str, pdf: str) -> int:
    """頁範圍與 PDF 實際頁數的交集頁數。開不了檔就退回純範圍頁數。"""
    want = _range_pages(spec)
    try:
        import fitz
        with fitz.open(pdf) as doc:
            total = doc.page_count
    except Exception:  # noqa: BLE001  Drive 斷線／PyMuPDF 缺席都不該擋住流程
        return want
    n = 0
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a), min(int(b), total)
            n += max(0, b - a + 1)
        elif int(part) <= total:
            n += 1
    return n


def _marker_pages(marker: Path) -> int | None:
    """.done 的內容是 "N pages"；讀不出數字就回 None（當成無法判斷，照舊跳過）。"""
    try:
        head = marker.read_text(encoding="utf-8").strip().split()[0]
        return int(head)
    except (OSError, ValueError, IndexError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="gemini", choices=["gemini", "sonnet", "haiku"])
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--testament", choices=["NT", "OT"], help="只跑此約")
    ap.add_argument("--only", help="只跑此 book_code")
    ap.add_argument("--include-multi", action="store_true",
                    help="也跑多書卷（需已補好 ranges）")
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    consecutive_fails = 0
    skipped: list[str] = []
    for vol in cfg:
        if not args.include_multi and vol["status"] != "ready":
            continue
        if args.testament and vol["testament"] != args.testament:
            continue
        if vol["ranges"] is None:
            print(f"  [skip] {vol['vol_key']} 尚未定界", flush=True)
            continue
        for rng in vol["ranges"]:
            book = rng["book"]
            if args.only and book != args.only:
                continue
            vol_name = NAME.get(book, book)
            src_vol = f"ACCS（{vol_name}）"
            # ingest_accs_genesis.py 在整卷目標頁都進 checkpoint 後會寫 .done，本意就是
            # 「讓每日排程不再重跑」，但這支 runner 從來沒讀它：58 卷全數 OCR 完之後，
            # keeper 每 30 分鐘仍把每一卷重跑一遍——不呼叫 Gemini，卻照樣把全部
            # ~29,000 列重新 upsert 進 Supabase（2026-08-25 查出）。已完成就跳過；
            # 要重做某卷，刪掉它的 .raw.done 即可。
            done_marker = (Path("c:/tmp" if sys.platform == "win32" else "/tmp")
                           / f"accs_{book}_{Path(vol['pdf']).stem}.raw.done")
            if done_marker.exists():
                # .done 只代表「寫檔當時的 --pages 都跑完了」。範圍後來被改寬（定界
                # 修正、合刊重切）時，舊標記就變成謊報，而只看檔案在不在會讓那一卷
                # 永遠跳過。2026-08-27 雅歌就是這樣：設定 120 頁、標記只記 36 頁，
                # 卻照樣被當成完成，DB 只有 2/8 章。所以要對頁數。
                recorded = _marker_pages(done_marker)
                # 設定的頁範圍可能超出 PDF 結尾（雅歌設 437-556、檔案只有 472 頁），
                # 這時標記記的頁數本來就會比設定少。拿沒被掃進來的頁去比，會判成
                # 過期→刪標記→重跑→再寫回同樣的頁數，每 30 分鐘空轉一次。
                # 所以要跟「範圍與 PDF 實際頁數的交集」比，不是跟設定比。
                want = _effective_pages(rng["pages"], vol["pdf"])
                if recorded is not None and want and recorded < want:
                    print(f"  [stale] {book} 標記只記 {recorded} 頁、設定要 {want} 頁"
                          f" → 標記過期，重跑補齊", flush=True)
                    done_marker.unlink()
                else:
                    print(f"  [skip] {book} 全卷已完成 → 跳過"
                          f"（要重做請刪 {done_marker.name}）", flush=True)
                    continue
            print(f"\n=== {book}  {rng['pages']}  {os.path.basename(vol['pdf'])} ===", flush=True)
            # 來源在 Google Drive 虛擬磁碟（G:）上，Drive 崩潰／重連時整個磁碟會消失。
            # 沒這道預檢，PyMuPDF 會對每一頁噴 "page not in document"，一卷燒掉幾百頁
            # 才輪到兩次失敗停批（2026-08-18 實測 Drive 掛掉 → act 連噴 25 批）。
            pdf_path = Path(vol["pdf"])
            if not pdf_path.exists():
                anchor_dir = Path(pdf_path.anchor)
                mounted = anchor_dir.exists() and any(anchor_dir.iterdir())
                if not mounted:
                    print(f"  [bail] 來源磁碟 {pdf_path.anchor} 未掛載"
                          f"（Google Drive 斷線？）→ 停整批，待掛回後續傳", flush=True)
                    return 1
                consecutive_fails += 1
                skipped.append(book)
                print(f"  [skip] 找不到來源 PDF {pdf_path.name} → 換下一卷", flush=True)
                if consecutive_fails >= 2:
                    print(f"  [bail] 連續 2 卷來源不可用 → 停整批"
                          f"（本批已跳過：{', '.join(skipped)}）", flush=True)
                    return 1
                continue
            cmd = [
                sys.executable, "-X", "utf8", str(ROOT / "ingest_accs_genesis.py"),
                "--pdf", vol["pdf"], "--book", book, "--pages", rng["pages"],
                "--source-vol", src_vol, "--engine", args.engine,
                "--batch", str(args.batch), "--resume", "--sleep", "1",
            ]
            rc = subprocess.run(cmd).returncode
            if rc == 0:
                consecutive_fails = 0
                continue
            consecutive_fails += 1
            skipped.append(book)
            if consecutive_fails >= 2:
                print(f"  [bail] {book} 退出碼 {rc}；連續 2 卷失敗＝provider 整體乾掉"
                      f" → 停整批，待重探續傳（本批已跳過：{', '.join(skipped)}）", flush=True)
                return 1
            print(f"  [skip] {book} 退出碼 {rc}（多半額度乾）→ 換下一卷，"
                  f"本卷 checkpoint 保留待續傳", flush=True)
    if skipped:
        print(f"\n本批跑完，跳過 {len(skipped)} 卷待續傳：{', '.join(skipped)}", flush=True)
        return 0
    print("\n本批 OCR 全數完成或無可跑項", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
