# -*- coding: utf-8 -*-
"""《基督教典外文獻》十冊重 OCR —— MinerU（CPU）逐冊跑，輸出夾留著。

為什麼不直接用 `mineru_ocr.py run --pdf`：那支用 `TemporaryDirectory`，跑完
`middle.json` 就沒了。而這套書的下游（切作品、定界、撿註腳與印刷頁碼）要回頭
讀 `middle.json` 的 `discarded_blocks` 與 block 型別，所以輸出夾一定要留。

CPU 而非 GPU：那張 6GB 的卡同時只能跑一個，多半被夜班佇列佔著（見
`scripts/state/mineru_gpu.lock`）。CPU 慢但不搶，實測約 8 秒／頁。
🚨 不可以 Stop-Process 殺掉別人的 MinerU。

逐冊存檔：這台筆電會通勤休眠，做完一冊就落地，下次跑自動跳過已完成的冊。

用法：
    python scripts/ocr_cct_apocrypha.py --part nt          # 新約篇 4 冊
    python scripts/ocr_cct_apocrypha.py --part ot          # 舊約篇 6 冊
    python scripts/ocr_cct_apocrypha.py --part nt --force  # 重跑（覆蓋已完成）
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

MINERU_EXE = REPO / "_mineru_venv" / "Scripts" / "mineru.exe"
SRC_DIR = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館\世界宗教\基督教"
               r"\基督教典外文獻 (10 冊)")
OUT_ROOT = REPO / "output" / "apocrypha-ocr"

# 🚨 同夾另有「王曉朝，基督教典外文獻─…」四本，那是**不同譯本**且本身有問題
#    （頁 9 / chunks 100 對不上），刻意不收進來。認檔名要認得出差別。
VOLUMES = {
    "nt": [(f"基督教典外文獻-新約篇-第{i}冊", f"cct-nt-{i}") for i in range(1, 5)],
    "ot": [(f"基督教典外文獻-舊約篇-第{i}冊", f"cct-ot-{i}") for i in range(1, 7)],
}


BATCH = 40          # 每批頁數，見 run_one 的說明


def page_count(pdf: Path) -> int:
    import pypdf
    return len(pypdf.PdfReader(str(pdf)).pages)


def run_batch(pdf: Path, out_dir: Path, start: int, end: int) -> bool:
    """跑一批頁（0-based、含頭含尾）。已經有 middle.json 就跳過。"""
    if sorted(out_dir.rglob("*_middle.json")):
        return True
    out_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.setdefault("MINERU_MODEL_SOURCE", "huggingface")
    env["MINERU_DEVICE_MODE"] = "cpu"          # 不佔顯存 → 不排 GPU 鎖
    argv = [str(MINERU_EXE), "-p", str(pdf), "-o", str(out_dir),
            "-b", "pipeline", "-m", "ocr", "-l", "ch", "-s", str(start), "-e", str(end)]
    t0 = time.time()
    proc = subprocess.run(argv, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    el = time.time() - t0
    if proc.returncode != 0 or not sorted(out_dir.rglob("*_middle.json")):
        from mineru_ocr import last_lines
        print(f"   ⛔ 頁 {start}–{end} 失敗（exit {proc.returncode}, {el:.0f}s）："
              f"{last_lines(proc.stderr, proc.stdout, n=2)}", flush=True)
        return False
    print(f"   ✓ 頁 {start}–{end}　{el:.0f}s（{el / (end - start + 1):.1f}s/頁）", flush=True)
    return True


def run_one(stem: str, slug: str, force: bool) -> bool:
    """跑一冊 —— 切成小批。回傳 True＝這一冊每一批都有 middle.json。

    🚨 為什麼要切批：2026-09-18 第一冊整本一次送進去，跑了 91 分鐘後死在 MinerU
    自己的 task timeout，**一頁都沒留下**。當時機器上另有兩個 MinerU 在跑，
    OCR-det 從 66s/it 掉到 166s/it，估計時間一路漲到 17 小時。單跑實測是
    9.9s/頁（40 頁 394 秒），所以那次純粹是 CPU 搶破頭。

    切成 40 頁一批有兩個好處：每批約 6–7 分鐘，遠低於任何內部逾時；而且別人的
    夜班佇列半路起來時，最多賠掉一批而不是整本。批次夾留著就等於斷點。
    """
    pdf = SRC_DIR / f"{stem}.pdf"
    out_dir = OUT_ROOT / slug
    if force:
        import shutil
        shutil.rmtree(out_dir, ignore_errors=True)
    if not pdf.exists():
        # G: 整個不見了是 Drive 卡住（先 Test-Path 再重啟 GoogleDriveFS），
        # 單一檔案不見才是這一冊的問題。
        if not Path("G:\\").exists():
            print("⛔ G: 掛不上 —— Drive 卡住了，先重啟 GoogleDriveFS", flush=True)
            raise SystemExit(3)
        print(f"✗ {slug} 找不到 PDF：{pdf}", flush=True)
        return False

    total = page_count(pdf)
    batches = [(s, min(s + BATCH - 1, total - 1)) for s in range(0, total, BATCH)]
    print(f"▶ {slug} ← {pdf.name}　{total} 頁 / {len(batches)} 批", flush=True)
    t0 = time.time()
    ok = True
    for s, e in batches:
        if not run_batch(pdf, out_dir / f"b{s:04d}", s, e):
            ok = False
    if not ok:
        print(f"⛔ {slug} 有批次沒跑成，先不併檔（重跑會接著做沒完成的批）", flush=True)
        return False

    pages = merge_batches(slug, out_dir, batches)
    from mineru_ocr import to_chunks, write_jsonl
    chunks = to_chunks(pages)
    write_jsonl(chunks, out_dir / f"{slug}.jsonl")
    printed = sum(1 for c in chunks if c["printed_page"])
    notes = sum(len(p["footnotes"]) for p in pages.values())
    print(f"✓ {slug} {len(pages)} 頁　{(time.time() - t0) / 60:.0f} 分　"
          f"印刷頁碼 {printed}/{len(pages)}　註腳 {notes} 條", flush=True)
    return True


def merge_batches(slug: str, out_dir: Path, batches: list[tuple[int, int]]) -> dict[int, dict]:
    """把各批的 middle.json 併回一冊，並存一份合併後的 middle.json 供下游用。

    🚨 `page_idx` 是**每一批各自從 0 開始**的（`-s 100` 那批的第一頁 page_idx 也是
    0），所以併檔一定要加上該批的起始頁。不加的話每批都蓋在 0–39，整本只剩最後
    一批——而且頁數看起來「正常」，因為每一頁都還在，只是全部擠在前 40 個索引。
    """
    from mineru_ocr import pages_from_middle
    merged_info, pages = [], {}
    for s, e in batches:
        mids = sorted((out_dir / f"b{s:04d}").rglob("*_middle.json"))
        mid = json.loads(mids[0].read_text(encoding="utf-8"))
        info = mid.get("pdf_info") or []
        if len(info) != e - s + 1:
            print(f"   ⚠ 批 {s}–{e} 宣告 {e - s + 1} 頁、實得 {len(info)} 頁", flush=True)
        for p in info:
            p["page_idx"] = int(p.get("page_idx", 0)) + s
            merged_info.append(p)
        pages.update(pages_from_middle({"pdf_info": info}))
    (out_dir / f"{slug}_middle.json").write_text(
        json.dumps({"pdf_info": merged_info}, ensure_ascii=False), encoding="utf-8")
    return pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["nt", "ot"], required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", type=int, nargs="*", help="只跑第幾冊（1-based）")
    args = ap.parse_args()

    try:
        from keep_awake import keep_awake
        keep_awake()
    except Exception:
        pass

    vols = VOLUMES[args.part]
    if args.only:
        vols = [v for i, v in enumerate(vols, 1) if i in args.only]
    ok = 0
    for stem, slug in vols:
        if run_one(stem, slug, args.force):
            ok += 1
    print(f"\n=== {args.part}：{ok}/{len(vols)} 冊有 middle.json ===", flush=True)
    return 0 if ok == len(vols) else 1


if __name__ == "__main__":
    raise SystemExit(main())
