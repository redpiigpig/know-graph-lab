#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""組裝《基督宗教譜系學》的 /works 書稿（idempotent，可重跑）。

全書目錄在 `christian_genealogy_plan.py`：一本書、六章。輸出單一檔
public/content/works/christian-genealogy/CG.html，每章一個 <section class="chapter">，
章內的節是 <h3>。

每一章有兩種可能的內容：

  改寫稿   public/content/works/christian-genealogy/chapters-cN/sNN.html
           成書用的正式節，人工逐節寫，寫好一節放一個檔。
  雜誌原稿 無境界者網站 Supabase `articles` 的 content + footnotes

規則：**該章的節全部寫完才換上改寫稿**，否則仍出雜誌原稿。方法論那章沒有原稿，
所以寫幾節出幾節。

取源刻意不走 Drive 的 docx：那份是雜誌排版稿，正文混著圖框錨點、標題只能靠
「粗體 14pt」猜、註腳要自己挖 XML；而且第2、5、6 章的底本（第12、10、11 期）
根本沒有 docx，只存在於 DB。

用法：
  python scripts/christian_genealogy_build.py            # 連線抓原稿後建置
  python scripts/christian_genealogy_build.py --cache    # 用快取重建（免連線）
  python scripts/christian_genealogy_build.py --check    # 只驗算不寫檔
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from christian_genealogy_plan import BOOK, CHAPTERS, SUBTITLE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public" / "content" / "works" / "christian-genealogy"
CACHE = ROOT / "output" / "christian-genealogy" / "source.json"
NONCHURCH_ENV = Path("C:/Users/user/Desktop/nonchurch-nuxt/.env")
BOOK_ID = "CG"

CITE = {
    "12-5從使徒到大公": "《無境界者》第12期（未刊）",
    "5-9尼西亞基督教的形成": "《無境界者》第5期（2025.10），頁55-72",
    "7-16基督宗教的七個大公傳統": "《無境界者》第7期（2026.02），頁212-229",
    "10-14基督新教的八大宗派系統": "《無境界者》第10期（未刊）",
    "11-6從宗派到陣營": "《無境界者》第11期（未刊）",
}


# ── 雜誌原稿 ────────────────────────────────────────────────────────────
def fetch() -> dict:
    cfg = {}
    for line in NONCHURCH_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            cfg[k.strip()] = v.strip().strip('"')
    url = cfg["VITE_SUPABASE_URL"].rstrip("/")
    key = cfg.get("SUPABASE_SECRET_KEY") or cfg["VITE_SUPABASE_KEY"]
    out = {}
    for ch in CHAPTERS:
        if not ch["source"]:
            continue
        r = requests.get(
            f"{url}/rest/v1/articles",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "select": "id,title,subtitle,author,keyword,summary,content,"
                "footnotes,issue,is_published",
                "id": f"eq.{ch['source']}",
            },
            timeout=60,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            raise SystemExit(f"找不到文章 {ch['source']}")
        out[ch["source"]] = rows[0]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


PLACEHOLDER_IMG = re.compile(r'<img src="\[\[[^\]]*\]\]"[^>]*>')
FIG_EMPTY = re.compile(r"(<figure[^>]*>)\s*(<figcaption>)")
SRC_REF = re.compile(
    r'<sup class="footnote-ref"><a href="#footnote-(\d+)" id="footnote-ref-\d+">'
    r"(\d+)</a></sup>"
)
SUP_REF = re.compile(
    r'<sup class="footnote-ref"><a href="#(fn-[\w-]+)" id="fnref-[\w-]+">\d+</a></sup>'
)
FN_ITEM = re.compile(r'<div class="fn-item" id="(fn-[\w-]+)"><span class="fn-num">\d+</span>')
FN_BACK = re.compile(r'<a href="#fnref-([\w-]+)" class="footnote-backref">')
# 連號之後用來把區塊內的條目排序（見 sort_fn_items）
FN_ITEM_WHOLE = re.compile(r'<div class="fn-item" id="fn-(\d+)">.*?</div></div>', re.S)
DIV_TAG = re.compile(r"<div\b|</div>")


