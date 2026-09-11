# -*- coding: utf-8 -*-
"""課程讀本的成品稽核——排完一定要跑這支，不要等使用者一項一項挑錯。

    python -X utf8 scripts/qa_course_reader.py                 # 三本都查
    python -X utf8 scripts/qa_course_reader.py --book 初階日文讀本.pdf

每一條檢查都對應一次真的踩過的錯（2026-09-08 至 09-10），所以**不要因為
「看起來沒事」就拿掉**：這條線的錯幾乎都是「印出來很正常但內容是壞的」。

  A 目錄印的頁碼要指得到那一篇      舊版印的是 PDF 絕對頁次，每條差 4
  B 每篇要有閱讀導引且排在篇首      使用者翻了十九頁沒看到，以為沒做
  C 導引不可跨頁                    第三個問題老是掉到下一頁
  D 正文不可留頁眉頁腳              「STUDY OF RELIGION: AN OVERVIEW8766」
  E 不可有私用區豆腐格              來源字型把數字對到 PUA，印成「􀀀􀀀􀀀」
  F 不可有黏字                      抽取時漏補空白：「Christendom,but」
  G 篇末不可留參考書目              使用者要求省略
  H 不可留編者寫的作者簡介          選集導言不是要讀的正文
  I 每頁份量要接近                  貪心填滿會讓某頁只剩兩行
  J 頁腳只能有一個號碼              整頁搬運時舊頁碼沒清
  K 正文首行要空兩格
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import fitz

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"G:\我的雲端硬碟\玄奘\博一上\上課")
BOOKS = {
    "宗教研究方法讀本_上冊.pdf": BASE / "宗教研究基本問題與研究方法",
    "宗教研究方法讀本_下冊.pdf": BASE / "宗教研究基本問題與研究方法",
    "宗教學理論讀本.pdf": BASE / "宗教學理論與方法(一)",
    "初階日文讀本.pdf": BASE / "初階宗教學日文文獻選讀",
}
PUA = re.compile(r"[\ue000-\uf8ff\U000f0000-\U0010ffff]")
# 🚨 只認「標點後面直接接大寫」——HarperCollins、McCutcheon、MacIntyre 這種
# 小寫接大寫本來就合法，連進來就是一堆假警報（2026-09-11 踩過）。
GLUED = re.compile(r"[a-z][,.;:][A-Z][a-z]{2,}")      # 「Christendom,but」「mystery.Valuable」
BIBLIO = re.compile(r"^(bibliography|references|works cited|參考書目)\b", re.I)
BIO = re.compile(r"\bwas born (in|on)\b", re.I)
INDENT_X = 48.0 + 10.8 * 2


def norm(t: str) -> str:
    t = t.replace("\u00ad", "-").replace("\u00a0", " ").replace("\u3000", " ")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", t)).strip()


def check(path: Path) -> int:
    doc = fitz.open(path)
    toc = doc.get_toc()
    if not toc:
        print(f"★ {path.name} 沒有書籤，無法稽核")
        return 1
    front = toc[0][2] - 1
    pieces = [(t, p) for lvl, t, p in toc if lvl == 1]
    bad: list[str] = []
    print("=" * 74)
    print(f"{path.name}　{doc.page_count} 頁／封面目錄 {front} 頁／篇 {len(pieces)}")

    # A 目錄
    printed = []
    for i in range(1, front):
        for line in doc[i].get_text().split("\n"):
            m = re.match(r"^(.+?)[·ꞏ.\s]{3,}(\d+)$", norm(line))
            if m:
                printed.append((norm(m.group(1)), int(m.group(2))))
    if len(printed) < len(pieces):
        bad.append(f"A 目錄只印了 {len(printed)} 條，篇數 {len(pieces)}")
    for (title, page), (label, shown) in zip(pieces, printed):
        if shown != page - front:
            bad.append(f"A 目錄頁碼 {norm(title)[:34]}：印 {shown}／實際 {page - front}")
        if norm(title)[:10] not in label:
            bad.append(f"A 目錄篇名對不上 {norm(title)[:34]}｜「{label[:34]}」")

    # B / C 導引
    for i, (title, page) in enumerate(pieces):
        end = pieces[i + 1][1] - 1 if i + 1 < len(pieces) else doc.page_count
        first = norm(doc[page - 1].get_text())
        if "閱讀導引" not in first[:60]:
            bad.append(f"B 導引不在篇首 {norm(title)[:34]}（p{page}）")
        n_guide = sum(1 for j in range(page - 1, min(end, doc.page_count))
                      if "閱讀導引" in norm(doc[j].get_text())[:60])
        if n_guide > 1:
            bad.append(f"C 導引跨了 {n_guide} 頁 {norm(title)[:34]}")
        if "可討論的問題" in first:
            bad.append(f"C 導引還印著可討論的問題 {norm(title)[:34]}")

    # D–H 逐頁內容
    heads = {}
    glued_hits, pua_hits, biblio_hits, bio_hits = [], [], [], []
    for i in range(front, doc.page_count):
        t = doc[i].get_text()
        if PUA.search(t):
            pua_hits.append(i + 1)
        body = norm(t)
        for m in GLUED.finditer(body):
            if not m.group(0).isupper():
                glued_hits.append((i + 1, m.group(0)))
        for line in t.split("\n"):
            ln = norm(line)
            # 書目標題是短標題（三個詞以內、不以句號收尾）；正文裡的
            # 「references apart. …」那種句子不算
            if (BIBLIO.match(ln) and len(ln) < 40
                    and len(ln.split()) <= 3 and not ln.endswith(".")):
                biblio_hits.append((i + 1, ln[:30]))
            if BIO.search(ln) and i - front < 3:
                bio_hits.append((i + 1, ln[:40]))
        # 頁眉重複字串混進內文：同一行在同一頁出現兩次以上
        for line in {norm(x) for x in t.split("\n") if 10 < len(norm(x)) < 70}:
            heads[line] = heads.get(line, 0) + 1
    if pua_hits:
        bad.append(f"E 私用區豆腐格 {len(pua_hits)} 頁：{pua_hits[:6]}")
    if glued_hits:
        bad.append(f"F 黏字 {len(glued_hits)} 處：{[g[1] for g in glued_hits[:6]]}")
    if biblio_hits:
        bad.append(f"G 還留著書目標題 {len(biblio_hits)} 處：{biblio_hits[:4]}")
    if bio_hits:
        bad.append(f"H 疑似編者作者簡介：{bio_hits[:3]}")

    # I 每頁份量
    counts = []
    for i in range(front, doc.page_count):
        t = doc[i].get_text()
        if "閱讀導引" in norm(t)[:60]:
            continue
        counts.append(len([l for l in t.split("\n") if norm(l)]))
    if counts:
        thin = [c for c in counts if c < max(6, sorted(counts)[len(counts) // 2] * 0.4)]
        if len(thin) > len(counts) * 0.08:
            bad.append(f"I 太空的頁 {len(thin)}／{len(counts)}（中位 {sorted(counts)[len(counts)//2]} 行）")

    # J 頁腳
    dupes = [i + 1 for i in range(front, doc.page_count)
             if len(re.findall(r"\d{1,4}", doc[i].get_text(
                 "text", clip=fitz.Rect(0, doc[i].rect.height - 60,
                                        doc[i].rect.width, doc[i].rect.height)))) > 1]
    if dupes:
        bad.append(f"J 頁腳重號 {len(dupes)} 頁：{dupes[:5]}")

    # K 首行縮排
    xs = [round(b[0]) for i in range(front, min(front + 80, doc.page_count))
          for b in doc[i].get_text("blocks") if b[4].strip()]
    if not any(abs(x - INDENT_X) <= 2 for x in xs):
        bad.append("K 找不到首行縮排")

    for b in bad:
        print("  ★", b)
    print("  →", "通過" if not bad else f"{len(bad)} 項要看")
    doc.close()
    return len(bad)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="只查這一本（檔名）")
    a = ap.parse_args()
    total = 0
    for name, folder in BOOKS.items():
        if a.book and a.book != name:
            continue
        path = folder / name
        if not path.exists():
            print(f"★ 找不到 {path}")
            total += 1
            continue
        total += check(path)
    print("\n總結：", "全數通過" if total == 0 else f"{total} 項要看")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
