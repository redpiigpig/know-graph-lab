# -*- coding: utf-8 -*-
"""量 PDF 的實際頁次，回填計畫書目錄的頁碼。

目錄頁碼不能用手改：正文一動（例如加了二十四條腳註）每一節都會位移，
而目錄本身也佔頁，改了目錄又會再位移一次。流程固定是
    build_proposal_docx.py → LibreOffice 轉 PDF → 本腳本量測回填 → 再建一次
本腳本負責中間那一步，並會自己判斷要不要再跑一輪（回填後頁數若變了就要）。

🚨 量測要抓「標題自己那一頁」，不是目錄裡提到它的那一頁。目錄頁一定排在前面，
   直接找字串會全部量成目錄頁。所以一律從目錄頁之後開始找。

  python -X utf8 scripts/proposal_toc_pages.py <md 檔>
"""
import re
import subprocess
import sys
from pathlib import Path

SOFFICE = r"C:/Program Files/LibreOffice/program/soffice.exe"
TMP = Path("C:/tmp")
BUILD = Path(__file__).resolve().parent / "build_proposal_docx.py"

# 目錄裡的項目 → 在正文中對應的標題文字
ITEMS = [
    ("摘要", "摘要"),
    ("Abstract", "Abstract"),
    ("前言", "前言"),
    ("一、研究背景與問題意識", "一、研究背景與問題意識"),
    ("二、文獻回顧與探討", "二、文獻回顧與探討"),
    ("三、研究設計：方法與範圍", "三、研究設計：方法與範圍"),
    ("四、論文架構（章節安排）", "四、論文架構（章節安排）"),
    ("五、研究時程", "五、研究時程"),
    ("六、預期研究成果與貢獻", "六、預期研究成果與貢獻"),
    ("七、結論", "七、結論"),
    ("徵引書目", "徵引書目"),
    ("附錄　十個月研究工作計畫", "附錄"),
]


def to_pdf(docx):
    out = TMP / (docx.stem + ".pdf")
    out.unlink(missing_ok=True)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf",
                    "--outdir", str(TMP), str(docx)],
                   capture_output=True, timeout=300)
    if not out.exists():
        sys.exit(f"🚨 轉 PDF 失敗：{out}")
    return out


def measure(pdf):
    """回傳 {目錄項目: 頁次}。

    🚨 兩個一定會踩的坑：
      1. 摘要與 Abstract 排在**目錄之前**，用「從目錄頁往後找」會整個漏掉。
      2. 只有 摘要／Abstract／目錄／前言／徵引書目／附錄 會另起一頁，
         中間各節接排在頁中間，用「頁首是不是這個標題」會全部找不到。
    所以：跳過目錄頁本身，其餘每頁逐行找行首相符的那一行。
    """
    import fitz
    doc = fitz.open(pdf)
    pages = [p.get_text() for p in doc]
    doc.close()
    toc_page = next((i for i, t in enumerate(pages)
                     if t.strip().startswith("目錄")), -1)
    found = {}
    for label, needle in ITEMS:
        for i, t in enumerate(pages):
            if i == toc_page:
                continue
            if any(ln.strip().startswith(needle) for ln in t.splitlines()):
                found[label] = i + 1
                break
    return found, len(pages)


def backfill(md, nums):
    text = md.read_text(encoding="utf-8")
    for label, page in nums.items():
        pat = re.compile(rf"^({re.escape(label)}[^\n　]*)　　\d+$", re.M)
        if not pat.search(text):
            print(f"  ⚠ 目錄裡找不到「{label}」，未回填")
            continue
        text = pat.sub(lambda m: f"{m.group(1)}　　{page}", text)
    md.write_text(text, encoding="utf-8")


def build(md):
    subprocess.run([sys.executable, "-X", "utf8", str(BUILD), str(md)],
                   capture_output=True, timeout=600)
    return md.with_suffix(".docx")


def main():
    md = Path(sys.argv[1])
    for rnd in range(1, 4):
        pdf = to_pdf(build(md))
        nums, total = measure(pdf)
        print(f"第 {rnd} 輪：{total} 頁　" +
              "　".join(f"{k[:6]}={v}" for k, v in nums.items()))
        before = md.read_text(encoding="utf-8")
        backfill(md, nums)
        if md.read_text(encoding="utf-8") == before:
            print("頁碼已收斂。")
            return
    print("⚠ 三輪仍未收斂，請人工確認。")


if __name__ == "__main__":
    main()
