#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分類 ledger → `DazangWork` 格式的待審提案（不入庫）。

  python scripts/dazangjing_proposal.py --ledger <a.jsonl> [--ledger <b.jsonl>] \
         --out c:/tmp/dazang_proposal.md

只取 decision=keep_primary_work。輸出兩份：
  ① Markdown 審閱表（按時代×藏分組，供人逐條勾選）
  ② 同名 .ts 片段，審過後可直接貼進 data/dazangjing/{era}.ts

🚨 不自動寫入 data/dazangjing/*.ts——那一步要人看過。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ERA = {"ancient": "古代", "medieval": "中世紀", "early-modern": "近代",
       "modern": "現代", "pre": "前史", "unknown": "待定"}
COLL = {"jing": "經藏", "lu": "律藏", "lun": "論藏", "xuandao": "宣道藏",
        "shuxin": "書信藏", "liyi": "禮儀藏", "shiwen": "詩文藏",
        "yijiao": "遺教藏", "shizhuan": "史傳藏", "leishu": "類書藏",
        "unknown": "待定"}


def esc(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace("'", "\\'").strip()


# 書名欄其實是人名的，要剔掉——TRC 的作者資料夾層會被當成作品收進來
# （「希波的奧古斯丁」「羅馬的革利免」「里昂的愛任紐」都出現在書名欄）。
PERSON_AS_TITLE = re.compile(
    r"^(?:[聖圣]?[^\s]{0,4}的)?[^\s]{1,6}(?:主教|教父|殉[教道]者)?$")


# 書名結尾若帶這些字，那就是作品而非人名——《徐光啟集》《馬相伯集》都因為
# 「書名含作者名」被誤剔過，但文集本來就會以作者命名。
WORK_SUFFIX = re.compile(r"(集|傳|錄|書|論|篇|記|譯|注|註|釋|選|全書|文集|著作|日記|年譜|言行)$")


def looks_like_person(c: dict) -> bool:
    """書名與作者高度重疊 → 那一筆是人不是書。"""
    t = re.sub(r"\s+", "", c.get("title_zh") or "")
    a = re.sub(r"\s+", "", (c.get("author") or "").split("(")[0])
    if not t or not a or WORK_SUFFIX.search(t):
        return False
    # 原名欄若等於英文人名（Augustine of Hippo / Justin Martyr）更確定
    orig = (c.get("title_orig") or "").strip()
    same_as_author = t in a or a in t
    return same_as_author and (len(t) <= 10 or orig == (c.get("author") or "").split("(")[0].strip())


def dedupe(items: list[dict]) -> tuple[list[dict], list[tuple[dict, dict]]]:
    """同書名同時代視為同一部。回傳 (保留, 被併掉的配對)。

    同一部書常因譯名不同而重出——《脫利騰公議會教理問答》與《特倫多公議會
    教理問答》就是同一份。這裡只併「書名完全相同」的；譯名不同的要靠翻譯
    詞庫，併不到的留給人看。
    """
    def akey(c: dict) -> str:
        """作者的比對鍵：取中文名或拉丁名的核心，去掉括號與頭銜。"""
        a = (c.get("author") or "").replace("聖", "")
        a = re.sub(r"[（(].*?[）)]", " ", a)
        toks = re.findall(r"[一-鿿]{2,}|[A-Za-z]{3,}", a)
        return toks[-1].lower() if toks else ""

    seen: dict[tuple, dict] = {}
    merged: list[tuple[dict, dict]] = []
    for c in items:
        # 🚨 鍵必須含作者。中文書名撞名的不同作品所在多有——儒斯定與特土良的
        # 護教篇都譯作《護教篇》，只用書名去重會把兩部書併成一部。
        k = (re.sub(r"\s+", "", c["title_zh"]), c["eraKey"], akey(c))
        if k in seen:
            merged.append((seen[k], c))
            # 作者較完整的那筆勝出
            if len(c.get("author") or "") > len(seen[k].get("author") or ""):
                seen[k] = c
        else:
            seen[k] = c
    return list(seen.values()), merged


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", action="append", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows: list[dict] = []
    for lp in a.ledger:
        p = Path(lp)
        if not p.exists():
            print(f"  ⚠ 找不到 {p}")
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))

    keep = [r["classification"] for r in rows
            if r["classification"]["decision"] == "keep_primary_work"]
    # 來源網址帶回去，方便審閱時查證
    src = {id(r["classification"]): (r["source_record"].get("url") or "") for r in rows}
    for c in keep:
        c["_url"] = src.get(id(c), "")

    persons = [c for c in keep if looks_like_person(c)]
    keep = [c for c in keep if not looks_like_person(c)]
    if persons:
        print(f"剔除「書名其實是人名」{len(persons)} 筆："
              + "、".join(c["title_zh"] for c in persons[:6]))
    kept, merged = dedupe(keep)
    print(f"入藏候選 {len(keep)} 部 → 去重後 {len(kept)} 部（合併 {len(merged)} 組）")

    g: dict[str, list[dict]] = defaultdict(list)
    for c in kept:
        g[c["eraKey"]].append(c)

    md = ["# 基督教大藏經 — 待審入藏提案", "",
          f"共 {len(kept)} 部。**這份是提案，尚未入庫**；勾選後才寫進 "
          "`data/dazangjing/{era}.ts`。", ""]
    ts: list[str] = []
    for e in ("ancient", "medieval", "early-modern", "modern", "unknown"):
        if e not in g:
            continue
        md += [f"## {ERA[e]}（{len(g[e])} 部）", ""]
        ts.append(f"\n// ─── {ERA[e]} / {e}.ts ───")
        by: dict[str, list[dict]] = defaultdict(list)
        for c in g[e]:
            by[c["collectionKey"]].append(c)
        for ck in sorted(by):
            md += [f"### {COLL.get(ck, ck)}", "",
                   "| ☐ | 漢語定名 | 原名 | 作者 | 正/外 | 信心 |",
                   "|---|---|---|---|---|---|"]
            ts.append(f"// {COLL.get(ck, ck)}")
            for c in sorted(by[ck], key=lambda x: x["title_zh"]):
                md.append(f"| ☐ | {c['title_zh']} | {c.get('title_orig','')} | "
                          f"{c.get('author','')} | {c['canon']} | {c.get('confidence','')} |")
                ts.append(
                    "{ title_zh: '%s', title_orig: '%s', author: '%s', era: '%s',"
                    " place: '%s', language: '%s' }," % (
                        esc(c["title_zh"]), esc(c.get("title_orig", "")),
                        esc(c.get("author", "")), esc(c.get("era", "")),
                        esc(c.get("place", "")), esc(c.get("language", ""))))
            md.append("")

    if merged:
        md += ["## 已自動合併的重複", "",
               "同書名同時代者已併為一筆；譯名不同而實為同書者併不到，需人工判斷。", ""]
        for a_, b_ in merged:
            md.append(f"- {a_['title_zh']}（{a_.get('author','')}）"
                      f" ← {b_['title_zh']}（{b_.get('author','')}）")
        md.append("")

    out = Path(a.out)
    out.write_text("\n".join(md), encoding="utf-8")
    out.with_suffix(".ts.txt").write_text("\n".join(ts), encoding="utf-8")
    print(f"審閱表 → {out}")
    print(f".ts 片段 → {out.with_suffix('.ts.txt')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
