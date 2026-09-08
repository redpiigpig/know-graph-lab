#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把《無境界者》的〈基督宗教譜系學〉五卷組裝成 /works 書稿（idempotent，可重跑）。

正本在無境界者網站的 Supabase `articles`（不是 Drive 的 docx——docx 那份帶著雜誌
排版的圖框錨點，而 DB 這份已經是乾淨 HTML 加結構化註腳）。本腳本抓回來、轉成
書稿格式，寫進 public/content/works/christian-genealogy/。

  卷〇  從使徒到大公                  第12期（未刊）
  卷一  尼西亞基督教的形成            第5期  2025.10
  卷二  基督宗教的七個大公傳統        第7期  2026.02
  卷三  基督新教的八大宗派系統        第10期（未刊）
  卷四  從宗派到陣營                  第11期（未刊；DB 副標誤植為「（五）」）

番外篇〈主教制的歷史演變與教會的大公性〉（第8期）依作者決定不收入本書。

轉換做四件事：
  1. <h3> 節標題 → <h2>，每節包成 <section class="chapter">
  2. 註號重新掛錨（#footnote-N → #fn-g0-N），註文按「這一節引到誰」分配到節末
  3. 未產圖的 [[圖片N]] 佔位符：拿掉 <img>，圖說留著並標明「圖待製」
  4. 卷首補 book-head（卷次、題名、提要、出處）

用法：
  python scripts/christian_genealogy_build.py            # 連線抓取後建置
  python scripts/christian_genealogy_build.py --cache    # 只用快取重建（免連線）
  python scripts/christian_genealogy_build.py --check    # 只驗算不寫檔
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public" / "content" / "works" / "christian-genealogy"
CACHE = ROOT / "output" / "christian-genealogy" / "source.json"
NONCHURCH_ENV = Path("C:/Users/user/Desktop/nonchurch-nuxt/.env")

VOLUMES = [
    {
        "id": "G0",
        "article": "12-5從使徒到大公",
        "vol": "卷〇",
        "sub": "尼西亞以前的見證網絡、使徒軌跡與城市傳統",
        "cite": "原稿：《無境界者》第12期（未刊）。",
    },
    {
        "id": "G1",
        "article": "5-9尼西亞基督教的形成",
        "vol": "卷一",
        "sub": "正統的劃界",
        "cite": "原刊：《無境界者》第5期（2025.10），頁55-72。",
    },
    {
        "id": "G2",
        "article": "7-16基督宗教的七個大公傳統",
        "vol": "卷二",
        "sub": "教系的成形",
        "cite": "原刊：《無境界者》第7期（2026.02），頁212-229。",
    },
    {
        "id": "G3",
        "article": "10-14基督新教的八大宗派系統",
        "vol": "卷三",
        "sub": "宗派的裂變",
        "cite": "原稿：《無境界者》第10期（未刊）。",
    },
    {
        "id": "G4",
        "article": "11-6從宗派到陣營",
        "vol": "卷四",
        "sub": "近現代的重組",
        "cite": "原稿：《無境界者》第11期（未刊）。DB 副標誤植為「初探（五）」，"
        "書稿依作者定序列為卷四。",
    },
]

BOOK = "基督宗教譜系學"


# ── 取源 ────────────────────────────────────────────────────────────────
def fetch() -> dict:
    cfg = {}
    for line in NONCHURCH_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            cfg[k.strip()] = v.strip().strip('"')
    url = cfg["VITE_SUPABASE_URL"].rstrip("/")
    key = cfg.get("SUPABASE_SECRET_KEY") or cfg["VITE_SUPABASE_KEY"]
    out = {}
    for v in VOLUMES:
        r = requests.get(
            f"{url}/rest/v1/articles",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "select": "id,title,subtitle,author,author_title,keyword,summary,"
                "content,footnotes,issue,is_published",
                "id": f"eq.{v['article']}",
            },
            timeout=60,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            raise SystemExit(f"找不到文章 {v['article']}")
        out[v["article"]] = rows[0]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ── 轉換 ────────────────────────────────────────────────────────────────
