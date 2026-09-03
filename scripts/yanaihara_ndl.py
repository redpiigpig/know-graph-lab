#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""矢內原忠雄《帝国主義下の台湾》（岩波 1929）：NDL 掃描 → OCR → 日文全文。

這一卷是矢內原全集裡最該做的一本，也是唯一版權全球乾淨的一本：1929 年出版 →
連 URAA 回溯都追不到（[[project_uchimura_yanaihara]] 的版權表）。NDL 數位典藏
pid 1191101 是インターネット公開，IIIF manifest 201 コマ。

三步，各自可重跑：
  --fetch  逐コマ抓 JPEG（節流；連兩次 429 就停，[[feedback_ocr_two_strike_quota]]）
  --pdf    把 JPEG 併成 PDF —— 只為了接上既有的 OCR 鏈（ocr_pdf_to_text 吃 PDF，
           key 輪替與配額處理都在那裡，不必重寫一份）
  --ocr    Gemini Vision 逐段 OCR → c:/tmp/yanaihara_ndl/ocr/NNN.txt

⚠️ 舊字舊假名＋縱排：prompt 明講不要改寫成新字新假名，原樣轉錄——這本的價值有一半
在它是 1929 年的日文。

  python scripts/yanaihara_ndl.py --fetch
  python scripts/yanaihara_ndl.py --pdf
  python scripts/yanaihara_ndl.py --ocr --batch 10
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

PID = "1191101"
MANIFEST = f"https://www.dl.ndl.go.jp/api/iiif/{PID}/manifest.json"
WORK_DIR = Path("c:/tmp/yanaihara_ndl")
IMG_DIR = WORK_DIR / "img"
OCR_DIR = WORK_DIR / "ocr"
PDF_PATH = WORK_DIR / "teikoku_taiwan.pdf"
UA = "know-graph-lab/1.0 (private research library; public-domain 1929 scan)"

OCR_PROMPT = (
    "これは1929年（昭和4年）岩波書店刊『帝国主義下の台湾』（矢内原忠雄）の"
    "スキャン画像です。縦書き・旧字旧仮名遣いです。\n"
    "・本文をそのまま文字起こししてください。**旧字旧仮名を新字新仮名に直さないこと**。\n"
    "・ルビ（振り仮名）は省略。柱（ページ上部の見出し）とノンブル（ページ番号）は省略。\n"
    "・表・統計数値はそのまま行単位で書き出す。判読不能な文字は〓。\n"
    "・段落の改行は保持し、章題・節題は独立した行にすること。"
)


