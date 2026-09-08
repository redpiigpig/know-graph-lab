#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""組裝《基督宗教譜系學》的 /works 書稿（idempotent，可重跑）。

全書目錄在 `christian_genealogy_plan.py`。每一卷有兩種可能的內容：

  改寫稿  public/content/works/christian-genealogy/chapters-gX/chNN.html
          成書用的正式章節，人工逐章寫，寫好一章放一個檔。
  雜誌原稿 無境界者網站 Supabase `articles` 的 content + footnotes
          《無境界者》連載的原文，轉錄用。

規則：**該卷的章目全部改寫完才換上改寫稿**，否則仍出雜誌原稿——半新半舊讀起來
會像同一卷有兩個作者。導論沒有原稿，所以寫幾章就出幾章。

取源刻意不走 Drive 的 docx：那份是雜誌排版稿，正文混著圖框錨點、標題只能靠
「粗體 14pt」猜、註腳要自己挖 XML；而且卷一、卷四、卷五（原第12、10、11 期）
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
from christian_genealogy_plan import BOOK, SUBTITLE, VOLUMES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public" / "content" / "works" / "christian-genealogy"
CACHE = ROOT / "output" / "christian-genealogy" / "source.json"
NONCHURCH_ENV = Path("C:/Users/user/Desktop/nonchurch-nuxt/.env")

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
    for v in VOLUMES:
        if not v["source"]:
            continue
        r = requests.get(
            f"{url}/rest/v1/articles",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "select": "id,title,subtitle,author,keyword,summary,content,"
                "footnotes,issue,is_published",
                "id": f"eq.{v['source']}",
            },
            timeout=60,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            raise SystemExit(f"找不到文章 {v['source']}")
        out[v["source"]] = rows[0]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


PLACEHOLDER_IMG = re.compile(r'<img src="\[\[[^\]]*\]\]"[^>]*>')
FIG_EMPTY = re.compile(r"(<figure[^>]*>)\s*(<figcaption>)")
REF = re.compile(
    r'<sup class="footnote-ref"><a href="#footnote-(\d+)" id="footnote-ref-\d+">'
    r"(\d+)</a></sup>"
)
H3 = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
SUP = re.compile(r'<sup class="footnote-ref">.*?</sup>', re.S)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def fn_block(vid: str, pairs: list[tuple[int, str]]) -> str:
    if not pairs:
        return ""
        # noqa
    items = "".join(
        f'<div class="fn-item" id="fn-{vid}-{n}"><span class="fn-num">{n}</span>'
        f'<div class="fn-body">{body}'
        f'<a href="#fnref-{vid}-{n}" class="footnote-backref">↩</a></div></div>'
        for n, body in pairs
    )
    return f'<div class="footnotes">{items}</div>'


def render_source(vol: dict, art: dict) -> tuple[str, dict]:
    """雜誌原稿 → 書稿卷（<h3> 升成章，註腳按章分配）。"""
    vid = vol["id"].lower()
    content = art["content"] or ""
    notes = {int(f["id"]): f["text"] for f in (art.get("footnotes") or [])}

    n_todo_img = len(PLACEHOLDER_IMG.findall(content))
    content = PLACEHOLDER_IMG.sub("", content)
    content = FIG_EMPTY.sub(r"\1<figcaption><strong>［圖待製］</strong>", content)
    content = REF.sub(
        lambda m: f'<sup class="footnote-ref">'
        f'<a href="#fn-{vid}-{m.group(1)}" id="fnref-{vid}-{m.group(1)}">'
        f"{m.group(2)}</a></sup>",
        content,
    )

    parts = H3.split(content)
    lead, pairs = parts[0], list(zip(parts[1::2], parts[2::2]))
    if strip_tags(lead):
        pairs.insert(0, ("弁言", lead))

    used, missing, chunks = set(), [], []
    for i, (title, body) in enumerate(pairs, 1):
        head_ids = [int(x) for x in re.findall(rf'href="#fn-{vid}-(\d+)"', title)]
        plain = strip_tags(SUP.sub("", title))
        head_sup = "".join(
            f'<sup class="footnote-ref">'
            f'<a href="#fn-{vid}-{n}" id="fnref-{vid}-{n}">{n}</a></sup>'
            for n in head_ids
        )
        ids = head_ids + [int(x) for x in re.findall(rf'href="#fn-{vid}-(\d+)"', body)]
        used.update(ids)
        fns = []
        for n in sorted(dict.fromkeys(ids)):
            if n in notes:
                fns.append((n, notes[n]))
            else:
                missing.append(n)
        chunks.append(
            f'<section class="chapter"><h2>第{i}章　{html.escape(plain)}{head_sup}</h2>\n'
            f"{body.strip()}\n{fn_block(vid, fns)}</section>\n"
        )

    stats = {
        "mode": "原稿",
        "chapters": len(pairs),
        "used": len(used),
        "notes": len(notes),
        "orphan": sorted(set(notes) - used),
        "missing": sorted(set(missing)),
        "todo_img": n_todo_img,
    }
    return "\n".join(chunks), stats


