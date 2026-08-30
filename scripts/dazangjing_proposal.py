#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分類 ledger → `DazangWork` 格式的待審提案（不入庫）。

  node scripts/dazangjing_dump_corpus.mjs c:/tmp/dz_corpus.json
  python scripts/dazangjing_proposal.py --ledger <a.jsonl> [--ledger <b.jsonl>] \
         --corpus c:/tmp/dz_corpus.json \
         --adjudication data/dazangjing/source-catalog/adjudication-<date>.json \
         --out c:/tmp/dazang_proposal.md

只取 decision=keep_primary_work。輸出兩份：
  ① Markdown 審閱表（按時代×藏分組，供人逐條勾選）
  ② 同名 .ts 片段，審過後可直接貼進 data/dazangjing/{era}.ts

🚨 不自動寫入 data/dazangjing/*.ts——那一步要人看過。

`--adjudication`（2026-08-30 加）帶入**人工**審定，與 `--corpus` 的自動撞名比對
分工：自動比對抓「機器看得出來的同書」，審定表記「只有人判得了的」——譯本合集
（《使徒教父著作》所收各篇早已分別在藏）、次級改編、時代標錯（《教務紀略》
光緒三十一年卻被歸到近代）、書名 OCR 誤字（「癖基督抹殺論」應作「闢」）、
作者張冠李戴（Joseph Martos 被安成明清耶穌會士「馬若瑟」）。

審定表的 keep 條目可帶 `patch` 改寫欄位，且**在自動比對之前套用**——改過的
時代與藏別才是拿去跟全藏比的那一份。沒有判定的 record 會照常留在提案裡並列
警告，**新增來源站後別忘了補判定**。
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


# ── 翻譯詞庫（人名） ────────────────────────────────────────────────────────
# 詞庫正本在 Supabase，這裡讀 export_glossary_from_db.py 落地的 markdown 快取，
# 讓清理流程離線可跑。表列格式：
#   | Clement of Rome | Κλήμης | –101 | **羅馬的革利免** | 思高=… · 中國=… |
GLOSSARY_MD = Path(__file__).resolve().parents[1] / ".claude/skills/ebook-translate/glossary.md"
GLOSSARY_ROW = re.compile(
    r"^\|\s*([A-Za-z][^|]*?)\s*\|[^|]*\|[^|]*\|\s*\*\*([^*|]+)\*\*\s*\|([^|]*)\|")


def load_people() -> tuple[set[str], dict[str, str], dict[str, str]]:
    """回傳 (英文人名集合, 異譯 → 建議定名, 英文名 → 建議定名)。

    第三項是英中作者的橋：來源站的作者欄常只寫 `Augustine of Hippo`，藏內卻
    只寫「奧古斯丁」，兩邊詞元永遠不會有交集，撞名就漏判。詞庫本來就是這組
    對照的權威，拿來補齊。詞庫讀不到就退成空表，不擋流程。
    """
    en: set[str] = set()
    variants: dict[str, str] = {}
    en2zh: dict[str, str] = {}
    if not GLOSSARY_MD.exists():
        print(f"  ⚠ 找不到詞庫快取 {GLOSSARY_MD}，略過定名檢查")
        return en, variants, en2zh
    for line in GLOSSARY_MD.read_text(encoding="utf-8").splitlines():
        m = GLOSSARY_ROW.match(line)
        if not m:
            continue
        name_en, zh, var = m.group(1).strip(), m.group(2).strip(), m.group(3)
        key = re.sub(r"\s+", " ", name_en).lower()
        en.add(key)
        en2zh[key] = zh
        for v in re.split(r"[·・‧]", var):
            v = v.split("=", 1)[-1].strip()
            # 只收純漢字異譯，且與建議定名不同者
            if v and v != zh and re.fullmatch(r"[一-鿿‧·]{2,12}", v):
                variants.setdefault(v, zh)
    return en, variants, en2zh


def looks_like_person(c: dict, people_en: set[str] = frozenset()) -> bool:
    """書名與作者高度重疊 → 那一筆是人不是書。

    先前只比對「書名 vs 作者」，漏掉譯名不同的：《羅馬的革利免》作者欄寫
    「克萊門」、《殉教者遊斯丁》作者欄寫「Justin Martyr」，兩邊字面不重疊就
    被當成書收進來。改成先問詞庫——原名欄若整個等於一位已知人物的英文名，
    那一筆鐵定是人不是書。
    """
    orig_key = re.sub(r"\s+", " ", (c.get("title_orig") or "")).strip().lower()
    if orig_key and orig_key in people_en:
        return True
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


# ── 與現有全藏比對 ──────────────────────────────────────────────────────────
# README 的規矩：入庫前要對「整個 Dazangjing corpus」去重，不是只在這一批之內。
# 少了這道，2026-08-28 那份提案就把《上帝之城》《懺悔錄》《教會史》這種早就
# 在藏的書又推了一次。

def norm_title(s: str) -> str:
    """書名比對鍵：去書名號、標點與空白。跨時代通用。"""
    return re.sub(r"[《》〈〉「」『』（）()\[\]，,、：:；;．.·‧\-—_\s]", "", s or "")


def norm_orig(s: str) -> str:
    """原名比對鍵：拉丁字母小寫化。太短的（<7 字元）不拿來當鍵，容易誤撞。"""
    return " ".join(re.sub(r"[^a-z ]", " ", (s or "").lower()).split())


def author_tokens(s: str, en2zh: dict[str, str] | None = None) -> set[str]:
    """作者比對用的詞元集合。中文取 2 字以上詞塊，拉丁取 3 字母以上單字。

    取集合而非「最後一個詞元」——「希波的奧古斯丁 Augustine of Hippo」的最後
    一個詞元是 hippo，跟藏內的「奧古斯丁」對不上；取交集就對得上。
    """
    a = re.sub(r"[（(].*?[）)]", " ", (s or "").replace("聖", ""))
    # 「的」也要當分隔——不切的話「希波的奧古斯丁」是一整個詞元，跟藏內只寫
    # 「奧古斯丁」的那筆永遠對不上，撞名就漏判。
    a = re.sub(r"[的‧·・、,;／/]", " ", a)
    toks = {t.lower() for t in re.findall(r"[一-鿿]{2,}|[A-Za-z]{3,}", a)}
    toks -= {"the", "and", "saint", "pope", "translator", "editor", "unknown",
             "author", "of", "et", "al", "others", "compiled", "attributed"}
    # 作者欄含詞庫裡的英文人名時，把該人的漢語定名詞元一併算進來
    if en2zh:
        low = " ".join(re.sub(r"[^a-z ]", " ", (s or "").lower()).split())
        for name_en, zh in en2zh.items():
            if len(name_en) >= 6 and name_en in low:
                toks |= {t.lower() for t in re.findall(
                    r"[一-鿿]{2,}", re.sub(r"[的‧·・]", " ", zh))}
    return toks


def same_person(x: set[str], y: set[str]) -> bool:
    """兩組作者詞元指向同一人。漢名常一詳一略（「托馬斯‧阿奎那」vs「阿奎那」），
    所以中文詞元用「一方包含另一方」判定，拉丁詞元則要求完全相同。"""
    for i in x:
        for j in y:
            if i == j:
                return True
            if len(i) >= 2 and len(j) >= 2 and re.fullmatch(r"[一-鿿]+", i + j)                     and (i in j or j in i):
                return True
    return False


def build_corpus_index(corpus: list[dict]) -> tuple[dict, dict]:
    zh: dict[str, list[dict]] = defaultdict(list)
    orig: dict[str, list[dict]] = defaultdict(list)
    for w in corpus:
        zh[norm_title(w["title_zh"])].append(w)
        o = norm_orig(w.get("title_orig", ""))
        if len(o) >= 7:
            orig[o].append(w)
    return zh, orig


def already_in_canon(c: dict, zh_idx: dict, orig_idx: dict,
                     en2zh: dict[str, str] | None = None) -> tuple[str, dict] | None:
    """撞到藏內既有條目就回傳 (判定, 那一筆)，否則 None。

    判定有兩級：
      'same'    書名與作者都對上 → 同一部書，直接剔除。
      'suspect' 書名對上但作者對不攏 → **不剔除**，另列一區交人工判。

    分兩級是必要的。書名相同不等於同一部書：奧古斯丁與希拉流各有一部《論三位
    一體》，湯漢與維克託利烏斯各有一部《創世論》，Barhebraeus 與 Baronius 各
    有一部《教會編年史》——自動剔掉就少收三部真書。反過來，作者欄一邊只寫
    `Pope John Paul II` 一邊只寫「教宗若望保祿二世」而詞庫又沒收的，也對不攏，
    但那確實是同一部。兩種情況機器分不出來，所以一律送人工。
    """
    cand = list(zh_idx.get(norm_title(c["title_zh"]), []))
    o = norm_orig(c.get("title_orig", ""))
    if len(o) >= 7:
        cand += orig_idx.get(o, [])
    if not cand:
        return None
    mine = author_tokens(c.get("author", ""), en2zh)
    for w in cand:
        theirs = author_tokens(w.get("author", ""), en2zh)
        if mine and theirs and same_person(mine, theirs):
            return "same", w
    return "suspect", cand[0]


def apply_adjudication(keep: list[dict], path: str) -> tuple[list[dict], list[tuple[dict, dict]]]:
    """套用人工審定表：drop_* 的剔除、keep 的套 patch。

    回傳 (留下的, 被剔除的 (條目, 判定) 配對)。比對鍵與審定表的 match_key 一致：
    (source, title_zh, eraKey, collectionKey)。同鍵重出的（比利時信條、西敏準則、
    徐光啟集各兩筆）本來就同判定，共用一條規則。
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    table = {(v["source"], re.sub(r"\s+", "", v["title_zh"]),
              v["eraKey"], v["collectionKey"]): v for v in data["verdicts"]}
    kept: list[dict] = []
    dropped: list[tuple[dict, dict]] = []
    unjudged: list[dict] = []
    for c in keep:
        key = (c.get("_source", ""), re.sub(r"\s+", "", c.get("title_zh") or ""),
               c.get("eraKey", ""), c.get("collectionKey", ""))
        v = table.get(key)
        if v is None:
            unjudged.append(c)
            kept.append(c)
        elif v["verdict"].startswith("drop"):
            dropped.append((c, v))
        else:
            # patch 可改 title_zh / eraKey / collectionKey，要在分組與全藏比對前套完
            c.update(v.get("patch") or {})
            c["_verdict_reason"] = v.get("reason", "")
            kept.append(c)
    by_verdict: dict[str, int] = defaultdict(int)
    for _, v in dropped:
        by_verdict[v["verdict"]] += 1
    print(f"人工審定 {Path(path).name}：剔除 {len(dropped)} 部（"
          + "、".join(f"{k} {n}" for k, n in sorted(by_verdict.items())) + f"），留 {len(kept)} 部")
    if unjudged:
        print(f"  ⚠ 尚無判定 {len(unjudged)} 部，先留在提案內請補審："
              + "、".join(c["title_zh"][:18] for c in unjudged[:8]))
    return kept, dropped


def misnamed(c: dict, variants: dict[str, str]) -> list[str]:
    """定名沒對齊詞庫者，回傳「異譯 → 建議」的說明。"""
    hay = f"{c.get('title_zh','')} {c.get('author','')}"
    return [f"{v}→{zh}" for v, zh in variants.items() if v in hay]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--corpus", help="node scripts/dazangjing_dump_corpus.mjs 產出的全藏 JSON；"
                                     "不給就跳過與現有全藏的去重（不建議）")
    ap.add_argument("--adjudication", help="人工審定 JSON（drop/keep 判定與欄位 patch）；"
                                           "不給就只跑自動比對")
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
    # 來源網址與站別帶回去：網址方便審閱時查證，站別是審定表的比對鍵之一
    # （同名書兩站各有一本，判定未必相同）。
    meta = {id(r["classification"]): (r["source_record"].get("url") or "",
                                      r["source_record"].get("source") or "") for r in rows}
    for c in keep:
        c["_url"], c["_source"] = meta.get(id(c), ("", ""))

    adjudicated: list[tuple[dict, dict]] = []
    if a.adjudication:
        keep, adjudicated = apply_adjudication(keep, a.adjudication)

    people_en, variants, en2zh = load_people()

    persons = [c for c in keep if looks_like_person(c, people_en)]
    keep = [c for c in keep if not looks_like_person(c, people_en)]
    if persons:
        print(f"剔除「書名其實是人名」{len(persons)} 筆："
              + "、".join(c["title_zh"] for c in persons[:6]))
    kept, merged = dedupe(keep)
    print(f"入藏候選 {len(keep)} 部 → 批內去重後 {len(kept)} 部（合併 {len(merged)} 組）")

    dupes: list[tuple[dict, dict]] = []
    suspects: list[tuple[dict, dict]] = []
    if a.corpus:
        corpus = json.loads(Path(a.corpus).read_text(encoding="utf-8"))
        zh_idx, orig_idx = build_corpus_index(corpus)
        fresh = []
        for c in kept:
            hit = already_in_canon(c, zh_idx, orig_idx, en2zh)
            if hit and hit[0] == "same":
                dupes.append((c, hit[1]))
            else:
                if hit:
                    suspects.append((c, hit[1]))
                fresh.append(c)
        kept = fresh
        print(f"全藏 {len(corpus)} 卷比對：撞名剔除 {len(dupes)} 部、"
              f"疑似重複待人工判 {len(suspects)} 部 → 實收 {len(kept)} 部")
    else:
        print("  ⚠ 沒給 --corpus，未與現有全藏去重")

    flagged = [(c, m) for c in kept if (m := misnamed(c, variants))]
    if flagged:
        print(f"定名待對齊詞庫 {len(flagged)} 部")

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

    if adjudicated:
        LABEL = {"drop_dup_existing": "藏內已收（同書異名）",
                 "drop_anthology": "譯本合集／選集，非單一原典",
                 "drop_person_or_folder": "書名欄其實是人名或來源站分類夾",
                 "drop_secondary": "次級改編或非原典層級"}
        by: dict[str, list] = defaultdict(list)
        for c, v in adjudicated:
            by[v["verdict"]].append((c, v))
        md += ["## 已剔除：人工審定", "",
               "逐筆查證後判定不入藏者。剔除理由與對應的藏內既有條目一併列出，"
               "供日後回查；判定表在 `data/dazangjing/source-catalog/`。", ""]
        for verdict in sorted(by):
            md += [f"### {LABEL.get(verdict, verdict)}（{len(by[verdict])} 部）", ""]
            for c, v in sorted(by[verdict], key=lambda x: x[0]["title_zh"]):
                line = f"- ~~{c['title_zh']}~~（{c.get('author','') or '作者未填'}）—— {v['reason']}"
                if v.get("dup_of"):
                    line += f"　→ 已在藏：{v['dup_of']}"
                md.append(line)
            md.append("")
        aliases = [v["alias"] for _, v in adjudicated if v.get("alias")]
        if aliases:
            md += ["### 待補進翻譯詞庫的同書異名", "",
                   "以下各組是同一部書的不同漢譯名，要補進 `theological_terms`"
                   "（`entity_type='work'`）——比對能力靠詞庫累積，補了下一輪自動就抓得到。", ""]
            for grp in sorted(aliases, key=lambda g: g[0]):
                md.append(f"- {'／'.join(grp)}")
            md.append("")

    if dupes:
        md += ["## 已剔除：現有全藏已收", "",
               "書名（或原名）與作者同時對上藏內既有條目者，視為同一部書，不重複入藏。", ""]
        for c, w in dupes:
            md.append(f"- ~~{c['title_zh']}~~（{c.get('author','')}）"
                      f" → 已在 {ERA.get(w['era'], w['era'])}／{COLL.get(w['coll'], w['coll'])}"
                      f"／{'正藏' if w['canon'] == 'zheng' else '外藏'}：{w['title_zh']}")
        md.append("")

    if suspects:
        md += ["## ⚠ 疑似重複：書名對上藏內，但作者對不攏", "",
               "**這一區仍列在上面的提案內**，勾選前要逐筆判：是同一部書（→ 取消勾選），"
               "還是同名異書（→ 照收，但漢語定名要加分別）。", ""]
        for c, w in sorted(suspects, key=lambda x: x[0]["title_zh"]):
            md.append(f"- {c['title_zh']}（{c.get('author','') or '作者未填'}）"
                      f" ←→ {ERA.get(w['era'], w['era'])}／{COLL.get(w['coll'], w['coll'])}"
                      f"／{'正藏' if w['canon'] == 'zheng' else '外藏'}："
                      f"{w['title_zh']}（{w.get('author','') or '作者未填'}）")
        md.append("")

    if persons:
        md += ["## 已剔除：書名欄其實是人名", "",
               "來源站的作者資料夾層被當成作品收進來，不是一部書。", ""]
        for c in sorted(persons, key=lambda x: x["title_zh"]):
            md.append(f"- ~~{c['title_zh']}~~（原名 {c.get('title_orig','')}）")
        md.append("")

    if flagged:
        md += ["## 待改：定名沒對齊翻譯詞庫", "",
               "以下條目仍在提案內，但入庫前要照 /translation-glossary 的建議定名改寫。", ""]
        for c, ms in sorted(flagged, key=lambda x: x[0]["title_zh"]):
            md.append(f"- {c['title_zh']}（{c.get('author','')}）—— {'、'.join(ms)}")
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
