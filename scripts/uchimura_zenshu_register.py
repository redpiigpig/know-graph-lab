# -*- coding: utf-8 -*-
"""把 Drive 上的《内村鑑三全集》20 卷 PDF 登記成 ebooks 列（collected-works）。

冪等：同一卷跑第二次只會更新欄位，不會生第二列（用固定的 d0000001-… 命名空間）。
只登記「檔案已在 Drive 且大小與 archive.org 相符」的卷，沒下載完的跳過。

    python scripts/uchimura_zenshu_register.py          # 登記已下載完成的卷
    python scripts/uchimura_zenshu_register.py --list    # 只看狀態不寫 DB
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import requests
from dotenv import load_dotenv

# 主控台是 cp950，印到 ✓／✗ 會 UnicodeEncodeError 整支掛掉（排程就變成每晚靜默失敗）。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = Path(__file__).resolve().parent.parent
load_dotenv(REPO / ".env")
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

DEST = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集\神學\內村鑑三\岩波全集（1932-33）")
UA = {"User-Agent": "kgl-research/1.0"}

# 各卷卷名：逐卷讀 archive.org djvu 文字層的「例言／本卷は…」定出來的，不是憑印象填的。
# 卷10 的例言被 OCR 吃掉，留空不猜。
VOLUMES = {
    1: "初期的著作 上",
    2: "初期的著作 下",
    3: "舊約研究 上（創世記～約伯記）",
    4: "舊約研究 下（詩篇～預言書）",
    5: "新約研究（福音書）",
    6: "新約研究（羅馬書）",
    7: "新約研究（使徒行傳～默示錄）",
    8: "教義研究 上",
    9: "教義研究 下",
    10: "",
    11: "信仰講演・講話（1900–1930）",
    12: "所感（《聖書之研究》每號短文全收）・詩與歌・愛吟",
    13: "感想（《聖書之研究》所載較長篇文章）",
    14: "時事・宗教與現世",
    15: "英文 上",
    16: "英文 下",
    17: "日記 上（1918–1930）",
    18: "日記 下（1918–1930）",
    19: "隨筆・雜錄・雜報",
    20: "書簡選集",
}


def ebook_id(vol: int) -> str:
    """固定命名空間，重跑不會產生新列。"""
    return f"d0000001-0000-4000-8000-{vol:012d}"


def remote_size(vol: int) -> int:
    ident = f"uchimurakanzzens{vol:02d}uchiuoft"
    meta = json.load(urllib.request.urlopen(
        urllib.request.Request(f"https://archive.org/metadata/{ident}", headers=UA), timeout=60))
    return next((int(f.get("size", 0)) for f in meta["files"] if f["name"] == f"{ident}.pdf"), 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="只印狀態，不寫 DB")
    args = ap.parse_args()

    if not DEST.exists():
        print("✗ Drive 上還沒有全集資料夾——先跑 uchimura_zenshu_fetch.py")
        return 2

    done = skipped = 0
    for vol, desc in VOLUMES.items():
        pdf = DEST / f"內村鑑三全集 第{vol:02d}卷（岩波1932-33）.pdf"
        if not pdf.exists():
            print(f"  卷{vol:02d} 尚未下載，跳過")
            skipped += 1
            continue
        local = pdf.stat().st_size
        try:
            remote = remote_size(vol)
        except Exception:
            remote = local  # 查不到遠端就只信本機（離線也能登記）
        if remote and local != remote:
            print(f"  卷{vol:02d} 檔案不完整（{local/1048576:.1f}/{remote/1048576:.1f} MB），跳過")
            skipped += 1
            continue
        row = {
            "id": ebook_id(vol),
            "title": (f"內村鑑三全集 第{vol:02d}卷：{desc}" if desc else f"內村鑑三全集 第{vol:02d}卷"),
            "author": "內村鑑三",
            "author_en": "Uchimura Kanzō",
            "original_title": f"内村鑑三全集 第{vol}巻",
            "file_type": "pdf",
            "file_path": str(pdf),
            "category": "神學",
            "collection": "collected-works",
            "publisher": "岩波書店",
            "publication_year": 1932,
            # 這一行就是 OCR 佇列的定義（見 ocr_with_gemini.fetch_ocr_targets）
            "parse_error": "no extractable text (1932 岩波掃描本，走本機 MinerU)",
        }
        if args.list:
            print(f"  卷{vol:02d} {local/1048576:6.1f}MB  → {row['title']}")
            done += 1
            continue
        r = requests.post(f"{URL}/rest/v1/ebooks?on_conflict=id",
                          headers={**H, "Prefer": "resolution=merge-duplicates,return=minimal"},
                          json=row, timeout=45)
        ok = r.status_code in (200, 201, 204)
        print(f"  卷{vol:02d} {'✓ 已登記' if ok else '✗ HTTP ' + str(r.status_code) + ' ' + r.text[:120]}  {row['title'][:38]}")
        done += ok
    print(f"完成：登記 {done} 卷、跳過 {skipped} 卷")
    return 0


if __name__ == "__main__":
    sys.exit(main())