PLACEHOLDER_IMG = re.compile(r'<img src="\[\[[^\]]*\]\]"[^>]*>')
FIG_EMPTY = re.compile(r'(<figure[^>]*>)\s*(<figcaption>)')
REF = re.compile(
    r'<sup class="footnote-ref"><a href="#footnote-(\d+)" id="footnote-ref-\d+">'
    r"(\d+)</a></sup>"
)
H3 = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
SUP = re.compile(r'<sup class="footnote-ref">.*?</sup>', re.S)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def render(vol: dict, art: dict) -> tuple[str, dict]:
    vid = vol["id"].lower()
    content = art["content"] or ""
    notes = {int(f["id"]): f["text"] for f in (art.get("footnotes") or [])}

    # 未產圖的佔位符：<img> 拿掉，圖說留下並標明
    n_todo_img = len(PLACEHOLDER_IMG.findall(content))
    content = PLACEHOLDER_IMG.sub("", content)
    content = FIG_EMPTY.sub(r'\1<figcaption><strong>［圖待製］</strong>', content)

    # 註號改掛書稿的錨點
    def reref(m):
        n = m.group(1)
        return (
            f'<sup class="footnote-ref">'
            f'<a href="#fn-{vid}-{n}" id="fnref-{vid}-{n}">{m.group(2)}</a></sup>'
        )

    content = REF.sub(reref, content)

    # 依 <h3> 切節
    parts = H3.split(content)
    lead, pairs = parts[0], list(zip(parts[1::2], parts[2::2]))
    if strip_tags(lead):
        pairs.insert(0, ("弁言", lead))

    used, missing = set(), []
    chunks = []
    for i, (title, body) in enumerate(pairs, 1):
        # 節標題本身可能掛著註號（卷一第6節就是），剝標籤前要先把它接住，
        # 否則那條註文會變成沒有人引用的孤兒。
        head_ids = [int(x) for x in re.findall(rf'href="#fn-{vid}-(\d+)"', title)]
        title = strip_tags(SUP.sub("", title))
        head_sup = "".join(
            f'<sup class="footnote-ref">'
            f'<a href="#fn-{vid}-{n}" id="fnref-{vid}-{n}">{n}</a></sup>'
            for n in head_ids
        )
        ids = head_ids + [int(x) for x in re.findall(rf'href="#fn-{vid}-(\d+)"', body)]
        used.update(ids)
        fns = []
        for n in sorted(dict.fromkeys(ids)):
            if n not in notes:
                missing.append(n)
                continue
            fns.append(
                f'<div class="fn-item" id="fn-{vid}-{n}"><span class="fn-num">{n}</span>'
                f'<div class="fn-body">{notes[n]}'
                f'<a href="#fnref-{vid}-{n}" class="footnote-backref">↩</a></div></div>'
            )
        block = f'<div class="footnotes">{"".join(fns)}</div>' if fns else ""
        chunks.append(
            f'<section class="chapter"><h2>第{i}節　{html.escape(title)}{head_sup}</h2>\n'
            f"{body.strip()}\n{block}</section>\n"
        )

    kw = re.sub(r"^[🌿\s]*關鍵字[：:]\s*", "", (art.get("keyword") or "").strip())
    thesis = html.escape(art.get("summary") or "")
    if kw:
        thesis += f'<br /><br /><strong>關鍵字：</strong>{html.escape(kw)}'
    status = "已刊" if art.get("is_published") else "未刊稿"

    head = (
        '<header class="book-head">'
        f'<p class="book-kicker">{BOOK}‧{vol["vol"]}</p>'
        f'<h1 class="book-title">{html.escape(art["title"])}</h1>'
        f'<p class="book-sub">{html.escape(vol["sub"])}</p>'
        f'<p class="book-thesis">{thesis}</p>'
        f'<p class="book-meta">{html.escape(art.get("author") or "張辰瑋")}　　'
        f'{html.escape(vol["cite"])}　　書稿版依原稿轉錄，尚未為成書改寫。</p>'
        "</header>\n"
    )
    stats = {
        "sections": len(pairs),
        "notes": len(notes),
        "used": len(used),
        "orphan": sorted(set(notes) - used),
        "missing": sorted(set(missing)),
        "todo_img": n_todo_img,
    }
    return head + "\n".join(chunks), stats


def main() -> int:
    check = "--check" in sys.argv
    src = json.loads(CACHE.read_text(encoding="utf-8")) if "--cache" in sys.argv else fetch()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, bad = [], 0
    for vol in VOLUMES:
        art = src[vol["article"]]
        out, st = render(vol, art)
        flag = "OK  "
        if st["missing"] or st["orphan"]:
            flag, bad = "WARN", bad + 1
        print(
            f'{flag} {vol["id"]} {vol["vol"]}　{art["title"]}　'
            f'{st["sections"]} 節 / 註 {st["used"]}用 {st["notes"]}條'
            + (f' / 孤兒註 {st["orphan"]}' if st["orphan"] else "")
            + (f' / 缺註文 {st["missing"]}' if st["missing"] else "")
            + (f' / 圖待製 {st["todo_img"]}' if st["todo_img"] else "")
            + f' / {len(out):,} 字元'
        )
        if not check:
            (OUT_DIR / f'{vol["id"]}.html').write_text(out, encoding="utf-8")
        manifest.append(
            {
                "id": vol["id"],
                "title": f'{vol["vol"]}　{art["title"]}',
                "subtitle": vol["sub"],
                "file": f'/content/works/christian-genealogy/{vol["id"]}.html',
                "nChapters": st["sections"],
            }
        )

    if not check:
        (OUT_DIR.parent / "christian-genealogy-books.json").write_text(
            json.dumps(
                {
                    "series": BOOK,
                    "note": "五卷。把《無境界者》連載的〈基督宗教譜系學〉合成一書："
                    "卷〇追到尼西亞以前的見證網絡與城市傳統，卷一講正統如何被劃界，"
                    "卷二講七個大公傳統如何成形，卷三解剖新教的八大宗派系統，"
                    "卷四處理近現代「宗派之外」的陣營重組。"
                    "第8期的番外篇〈主教制的歷史演變與教會的大公性〉不收入本書。"
                    "各卷目前皆為原稿轉錄，成書改寫與統一體例尚未進行。",
                    "independent": True,
                    "books": manifest,
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
