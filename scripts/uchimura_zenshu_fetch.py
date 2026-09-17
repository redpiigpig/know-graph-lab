# -*- coding: utf-8 -*-
"""把 archive.org 的《内村鑑三全集》（岩波 1932–33）20 卷 PDF 下載到 Drive。

canonical 位置：G:\\我的雲端硬碟\\資料\\知識圖工作室\\全集\\神學\\內村鑑三\\岩波全集（1932-33）\\
下載即校驗大小；已存在且大小相符就跳過（可重跑續傳）。

    python scripts/uchimura_zenshu_fetch.py            # 全部 20 卷
    python scripts/uchimura_zenshu_fetch.py --vols 1 2 # 只抓指定卷
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

DEST = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集\神學\內村鑑三\岩波全集（1932-33）")
UA = {"User-Agent": "kgl-research/1.0 (personal digital library)"}


def ident(vol: int) -> str:
    return f"uchimurakanzzens{vol:02d}uchiuoft"


def remote_pdf(vol: int) -> tuple[str, int]:
    """回傳 (下載網址, 遠端位元組數)。"""
    url = f"https://archive.org/metadata/{ident(vol)}"
    meta = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
    name = f"{ident(vol)}.pdf"
    size = next((int(f.get("size", 0)) for f in meta["files"] if f["name"] == name), 0)
    if not size:
        raise RuntimeError(f"卷{vol} 找不到 PDF")
    return f"https://archive.org/download/{ident(vol)}/{name}", size


def fetch(vol: int) -> str:
    dest = DEST / f"內村鑑三全集 第{vol:02d}卷（岩波1932-33）.pdf"
    url, size = remote_pdf(vol)
    if dest.exists() and dest.stat().st_size == size:
        return f"卷{vol:02d} 已存在且大小相符（{size/1048576:.1f}MB），跳過"
    tmp = dest.with_suffix(".part")
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, tmp.open("wb") as fh:
                while chunk := r.read(1 << 20):
                    fh.write(chunk)
            got = tmp.stat().st_size
            if got != size:
                raise RuntimeError(f"大小不符 遠端={size} 本機={got}")
            tmp.replace(dest)
            return f"卷{vol:02d} ✓ {got/1048576:.1f}MB → {dest.name}"
        except Exception as e:  # 斷網／429 就退一步再試
            if tmp.exists():
                tmp.unlink()
            if attempt == 4:
                return f"卷{vol:02d} ✗ 四次都失敗：{e}"
            time.sleep(20 * attempt)
    return f"卷{vol:02d} ✗"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vols", type=int, nargs="*", default=list(range(1, 21)))
    args = ap.parse_args()
    if not DEST.parent.parent.exists():
        print("✗ Drive 沒掛（G: 不見了）——先重啟 GoogleDriveFS 再跑", flush=True)
        return 2
    DEST.mkdir(parents=True, exist_ok=True)
    bad = 0
    for v in args.vols:
        line = fetch(v)
        print(line, flush=True)
        bad += line.count("✗")
    total = sum(f.stat().st_size for f in DEST.glob("*.pdf"))
    print(f"完成：{len(list(DEST.glob('*.pdf')))} 卷 / {total/1073741824:.2f} GB，失敗 {bad}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
