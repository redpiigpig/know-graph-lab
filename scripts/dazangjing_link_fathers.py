#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把基督教大藏經的教父卷連到 /fathers 裡「那一卷」，而不是入口頁。

  node scripts/dazangjing_dump_corpus.mjs c:/tmp/dz_corpus.json
  python scripts/dazangjing_link_fathers.py --corpus c:/tmp/dz_corpus.json \
         --out data/dazangjing/source-catalog/LINKS_fathers.md

背景：藏內 414 卷教父著作的 link 全是光禿禿的 /fathers，點進去只到入口頁——
但目錄頁尾寫著「『對照 →』表示該卷已有站內全文對照可閱讀」。頁面正常、內容
卻配錯，正是最難察覺的那種失敗。這支腳本把它們解析成
/fathers/{ebook_id}?page={n}。

為什麼不用字串比對就好：試過，414 卷只中 43 卷，而且配錯的比沒配上更危險
——「論道成肉身」會配到金口若望講道集裡的一講而不是亞他那修的專論，「論聖
靈」會配到「論聖靈與字句」。所以改成每卷書問一次 LLM，給它整卷目錄與候選定
名做對齊；回傳的單元名必須逐字存在於該卷目錄中，否則整筆丟掉。

🚨 只產提案，不寫回 data/dazangjing/*.ts——那一步要人看過。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 引擎鏈與詞庫都已經有現成的，不重寫
AI = _load("dz_catalog_ai", ROOT / "scripts" / "dazangjing_catalog_ai.py")
PROP = _load("dz_proposal", ROOT / "scripts" / "dazangjing_proposal.py")


# ── 取得 /fathers 的卷 ───────────────────────────────────────────────────────
def fetch_fathers_books() -> list[dict]:
    """與 pages/fathers/index.vue 同一條件：subcategory 含 Schaff 或 ACCS。"""
    import requests
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.get(
        f"{url}/rest/v1/ebooks",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        params={"select": "id,title,original_title,chunk_count,parsed_at",
                "or": "(subcategory.ilike.%Schaff%,subcategory.ilike.%ACCS%)",
                "limit": "500"},
        timeout=60)
    r.raise_for_status()
    return [b for b in r.json() if b.get("parsed_at") and (b.get("chunk_count") or 0) > 0]


def volume_units(ebook_id: str, chunks_dir: Path) -> list[dict]:
    """一卷書的可連結單元。page = chunk_index + 1（見 server/api/ebooks/[id].get.ts）。

    🚨 只讀 {id}.jsonl。同目錄下還躺著 .en.bak.jsonl 與 .bak_pre_merge，那些是
    翻譯前的英文原檔，段數對不上也沒有中譯（Augustine Confessions 那卷正式檔
    68 段、英文備份 481 段），讀錯就整卷配錯頁。
    """
    path = chunks_dir / f"{ebook_id}.jsonl"
    if not path.exists():
        return []
    units, seen_parent = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        page = c["chunk_index"] + 1
        pv, cp = c.get("parent_volume"), c.get("chapter_path")
        if pv and pv not in seen_parent:
            seen_parent.add(pv)
            units.append({"kind": "parent", "label": pv, "page": page})
        if cp:
            units.append({"kind": "chapter", "label": cp, "page": page})
    return units


# ── 候選歸卷 ────────────────────────────────────────────────────────────────
SKIP_UNIT = re.compile(
    r"^(封面|目錄|前言|序言?$|導論|介紹說明|索引|附錄|書名頁|譯者序|"
    r"Contents?\.?$|Preface|Index|Bibliography)")


def build_zh2en(en2zh: dict[str, str]) -> dict[str, set[str]]:
    """漢語定名詞元 → 英文人名。用來把「奧古斯丁」對到 Augustine - … NPNF1 那幾卷。"""
    out: dict[str, set[str]] = defaultdict(set)
    for en, zh in en2zh.items():
        for tok in re.findall(r"[一-鿿]{2,}", re.sub(r"[的‧·・]", " ", zh)):
            out[tok].add(en)
    return out


def shortlist(work: dict, books: list[dict], zh2en: dict[str, set[str]]) -> list[str]:
    """這一卷大藏經著作可能落在哪幾冊 Schaff／ACCS。對不到就回空，交給 orphan 池。"""
    author = re.sub(r"[（(].*?[）)]", " ", work.get("author") or "")
    ens: set[str] = set()
    for tok in re.findall(r"[一-鿿]{2,}", re.sub(r"[的‧·・]", " ", author)):
        ens |= zh2en.get(tok, set())
    surnames = {e.split(" of ")[0].split(",")[0].strip().lower() for e in ens}
    surnames = {s for s in surnames if len(s) >= 4}
    ids = []
    for b in books:
        hay = f"{b['title']} {b.get('original_title') or ''}".lower()
        if any(s in hay for s in surnames):
            ids.append(b["id"])
    return ids


PROMPT = """你在把《基督教大藏經》的教父書目對到站上已有全文的 Schaff／ACCS 卷冊。

這一卷書是：{book_title}

它的目錄單元如下（每行：頁碼 tab 單元名）：
{toc}

以下是大藏經裡「可能」收在這一卷的著作，逐條判斷它在不在這一卷：
{cands}

規則：
1. 只有確定是「同一部著作」才配。書名相近但不是同一部——例如亞他那修的專論
   《論道成肉身》與金口若望講道集裡某一講「論道成肉身、成為人」——一律不配。
2. 挑「最能單獨指向這一部著作」的單元。一部著作橫跨多個單元時配第一個；
   若目錄把好幾部不同的著作併成同一個大單元，那就不要配，留白。
3. unit 欄必須逐字複製上面目錄裡的單元名，不得改寫、簡稱或補字。
4. 配不到的就不要出現在輸出裡。寧缺勿錯。

只輸出 JSON，格式：
{{"matches":[{{"title_zh":"…","unit":"…","confidence":0.0}}]}}"""


def ask(prompt: str, gk: list[str], nk: list[str], cur: dict) -> dict | None:
    """Gemini 主 → NVIDIA → Haiku 救急（見 feedback_engine_nvidia_no_haiku）。"""
    for engine in ("gemini", "nvidia", "haiku"):
        try:
            if engine == "gemini":
                if not gk:
                    continue
                text, _, cur["gemini"] = AI.call_gemini(prompt, gk, cur.get("gemini", 0))
            elif engine == "nvidia":
                if not nk:
                    continue
                text, _, cur["nvidia"] = AI.call_nvidia(prompt, nk, cur.get("nvidia", 0))
            else:
                text, _ = AI.call_haiku(prompt)
            return AI.parse_json_loose(text)
        except Exception as e:                                        # noqa: BLE001
            print(f"    {engine} 失敗：{str(e)[:90]}")
    return None


def split_ambiguous(results: list[dict]) -> tuple[list[dict], list[list[dict]]]:
    """幾卷書指到同一頁時，那一頁不可能同時是它們各自的正文起點。

    NPNF1 Vol 4 把奧古斯丁六部各自獨立的駁摩尼教著作壓成一個「駁摩尼派論集
    卷一～卷七」，目錄裡分不出哪一卷是《論善之本性》哪一卷是《駁福斯圖斯》。
    這種情況下六條連結會全部指到同一頁——頁面照樣打得開，但讀者看到的不是他
    點的那部書。與其配一個看起來成功的錯連結，不如留白並把該冊列出來重切。
    """
    by_page: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for r in results:
        by_page[(r["ebook_id"], r["page"])].append(r)
    good = [g[0] for g in by_page.values() if len(g) == 1]
    clashes = [g for g in by_page.values() if len(g) > 1]
    return good, clashes


def render(results: list[dict], clashes: list[list[dict]], lowconf: list[dict],
           total: int, min_conf: float) -> str:
    md = ["# 教父卷逐卷連結 — 待審", "",
          f"藏內 {total} 卷教父著作的 link 原本全是 /fathers 入口頁；這裡解析出 "
          f"{len(results)} 條直達該卷的連結。**尚未寫回** data/dazangjing/*.ts。", "",
          "三道閘：單元名逐字對得上該冊目錄、信心不低於 "
          f"{min_conf}、同一頁不得對到多卷。", ""]
    if lowconf:
        md += [f"## 未採用：信心低於 {min_conf}", "",
               "模型自己標低信心的多半是「照順序填」——安波羅修那一冊八部著作被依序"
               "填進「論著選 第1-10章」到「第71-80章」，信心全 0.0。", ""]
        for r in sorted(lowconf, key=lambda x: (x["book_title"], x["page"])):
            md.append(f"- {r['title_zh']} → {r['book_title'][:40]}／"
                      f"{r['unit']}（{r['confidence']}）")
        md.append("")
    if clashes:
        md += ["## ⚠ 未採用：該冊未分篇，數卷指到同一頁", "",
               "這幾組著作在站上那一冊的目錄裡被併成同一個大單元，分不出各自的"
               "起點。連過去會開到別部書，所以留白——要解，得先把那一冊重新分篇"
               "（見 ebook-pipeline 的 consolidator）。", ""]
        for g in sorted(clashes, key=lambda x: -len(x)):
            md.append(f"- **{g[0]['book_title'][:56]}** · 單元「{g[0]['unit']}」"
                      f"（第 {g[0]['page']} 頁）← "
                      + "、".join(r["title_zh"] for r in g))
        md.append("")
    by_book: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_book[r["book_title"]].append(r)
    for bt in sorted(by_book):
        md += [f"## {bt}", "",
               "| ☐ | 大藏經定名 | 對到的單元 | 頁 | 信心 |", "|---|---|---|---|---|"]
        for r in sorted(by_book[bt], key=lambda x: x["page"]):
            md.append(f"| ☐ | {r['title_zh']} | {r['unit']} | {r['page']} | {r['confidence']} |")
        md.append("")
    return "\n".join(md)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunks-dir", default=None)
    ap.add_argument("--limit", type=int, help="只跑前 N 冊（試跑用）")
    ap.add_argument("--min-confidence", type=float, default=0.5,
                    help="低於此信心的一律不採用（預設 0.5）")
    ap.add_argument("--from-jsonl", help="不打 LLM，直接拿上次的 .jsonl 重跑各道閘並重出報告")
    a = ap.parse_args()

    if a.from_jsonl:
        rows = [json.loads(l) for l in
                Path(a.from_jsonl).read_text(encoding="utf-8").splitlines() if l.strip()]
        corpus = json.loads(Path(a.corpus).read_text(encoding="utf-8"))
        total = sum(1 for w in corpus if w["link"] == "/fathers")
        return finish(rows, total, Path(a.out), a.min_confidence)

    AI.load_dotenv()
    chunks_dir = Path(a.chunks_dir or os.environ["EBOOK_CHUNKS_DIR"])
    corpus = json.loads(Path(a.corpus).read_text(encoding="utf-8"))
    targets = [w for w in corpus if w["link"] == "/fathers"]
    books = fetch_fathers_books()
    print(f"待連結 {len(targets)} 卷 · 已有全文 {len(books)} 冊")

    _, _, en2zh = PROP.load_people()
    zh2en = build_zh2en(en2zh)

    per_book: dict[str, list[dict]] = defaultdict(list)
    orphans: list[dict] = []
    for w in targets:
        ids = shortlist(w, books, zh2en)
        if ids:
            for i in ids:
                per_book[i].append(w)
        else:
            orphans.append(w)
    print(f"作者對得上冊次 {len(targets) - len(orphans)} 卷；"
          f"對不上 {len(orphans)} 卷（併進每冊候選，靠目錄判）")

    gk = AI.env_keys(("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    nk = AI.env_keys(("NVIDIA_API_KEY",))
    cur: dict[str, int] = {}

    results: list[dict] = []
    seen: set[str] = set()
    todo = books[: a.limit] if a.limit else books
    for n, b in enumerate(todo, 1):
        units = [u for u in volume_units(b["id"], chunks_dir)
                 if not SKIP_UNIT.match(u["label"])]
        if not units:
            print(f"[{n}/{len(todo)}] {b['title'][:44]} — 無本機 JSONL，跳過")
            continue
        cands = [w for w in per_book.get(b["id"], []) + orphans
                 if w["title_zh"] not in seen]
        if not cands:
            continue
        by_label = {u["label"]: u for u in units}
        toc = "\n".join(f"{u['page']}\t{u['label']}" for u in units)
        cand_txt = "\n".join(
            f"- {w['title_zh']}｜原名 {w['title_orig'] or '—'}｜作者 {w['author'] or '—'}"
            for w in cands)
        print(f"[{n}/{len(todo)}] {b['title'][:44]} — 目錄 {len(units)} · 候選 {len(cands)}")

        data = ask(PROMPT.format(book_title=b["title"], toc=toc, cands=cand_txt), gk, nk, cur)
        if not data:
            print("    三引擎皆失敗，跳過")
            continue

        by_title = {w["title_zh"]: w for w in cands}
        kept = 0
        for m in data.get("matches", []):
            t = (m.get("title_zh") or "").strip()
            unit = (m.get("unit") or "").strip()
            # 兩道驗證：定名要在候選裡，單元名要逐字對得上目錄。少了這兩道，
            # 模型憑空補一個章節名就會產生一條「點進去是別本書」的連結。
            if t not in by_title or unit not in by_label:
                continue
            if t in seen:
                continue
            seen.add(t)
            w = by_title[t]
            results.append({
                "title_zh": t, "author": w.get("author", ""),
                "era": w["era"], "coll": w["coll"], "canon": w["canon"],
                "ebook_id": b["id"], "book_title": b["title"],
                "unit": unit, "page": by_label[unit]["page"],
                "confidence": m.get("confidence"),
                "link": f"/fathers/{b['id']}?page={by_label[unit]['page']}",
            })
            kept += 1
        print(f"    採用 {kept} 筆（模型回 {len(data.get('matches', []))} 筆）")

    # 原始結果先落地，之後調閘用 --from-jsonl 重跑就好，不必再打一輪 LLM
    Path(a.out).with_suffix(".raw.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results), encoding="utf-8")
    return finish(results, len(targets), Path(a.out), a.min_confidence)


def finish(results: list[dict], total: int, out: Path, min_conf: float) -> int:
    """三道閘 → 報告。與主流程分開，好讓 --from-jsonl 走同一段。"""
    lowconf = [r for r in results if (r.get("confidence") or 0) < min_conf]
    results = [r for r in results if (r.get("confidence") or 0) >= min_conf]
    if lowconf:
        print(f"信心低於 {min_conf} 不採用 {len(lowconf)} 條")

    results, clashes = split_ambiguous(results)
    if clashes:
        print(f"{sum(len(g) for g in clashes)} 卷因「該冊未分篇、數卷同頁」不採用"
              f"（{len(clashes)} 組）")

    out.write_text(render(results, clashes, lowconf, total, min_conf), encoding="utf-8")
    out.with_suffix(".jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results), encoding="utf-8")
    print(f"解析出 {len(results)} / {total} 條逐卷連結")
    print(f"審閱表 → {out}")
    print(f"資料   → {out.with_suffix('.jsonl')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