def renumber(body: str) -> tuple[str, list[str]]:
    """全書註號按出現順序重編。

    節檔各自寫作，作者不可能記得上一節編到第幾號；硬要人工維護，遲早會在兩節之間
    撞號而且頁面看起來完全正常。所以節檔裡的 id 只要在全書唯一即可（fn-c1-a 這種
    也行），連號交給這裡做。
    """
    order: dict[str, int] = {}

    def ref(m):
        key = m.group(1)
        if key not in order:
            order[key] = len(order) + 1
        n = order[key]
        return (
            f'<sup class="footnote-ref">'
            f'<a href="#fn-{n}" id="fnref-{n}">{n}</a></sup>'
        )

    body = SUP_REF.sub(ref, body)
    orphans: list[str] = []

    def item(m):
        key = m.group(1)
        if key not in order and key not in orphans:
            orphans.append(key)
        n = order.get(key, 0)
        return f'<div class="fn-item" id="fn-{n}"><span class="fn-num">{n}</span>'

    body = FN_ITEM.sub(item, body)
    # 回鏈寫的是 #fnref-<key 去掉 fn- 前綴>，換算回 order 的鍵要把 fn- 補回去
    body = FN_BACK.sub(
        lambda m: f'<a href="#fnref-{order.get("fn-" + m.group(1), 0)}"'
        f' class="footnote-backref">',
        body,
    )
    return sort_fn_items(body), orphans


def sort_fn_items(body: str) -> str:
    """把每個註釋區塊裡的條目按註號排好。

    條目的順序來自節檔的書寫順序，而書寫順序不一定等於引用順序——正文改過一輪、
    某一條註被搬到別段之後就會錯開。頁面照樣長得好好的，只是註釋清單變成
    1、2、8、5、6⋯⋯，要一條一條看才發現。連號交給 renumber 之後，這裡再按號排序，
    往後就不會再犯。
    """

    out, pos = [], 0
    marker = '<div class="footnotes">'
    while (start := body.find(marker, pos)) != -1:
        inner = start + len(marker)
        # 用 div 深度找出區塊真正的結尾——fn-item 裡還有兩層 div，
        # 靠正則前瞻猜結尾會在某一章吃掉下一章的開頭（試過，會靜默少一章）
        depth, end = 1, inner
        for t in DIV_TAG.finditer(body, inner):
            depth += 1 if t.group(0) == "<div" else -1
            if depth == 0:
                end = t.start()
                break
        else:
            break
        block = body[inner:end]
        items = [m.group(0) for m in FN_ITEM_WHOLE.finditer(block)]
        if len(items) > 1:
            ordered = sorted(items, key=lambda s: int(FN_ITEM_WHOLE.match(s).group(1)))
            if ordered != items:
                block = "\n" + "\n".join(ordered) + "\n"
        out.append(body[pos:inner] + block)
        pos = end
    out.append(body[pos:])
    return "".join(out)


def source_body(art: dict) -> tuple[str, int]:
    """雜誌原稿 → 章內容。原稿的 <h3> 就是節，原樣保留。"""
    content = art["content"] or ""
    n_todo_img = len(PLACEHOLDER_IMG.findall(content))
    content = PLACEHOLDER_IMG.sub("", content)
    content = FIG_EMPTY.sub(r"\1<figcaption><strong>［圖待製］</strong>", content)
    # 原稿的註號改成本書的暫時鍵，交給 renumber 統一連號
    content = SRC_REF.sub(
        lambda m: f'<sup class="footnote-ref">'
        f'<a href="#fn-{art["id"][:4]}-{m.group(1)}" '
        f'id="fnref-{art["id"][:4]}-{m.group(1)}">{m.group(2)}</a></sup>',
        content,
    )
    notes = "".join(
        f'<div class="fn-item" id="fn-{art["id"][:4]}-{f["id"]}">'
        f'<span class="fn-num">{f["id"]}</span>'
        f'<div class="fn-body">{f["text"]}'
        f'<a href="#fnref-{art["id"][:4]}-{f["id"]}" class="footnote-backref">↩</a>'
        f"</div></div>"
        for f in (art.get("footnotes") or [])
    )
    if notes:
        content += f'<div class="footnotes">{notes}</div>'
    return content, n_todo_img