def render_rewrite(vol: dict, files: list[Path]) -> tuple[str, dict]:
    """改寫稿 → 書稿卷。章檔本身已是 <section class="chapter">…</section>。"""
    body = "\n".join(f.read_text(encoding="utf-8").strip() for f in files)
    vid = vol["id"].lower()
    refs = set(re.findall(rf'id="fnref-{vid}-([\w-]+)"', body))
    tgts = set(re.findall(rf'id="fn-{vid}-([\w-]+)"', body))
    return body, {
        "mode": "改寫",
        "chapters": body.count('<section class="chapter">'),
        "used": len(refs),
        "notes": len(tgts),
        "orphan": sorted(tgts - refs),
        "missing": sorted(refs - tgts),
        "todo_img": 0,
    }


def head_html(vol: dict, thesis: str, meta: str) -> str:
    return (
        '<header class="book-head">'
        f'<p class="book-kicker">{BOOK}‧{vol["vol"]}</p>'
        f'<h1 class="book-title">{html.escape(vol["title"])}</h1>'
        f'<p class="book-sub">{html.escape(vol["sub"])}</p>'
        f'<p class="book-thesis">{thesis}</p>'
        f'<p class="book-meta">{meta}</p>'
        "</header>\n"
    )


def main() -> int:
    check = "--check" in sys.argv
    need_src = any(v["source"] for v in VOLUMES)
    src = {}
    if need_src:
        src = (
            json.loads(CACHE.read_text(encoding="utf-8"))
            if "--cache" in sys.argv or check and CACHE.exists()
            else fetch()
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, bad = [], 0
    for vol in VOLUMES:
        vid = vol["id"].lower()
        cdir = OUT_DIR / f"chapters-{vid}"
        files = sorted(cdir.glob("ch*.html")) if cdir.exists() else []
        planned = len(vol["chapters"])
        complete = len(files) >= planned

        if files and (complete or not vol["source"]):
            body, st = render_rewrite(vol, files)
            thesis = html.escape(vol["sub"])
            meta = (
                f"張辰瑋　　成書稿．已改寫 {len(files)}／{planned} 章"
                + (f"　　據 {html.escape(CITE.get(vol['source'], ''))} 改寫" if vol["source"] else "")
            )
        elif vol["source"]:
            art = src[vol["source"]]
            body, st = render_source(vol, art)
            thesis = html.escape(art.get("summary") or vol["sub"])
            meta = (
                f'張辰瑋　　<strong>雜誌原稿轉錄</strong>，尚未為成書改寫'
                f'（已改寫 {len(files)}／{planned} 章）　　'
                f'原刊 {html.escape(CITE.get(vol["source"], ""))}'
            )
        else:
            continue  # 導論還沒動筆

        out = head_html(vol, thesis, meta) + body
        flag = "OK  "
        if st["missing"] or st["orphan"]:
            flag, bad = "WARN", bad + 1
        print(
            f'{flag} {vol["id"]} {vol["vol"]}　{vol["title"]}　[{st["mode"]}] '
            f'{st["chapters"]}/{planned} 章 / 註 {st["used"]}引 {st["notes"]}條'
            + (f' / 孤兒註 {st["orphan"][:5]}' if st["orphan"] else "")
            + (f' / 缺註文 {st["missing"][:5]}' if st["missing"] else "")
            + (f' / 圖待製 {st["todo_img"]}' if st["todo_img"] else "")
            + f' / {len(out):,} 字元'
        )
        if not check:
            (OUT_DIR / f'{vol["id"]}.html').write_text(out, encoding="utf-8")
        manifest.append(
            {
                "id": vol["id"],
                "title": f'{vol["vol"]}　{vol["title"]}',
                "subtitle": vol["sub"] + ("" if st["mode"] == "改寫" else "（雜誌原稿）"),
                "file": f'/content/works/christian-genealogy/{vol["id"]}.html',
                "nChapters": st["chapters"],
            }
        )

    if not check:
        (OUT_DIR.parent / "christian-genealogy-books.json").write_text(
            json.dumps(
                {
                    "series": BOOK,
                    "note": f"{SUBTITLE}。導論立方法，五卷依分化四階段推進："
                    "卷一追到尼西亞以前的見證網絡與城市傳統，卷二講正統如何被劃界，"
                    "卷三講七個大公傳統如何成形，卷四解剖新教的八大宗派系統，"
                    "卷五處理近現代「宗派之外」的陣營重組。"
                    "底本是《無境界者》第5、7、10、11、12 期的連載，"
                    "第8期的番外篇〈主教制的歷史演變與教會的大公性〉不收入本書。"
                    "標「雜誌原稿」的卷還沒為成書改寫。",
                    "independent": True,
                    "unit": "卷",
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