def _get(url: str, *, timeout: int = 60, retry_after: float = 60.0) -> bytes:
    """429 只退避重試一次就放棄——對方已經在說慢一點了，硬打只會被鎖更久
    （[[feedback_ocr_two_strike_quota]] 同精神）。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code != 429:
            raise
        print(f"  429 → {retry_after:.0f} 秒待って一度だけ再試行", flush=True)
        time.sleep(retry_after)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()


def canvas_ids(manifest: dict) -> list[str]:
    """manifest → 逐コマ的 image service id（R0000001…）。"""
    out = []
    for c in manifest["sequences"][0]["canvases"]:
        svc = c["images"][0]["resource"]["service"]["@id"]
        out.append(svc.rstrip("/").split("/")[-1])
    return out


def fetch_images(*, width: int = 1800, pause: float = 3.0) -> int:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    mpath = WORK_DIR / "manifest.json"
    if not mpath.exists():
        mpath.write_bytes(_get(MANIFEST))
    ids = canvas_ids(json.loads(mpath.read_text(encoding="utf-8")))
    print(f"コマ数：{len(ids)}", flush=True)
    strikes = 0
    got = 0
    for i, cid in enumerate(ids, 1):
        dst = IMG_DIR / f"{i:03d}.jpg"
        if dst.exists() and dst.stat().st_size > 5000:
            continue
        url = f"https://dl.ndl.go.jp/api/iiif/{PID}/{cid}/full/{width},/0/default.jpg"
        try:
            dst.write_bytes(_get(url))
            got += 1
            strikes = 0
        except urllib.error.HTTPError as e:
            # NDL は連打に敏感：429 が続いたら潔く退く
            print(f"  [{i:03d}] HTTP {e.code}", flush=True)
            strikes += 1
            if strikes >= 2:
                print("  連続 2 回失敗 → 中断（あとで再実行すれば続きから）", flush=True)
                break
            time.sleep(30)
            continue
        if i % 20 == 0:
            print(f"  …{i}/{len(ids)}", flush=True)
        time.sleep(pause)
    return got


def make_pdf() -> Path:
    from PIL import Image

    files = sorted(IMG_DIR.glob("*.jpg"))
    if not files:
        raise SystemExit("先に --fetch")
    first, *rest = [Image.open(f).convert("RGB") for f in files]
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    first.save(PDF_PATH, save_all=True, append_images=rest)
    print(f"✓ {PDF_PATH}（{len(files)} 頁, {PDF_PATH.stat().st_size / 1e6:.1f}MB）")
    return PDF_PATH


def _live_model() -> str:
    """keeper 的 gemini_probe 會把「今天還有額度的那個 model」寫在這裡。"""
    f = SCRIPT_DIR / "state" / "gemini_live_model.txt"
    if f.exists():
        name = f.read_text(encoding="utf-8").strip()
        if name:
            return name
    return "gemini-flash-latest"      # 2.5-flash 對新帳號會 404


def run_ocr(batch: int) -> None:
    """既存の OCR チェーンに乗せる（key ローテーションと配額処理はあちら側）。"""
    import ocr_pdf_to_text as op

    OCR_DIR.mkdir(parents=True, exist_ok=True)
    total = op._pdf_page_count(PDF_PATH)
    print(f"PDF {total} 頁、{batch} 頁ずつ", flush=True)
    for start in range(1, total + 1, batch):
        end = min(start + batch - 1, total)
        dst = OCR_DIR / f"{start:03d}-{end:03d}.txt"
        if dst.exists() and dst.stat().st_size > 200:
            continue
        pages = op.ocr_pdf(PDF_PATH, model=_live_model(), pages=(start, end),
                           prompt=OCR_PROMPT)
        text = op.pages_to_text(pages)
        if not text.strip():
            # 空有兩種：Gemini 暫時掛掉（503/額度），或那幾頁真的是白頁（奧付、
            # 見返し）。分不出來，所以記次數：連三輪都空就當白頁放行，不然整本
            # 會卡在最後一張空白頁上永遠等不到「OCR 跑完」。
            miss = OCR_DIR / f"{start:03d}-{end:03d}.miss"
            n = int(miss.read_text(encoding="utf-8").strip() or 0) + 1 if miss.exists() else 1
            miss.write_text(str(n), encoding="utf-8")
            if n >= 3:
                dst.write_text("（このコマに本文なし）", encoding="utf-8")
                print(f"  [{start}-{end}] 三輪とも空 → 白頁として確定", flush=True)
                continue
            print(f"  [{start}-{end}] 空（{n}/3 回目）→ 中断、次のラウンドで再試行", flush=True)
            break
        dst.write_text(text, encoding="utf-8")
        print(f"  ✓ {dst.name} {len(text):,} 字", flush=True)


def auto(pause: float, batch: int) -> None:
    """抓圖→併 PDF→OCR，跑到哪算哪。給 fleet keeper 掛 lane 用：

    NDL 會 429、Gemini 會 503，兩邊都是「等一下再來」的錯，所以這支不重試到死，
    做得動就往前一步，做不動就退出來讓 keeper 下一輪再探。
    """
    ids = json.loads((WORK_DIR / "manifest.json").read_text(encoding="utf-8"))
    total = len(canvas_ids(ids))
    have = len(list(IMG_DIR.glob("*.jpg"))) if IMG_DIR.is_dir() else 0
    if have < total:
        print(f"画像 {have}/{total} → 続きを取得", flush=True)
        fetch_images(pause=pause)
        have = len(list(IMG_DIR.glob("*.jpg")))
    if have < total:
        print(f"まだ {have}/{total}；次のラウンドで続行", flush=True)
        return
    if not PDF_PATH.exists() or PDF_PATH.stat().st_mtime < max(
            f.stat().st_mtime for f in IMG_DIR.glob("*.jpg")):
        make_pdf()
    run_ocr(batch)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--auto", action="store_true",
                    help="抓圖→PDF→OCR 一氣呵成，做不動就退（keeper lane 用）")
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--width", type=int, default=1800)
    ap.add_argument("--pause", type=float, default=3.0, help="コマ間の待ち（秒）")
    a = ap.parse_args()
    if a.fetch:
        print(f"取得 {fetch_images(width=a.width, pause=a.pause)} コマ；"
              f"手元に {len(list(IMG_DIR.glob('*.jpg')))} コマ")
    if a.pdf:
        make_pdf()
    if a.ocr:
        run_ocr(a.batch)
    if a.auto:
        auto(a.pause, a.batch)
    if not (a.fetch or a.pdf or a.ocr or a.auto):
        ap.error("--fetch / --pdf / --ocr / --auto のいずれか")


if __name__ == "__main__":
    main()
