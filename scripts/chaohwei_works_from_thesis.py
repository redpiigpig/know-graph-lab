#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用碩論附錄三的「著作一覽」補齊昭慧法師／性廣法師的專書目錄。

hub 原本那份書目是東拼西湊的（法界出版社書末廣告頁＋我自己補的），缺書、也沒有
出版社與出版年月。碩論附錄三是**從佛教弘誓學院官網「昭慧法師著作一覽」抄來的
權威清單**，連再版資訊都有，拿它當準。

來源：public/content/thesis/app3.txt（碩論附錄三，markdown 表格）

解析要點：
  🚨 **再版是接在書名那一列下面的「續列」**，第一欄是出版社而不是書名：
        | 佛教倫理學 | 法界出版社 | 1995.10初版 |
        | 淨心文教基金會 | 2001.09三版 |  |
     把續列當成新書，會生出「淨心文教基金會」這種不存在的書名。
  🚨 書名裡的括號帶著編著身分（編輯／合著／口述），要抽出來當 note 而不是書名的一部分。

  python -X utf8 scripts/chaohwei_works_from_thesis.py            # dry-run
  python -X utf8 scripts/chaohwei_works_from_thesis.py --apply
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP3 = ROOT / "public/content/thesis/app3.txt"
STORE = ROOT / "stores/collectedWorks.ts"

# 出版社名（用來認出「再版續列」——那種列的第一欄是出版社不是書名）
_PUBLISHER_RE = re.compile(
    r"(出版社|出版公司|文化|基金會|印精會|圖書公司|Publishing|Verlag|書局|精舍)")


# ── 純函式（scripts/tests/test_chaohwei_works_from_thesis.py 鎖定）────────

def parse_rows(markdown: str) -> list[list[str]]:
    """markdown 表格 → 每列的欄位 list（去掉分隔列與表頭）。"""
    out = []
    for line in markdown.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not any(cells):
            continue
        if all(set(c) <= set(":- ") for c in cells if c):
            continue           # 對齊列
        if cells[0] in ("書名",):
            continue           # 表頭
        out.append(cells)
    return out


_ROLE_RE = re.compile(r"編輯|合著|代撰|口述|訪問|追思集")
_OPEN, _CLOSE = "（(", "）)"


def _last_paren_group(t: str) -> tuple[int, str] | None:
    """從字串**尾端**往前找一組配對的括號，回傳 (起始 index, 括號內文)。

    🚨 一定要能處理巢狀：「（與彼得・辛格（Peter Singer）合著）」裡面還有一層，
    不允許巢狀的 regex 會整組匹配不到，書名就會把「（與…合著）」一起帶進去。
    """
    s = t.rstrip()
    if not s or s[-1] not in _CLOSE:
        return None
    depth = 0
    for i in range(len(s) - 1, -1, -1):
        if s[i] in _CLOSE:
            depth += 1
        elif s[i] in _OPEN:
            depth -= 1
            if depth == 0:
                return i, s[i + 1:-1]
    return None


def split_title_note(title: str) -> tuple[str, str]:
    """書名 → (正書名, 註記)。結尾括號裡若是編著身分就抽出來當註記。

    「成佛之道偈頌科判表（與性廣法師合著）」→ ("成佛之道偈頌科判表", "與性廣法師合著")
    書名本身以括號結尾但不是身分者（如「…中道智慧（一）」）保持原樣。
    """
    t = (title or "").strip().strip("《》").strip()
    g = _last_paren_group(t)
    if not g or not _ROLE_RE.search(g[1]):
        return t, ""
    return t[:g[0]].strip().strip("《》").strip(), g[1].strip()


def is_reprint_row(cells: list[str]) -> bool:
    """這一列是不是前一本書的「再版」續列？

    判準：第一欄看起來是出版社，而且最後一欄是空的——真正的書名列三欄都有值。
    """
    if len(cells) < 2:
        return False
    first_is_publisher = bool(_PUBLISHER_RE.search(cells[0]))
    tail_empty = not (cells[-1].strip())
    return first_is_publisher and tail_empty


def parse_works(markdown: str) -> list[dict]:
    """附錄三表格 → [{"title","publisher","date","year","note","reprints":[…]}]。"""
    works: list[dict] = []
    for cells in parse_rows(markdown):
        if is_reprint_row(cells) and works:
            works[-1]["reprints"].append(f"{cells[0]} {cells[1]}".strip())
            continue
        if len(cells) < 2 or not cells[0]:
            continue
        title, note = split_title_note(cells[0])
        date = cells[2] if len(cells) > 2 and cells[2] else cells[1]
        publisher = cells[1] if len(cells) > 2 else ""
        ym = re.search(r"(\d{4})", date or "")
        works.append({
            "title": title, "publisher": publisher, "date": date,
            "year": ym.group(1) if ym else "", "note": note, "reprints": [],
        })
    return works


def split_sections(markdown: str) -> dict[str, str]:
    """附錄三含兩個人的清單，依「（一）…／（二）…」切開。"""
    parts = re.split(r"\n（[一二]）\s*", markdown)
    names = re.findall(r"\n（[一二]）\s*(\S+)", markdown)
    return dict(zip(names, parts[1:]))


# ── I/O ────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    md = APP3.read_text(encoding="utf-8")
    secs = split_sections(md)
    for who, body in secs.items():
        ws = parse_works(body)
        print(f"\n=== {who}：{len(ws)} 本")
        for w in ws:
            rp = f"　（再版：{'；'.join(w['reprints'])}）" if w["reprints"] else ""
            nt = f"　［{w['note']}］" if w["note"] else ""
            print(f"  {w['year'] or '????'}　{w['title']}　／{w['publisher']}{nt}{rp}")

    if not a.apply:
        print("\n（dry-run，加 --apply 才會寫進 store）")
        return 0

    text = STORE.read_text(encoding="utf-8")
    for who, slug in (("昭慧法師", "chao-hwei"), ("性廣法師", "hsing-kuang")):
        if who not in secs:
            continue
        ws = parse_works(secs[who])
        try:
            i = text.index(f"slug: '{slug}',")
        except ValueError:
            print(f"⚠ store 裡沒有 {slug}，跳過（{who} {len(ws)} 本）")
            continue
        # 這位作家的 works 陣列結尾
        end = text.index("      ],\n    },", i)
        block = text[i:end]
        have = {re.sub(r"[\s　]+", "", t) for t in re.findall(r"title: '([^']+)'", block)}

        rows = []
        for w in ws:
            key = re.sub(r"[\s　]+", "", w["title"])
            if key in have:
                continue
            note_bits = [b for b in (w["note"], w["publisher"]) if b]
            if w["reprints"]:
                note_bits.append("再版：" + "；".join(w["reprints"]))
            note = "，".join(note_bits).replace("'", "’")
            rows.append(
                "        {\n"
                f"          title: '{w['title'].replace(chr(39), chr(8217))}',\n"
                f"          year: '{w['date']}',\n"
                f"          yearSort: {w['year'] or 0},\n"
                "          category: '專書',\n"
                "          languages: ['zh'],\n"
                "          status: 'planned',\n"
                + (f"          note: '{note}',\n" if note else "")
                + "        },")
        if rows:
            text = text[:end] + "\n".join(rows) + "\n" + text[end:]
        print(f"✅ {who}：補入 {len(rows)} 本（原有 {len(have)}，目錄 {len(ws)}）")
    STORE.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
