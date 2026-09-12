# -*- coding: utf-8 -*-
"""切片本身的稽核：每一份指定讀物**在來源書裡真的讀完了沒**。

讀本那一層的稽核（qa_course_reader.py）只看得到成品，看不出「課綱給的頁碼
本來就少一頁」。而這種錯最像成功：切片打開是一篇論文、頁數正常、首頁也對，
只有翻到最後一頁才會發現句子斷在半路（[[feedback_reader_silent_failures]]）。

兩個方向都查：

  短了 —— 最後一頁的正文不是以句末標點收尾，而且下一頁還是同一章
           （課綱寫「Penner, Interpretation, Guide 57-66」，但那一章到 71 頁）
  長了 —— 切片裡出現第二個條目／章的標題（Alles 那份夾到了隔壁條目
           〈… IN AUSTRALIA AND OCEANIA〉）

    python -X utf8 scripts/qa_course_slices.py
"""
from __future__ import annotations

import os
import re
import sys

import fitz

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = r"G:\我的雲端硬碟\玄奘\博一上\上課"
END_OK = ('.', '?', '!', '"', ')', ']', '\u201d', '\u2019')
FURNITURE = re.compile(
    r"^(\d{1,4}|[ivxlcIVXLC]{1,7}|brought to you by.*|authenticated|download date.*|"
    r"encyclopedia of religion.*|.*bobst library.*)$", re.I)

# 查過、確認不是錯的，列這裡免得每次都當成待辦重查一遍。鍵是檔名片段。
ACCEPTED = {
    "Alles_Study of Religion":
        "課綱給的是 EoR 8761-8767，而 8767 那一頁一頁兩條目（Overview 的書目＋下一"
        "條目的開頭）。切片是忠實存檔，不動它；讀本那一端已經在 BIBLIOGRAPHY 處切"
        "乾淨，成品裡沒有 AUSTRALIA 也沒有 8767。",
    "King_Historical and Phenomenological Approaches (41-56)":
        "課綱是 41-176 但只讀 41-56 與 84-164，從 56 頁跳到 84 頁。任何頁界都會斷在"
        "句中（試過切到 57，末行一樣斷句），所以照課綱切，改在讀本篇末印一行說明"
        "（build_course_reader.RANGE_NOTE）。",
}


def body_lines(page: fitz.Page) -> list[str]:
    """去掉頁眉頁腳與資料庫套印之後的正文行。"""
    h = page.rect.height
    out = []
    for blk in page.get_text("dict")["blocks"]:
        lines = blk.get("lines", [])
        if not lines:
            continue
        y0, y1 = blk["bbox"][1], blk["bbox"][3]
        if y1 < h * 0.07 or y0 > h * 0.93:
            continue
        for ln in lines:
            t = "".join(sp["text"] for sp in ln["spans"]).strip()
            if t and not FURNITURE.match(t):
                out.append(t)
    return out


def main() -> None:
    rows: list[tuple[str, str, str]] = []
    for course in sorted(os.listdir(BASE)):
        cdir = os.path.join(BASE, course)
        if not os.path.isdir(cdir):
            continue
        for week in sorted(os.listdir(cdir)):
            wdir = os.path.join(cdir, week)
            if not os.path.isdir(wdir):
                continue
            for f in sorted(os.listdir(wdir)):
                if not f.lower().endswith(".pdf"):
                    continue
                doc = fitz.open(os.path.join(wdir, f))
                if doc.page_count < 2:
                    doc.close()
                    continue
                tail = body_lines(doc[-1])
                last = tail[-1] if tail else ""
                if last and not last.rstrip().endswith(END_OK):
                    rows.append(("短？", f[:62], last[-60:]))
                # 長了：最後兩頁出現整行大寫的長標題＝隔壁條目的起點
                for pg in range(max(0, doc.page_count - 2), doc.page_count):
                    for t in body_lines(doc[pg]):
                        letters = [c for c in t if c.isalpha()]
                        if (len(t) > 24 and letters
                                and sum(c.isupper() for c in letters) / len(letters) > 0.85):
                            rows.append(("長？", f[:62], t[:60]))
                doc.close()

    known = [r for r in rows if any(k in r[1] for k in ACCEPTED)]
    rows = [r for r in rows if not any(k in r[1] for k in ACCEPTED)]
    if not rows:
        print("全部切片都以句末標點收尾，也沒夾到隔壁條目（已核可的例外不計）。")
    else:
        print(f"{'':4s} {'檔名':62s}  末行／可疑標題")
        for kind, name, note in rows:
            print(f"{kind:4s} {name:62s}  {note}")
        print(f"\n共 {len(rows)} 筆要看。")
    if known:
        print(f"\n已核可的例外（查過，不必再查）：")
        for k, why in ACCEPTED.items():
            if any(k in r[1] for r in known):
                print(f"  · {k}\n    {why}")


if __name__ == "__main__":
    main()
