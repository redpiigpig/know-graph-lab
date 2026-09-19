"""把「一張裝兩個書頁」的掃描 PDF 拆成一頁一個書頁。

館藏裡的掃描本有兩種 2-up：
  - **上下疊**（橫躺的紙，要先轉正）→ 走 `scan_prep.py`，那支處理旋轉與半頁順序；
  - **左右並排**（書攤平橫拍，正立）→ 走這支，只要從中線切開。

為什麼要拆：不拆的話一張上有**兩個印刷頁碼**，頁碼一致性檢查必然過不了，
撿回來的頁碼會被當成雜訊清掉。Geertz《Local Knowledge》第一版 OCR 就是這樣，
126 頁只留下 16 個頁碼、每頁 4,913 字（正常單頁約 2,500），兩個數字都在喊 2-up。

🚨 **中線不要直接取寬度的一半。** 書攤平拍照時裝訂線不見得落在正中央；取中央
±12% 範圍內**最暗的一欄**（書溝的陰影）才準，整區都不夠暗才退回正中間。

🚨 **存檔一定要 `garbage=4, clean=True`。** 每個半頁都引用整張來源掃描圖，
不做跨物件去重的話檔案會膨脹好幾倍，而且看起來完全正常。

    python scripts/split_two_up_pdf.py --src <原檔> --out <拆頁檔>
    python scripts/split_two_up_pdf.py --src <原檔> --out <拆頁檔> --order rl   # 直排書右頁在前
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8")


def find_split_x(page: fitz.Page, band: float = 0.12) -> float:
    """回傳中線的 x（頁面座標）。取中央 ±band 內最暗的一欄。"""
    pix = page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35), colorspace=fitz.csGRAY)
    w, h = pix.width, pix.height
    lo, hi = int(w * (0.5 - band)), int(w * (0.5 + band))
    samples = pix.samples
    best_x, best_v = None, None
    for x in range(lo, hi):
        total = sum(samples[y * pix.stride + x] for y in range(0, h, 4))
        if best_v is None or total < best_v:
            best_v, best_x = total, x
    # 整區都不夠暗（沒有明顯書溝）就用正中間
    avg = best_v / max(1, len(range(0, h, 4)))
    if best_x is None or avg > 200:
        return page.rect.width / 2
    return page.rect.width * best_x / w


def split(src: Path, out: Path, order: str = "lr") -> tuple[int, int]:
    doc = fitz.open(str(src))
    new = fitz.open()
    for page in doc:
        r = page.rect
        mid = find_split_x(page)
        left = fitz.Rect(r.x0, r.y0, mid, r.y1)
        right = fitz.Rect(mid, r.y0, r.x1, r.y1)
        halves = [left, right] if order == "lr" else [right, left]
        for clip in halves:
            p = new.new_page(width=clip.width, height=clip.height)
            p.show_pdf_page(p.rect, doc, page.number, clip=clip)
    out.parent.mkdir(parents=True, exist_ok=True)
    new.save(str(out), garbage=4, clean=True, deflate=True)
    n_src, n_out = doc.page_count, new.page_count
    doc.close()
    new.close()
    return n_src, n_out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--order", choices=["lr", "rl"], default="lr",
                    help="lr＝左頁在前（橫排書），rl＝右頁在前（直排書）")
    args = ap.parse_args()
    src, out = Path(args.src), Path(args.out)
    n_src, n_out = split(src, out, args.order)
    print(f"{src.name}：{n_src} 頁 → {n_out} 頁")
    print(f"  {src.stat().st_size / 1048576:.1f} MB → {out.stat().st_size / 1048576:.1f} MB")
    print(f"  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
