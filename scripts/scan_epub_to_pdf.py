"""把「整本都是掃描圖、沒有文字層」的 epub 組成 PDF，好讓它走既有的 OCR 佇列。

為什麼需要這一支：有些掃描書是包成 epub 而不是 PDF 的。parse_worker 抽不到文字，
標成 `no extractable text`，於是**混進 OCR 佇列**——但 MinerU 只吃 PDF，撈到只會
回 exit 1 退件，這本就永遠卡著。轉成 PDF 之後 `file_path`／`file_type` 一改，
既有的 OCR 佇列就認得它了，不必為 epub 另開一條 OCR 路。

🚨 先確認「真的沒文字」再用這支。ebooklib 讀不動但正文其實都在的 epub 也會被標成
   `no extractable text`（見 parse_worker._epub_docs_from_zip），那種要修解析、
   不是拿去 OCR。判準：zip 直讀所有 html 抽出的字數——上千字就是解析問題。
🚨 照 HTML 裡 <img> 的出現順序，不是檔名排序：`index-10_1.jpg` 會排到
   `index-2_1.jpg` 前面，頁序就整個亂了，而產出的 PDF 看起來完全正常。

用法：
    python scripts/scan_epub_to_pdf.py <來源.epub> <輸出.pdf>
"""
import os
import re
import sys
import zipfile

import fitz  # PyMuPDF


def image_order(zf: zipfile.ZipFile) -> list[str]:
    """照 HTML 裡 <img src> 的出現順序回傳 zip 內的圖片路徑。"""
    names = zf.namelist()
    order: list[str] = []
    for doc in sorted(n for n in names if n.lower().endswith((".html", ".xhtml", ".htm"))):
        base = doc.rsplit("/", 1)[0] + "/" if "/" in doc else ""
        html = zf.read(doc).decode("utf-8", "replace")
        for src in re.findall(r'src=["\']([^"\']+)["\']', html):
            cand = os.path.normpath(base + src).replace(os.sep, "/")
            if cand not in names:
                cand = next((n for n in names if n.endswith("/" + src) or n == src), None)
            if cand and cand not in order:
                order.append(cand)
    return order


def build(src_epub: str, dst_pdf: str) -> int:
    """一頁一張圖、原尺寸貼上不重新取樣。回傳頁數。"""
    zf = zipfile.ZipFile(src_epub)
    order = image_order(zf)
    if not order:
        raise SystemExit("⛔ HTML 裡找不到任何 <img>，這本不是這種掃描 epub")

    doc = fitz.open()
    for name in order:
        data = zf.read(name)
        pix = fitz.Pixmap(data)
        page = doc.new_page(width=pix.width, height=pix.height)
        page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), stream=data)
    doc.save(dst_pdf, deflate=True)
    doc.close()
    return len(order)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    n = build(sys.argv[1], sys.argv[2])
    print(f"✓ {n} 頁　{os.path.getsize(sys.argv[2]) / 1024 / 1024:.1f} MB")