def main() -> int:
    check = "--check" in sys.argv
    src = {}
    if any(c["source"] for c in CHAPTERS):
        use_cache = "--cache" in sys.argv or (check and CACHE.exists())
        src = json.loads(CACHE.read_text(encoding="utf-8")) if use_cache else fetch()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parts, rows, todo_img = [], [], 0
    for i, ch in enumerate(CHAPTERS, 1):
        cdir = OUT_DIR / f"chapters-{ch['id']}"
        files = sorted(cdir.glob("s*.html")) if cdir.exists() else []
        planned = len(ch["sections"])
        rewritten = len(files) >= planned

        if files and (rewritten or not ch["source"]):
            body = "\n".join(f.read_text(encoding="utf-8").strip() for f in files)
            mode = "改寫" if rewritten else f'改寫中 {len(files)}/{planned}'
        elif ch["source"]:
            body, n_img = source_body(src[ch["source"]])
            todo_img += n_img
            mode = "原稿"
        else:
            body, mode = "", "未動筆"

        if not body:
            rows.append((ch, mode, 0))
            continue

        note = (
            f'<p class="chapter-source">{html.escape(ch["sub"])}　·　'
            + (
                f'據 {html.escape(CITE.get(ch["source"], ""))} 改寫'
                if mode == "改寫" and ch["source"]
                else f'<strong>雜誌原稿轉錄</strong>，尚未為成書改寫（原刊 '
                f'{html.escape(CITE.get(ch["source"], ""))}）'
                if mode == "原稿"
                else f'成書稿．{html.escape(mode)} 節'
                if mode.startswith("改寫中")
                else "成書稿"
            )
            + "</p>"
        )
        parts.append(
            f'<section class="chapter"><h2>第{i}章　{html.escape(ch["title"])}</h2>\n'
            f"{note}\n{body}\n</section>\n"
        )
        rows.append((ch, mode, len(files)))

    body_all, orphans = renumber("\n".join(parts))
    refs = len(set(re.findall(r'id="fnref-(\d+)"', body_all)))
    tgts = len(set(re.findall(r'id="fn-(\d+)"', body_all)))

    head = (
        '<header class="book-head">'
        f'<p class="book-kicker">張辰瑋</p>'
        f'<h1 class="book-title">{html.escape(BOOK)}</h1>'
        f'<p class="book-sub">{html.escape(SUBTITLE)}</p>'
        '<p class="book-thesis">全書六章：一章立方法，五章依四次事件推進。'
        '主張是——<strong>基督宗教的分化不是墮落，是信仰適應環境所留下的痕跡；'
        '而每一次大事件之後，判斷「兩個群體算不算分開了」的單位本身就換了一次。'
        '</strong>因此起源、正統化、改教、現代化四個時期必須用四種不同的譜系單位'
        '來敘述：記憶的保存者、教座與宗主教集團、認信文書與會祖、立場與運動。'
        '<br /><br />底本是《無境界者》第12、5、7、10、11 期的連載；'
        '第8期的番外篇〈主教制的歷史演變與教會的大公性〉不收入本書。</p>'
        f'<p class="book-meta">標「雜誌原稿」的章尚未為成書改寫。</p>'
        "</header>\n"
    )
    out = head + body_all

    for ch, mode, n in rows:
        print(f'  第{CHAPTERS.index(ch) + 1}章 {ch["title"]:<12s} [{mode}]')
    flag = "WARN" if orphans else "OK  "
    print(
        f'{flag} {BOOK}　{len(parts)}/{len(CHAPTERS)} 章 / 註 {refs}引 {tgts}條'
        + (f" / 孤兒註 {orphans[:5]}" if orphans else "")
        + (f" / 圖待製 {todo_img}" if todo_img else "")
        + f" / {len(out):,} 字元"
    )

    if not check:
        (OUT_DIR / f"{BOOK_ID}.html").write_text(out, encoding="utf-8")
        (OUT_DIR.parent / "christian-genealogy-books.json").write_text(
            json.dumps(
                {
                    "series": BOOK,
                    "note": f"{SUBTITLE}。一章立方法，五章依四次事件推進。"
                    "底本是《無境界者》第12、5、7、10、11 期的五篇連載；"
                    "第8期的番外篇〈主教制的歷史演變與教會的大公性〉不收入本書。",
                    "independent": True,
                    "books": [
                        {
                            "id": BOOK_ID,
                            "title": BOOK,
                            "subtitle": SUBTITLE,
                            "file": f"/content/works/christian-genealogy/{BOOK_ID}.html",
                            "nChapters": len(parts),
                        }
                    ],
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )
    return 1 if orphans else 0


if __name__ == "__main__":
    raise SystemExit(main())
