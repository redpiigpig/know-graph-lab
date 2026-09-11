# -*- coding: utf-8 -*-
"""讀本內容完整性稽核：印出來的字，跟來源那份切片對得起來嗎？

`qa_course_reader.py` 查的是版面與結構（目錄、頁碼、頁眉、導引），**查不出
「少了一塊」**——這條線有四道會刪字的關卡（砍篇末書目、砍編者導言、濾註釋、
丟私用區壞段），任何一道判過頭，印出來仍然是一本排版完美、讀起來也順的書，
只是少了三分之一。所以另外用這支對帳：

    python -X utf8 scripts/qa_reader_completeness.py

逐篇比對「來源切片的字數」與「書上這一篇的字數」，列出保留率；並印出每篇的
頭尾各一句，肉眼確認是不是從正文開頭起、到正文結尾止。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_course_reader as B  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BOOKS = [
    ("宗教研究方法讀本_上冊.pdf", B.C_MON, "mon1"),
    ("宗教研究方法讀本_下冊.pdf", B.C_MON, "mon2"),
    ("宗教學理論讀本.pdf", B.C_SAT, "sat"),
]
LOW = 0.55        # 保留率低於這個就要人看一眼


def zh_len(t: str) -> int:
    return len(re.sub(r"\s+", "", t))


def main() -> None:
    worst = []
    for fname, course, reader in BOOKS:
        parts, courses, lang, _ = B.READERS[reader]
        files = B.index_pdfs(courses)
        doc = fitz.open(B.BASE + "\\" + course + "\\" + fname)
        toc = [t for t in doc.get_toc() if t[0] == 1]
        print("=" * 78)
        print(f"{fname}　{doc.page_count} 頁／{len(toc)} 篇")
        idx = 0
        for _, _, items in parts:
            for key, weeks in items:
                path = B.locate(files, key)
                if not path:
                    print(f"  ★ 找不到來源：{key}")
                    continue
                src_raw = "".join(p.get_text() for p in fitz.open(path))
                paras, notes = B.extract_pdf(path)
                paras, _ = B.cut_editor_intro(paras)
                paras, _ = B.cut_bibliography(paras)
                kept = "\n".join(t for _, t in paras)
                ratio = zh_len(kept) / max(zh_len(src_raw), 1)

                _, title, page = toc[idx]
                end = toc[idx + 1][2] - 1 if idx + 1 < len(toc) else doc.page_count
                idx += 1
                book_text = " ".join(" ".join(doc[j].get_text().split())
                                     for j in range(page - 1, end))
                flag = "★" if ratio < LOW else " "
                print(f" {flag} {title[:44]:46s} 保留 {ratio:5.0%}"
                      f"（來源 {zh_len(src_raw):6d} → 書上 {zh_len(kept):6d}）")
                head = kept[:70].replace("\n", " ")
                tail = kept[-70:].replace("\n", " ")
                print(f"     首：{head}")
                print(f"     尾：{tail}")
                if ratio < LOW:
                    worst.append((fname, title, ratio))
                # 書上的字要真的印出來（不是只存在於抽取結果）
                probe = re.sub(r"\s+", "", kept[:40])
                if probe and probe[:12] not in re.sub(r"\s+", "", book_text):
                    print("     ★ 首段在書上找不到——排版可能吃掉了開頭")
        doc.close()

    print("\n" + "=" * 78)
    if worst:
        print("保留率偏低（砍過頭？要人看一眼）：")
        for f, t, r in worst:
            print(f"  {f}｜{t[:44]}｜{r:.0%}")
    else:
        print("每一篇的保留率都在門檻以上")


if __name__ == "__main__":
    main()
