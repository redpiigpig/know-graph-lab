"""把《阿拉伯語耶穌嬰孩時期福音》與《拉丁語耶穌嬰孩時期福音》收進 /apocrypha。

    python scripts/ingest_infancy_gospels.py --dry-run
    python scripts/ingest_infancy_gospels.py --write

兩篇都出自《基督教典外文獻・新約篇》第一冊（黃錫木主編），所以版本碼就是
`cct_zh`——與《猶大福音》不同，那一篇不在這套書裡才要另立版本碼。

🚨 為什麼不吃 mineru_ocr.py 產的 jsonl，而回頭讀 middle.json：
   jsonl 只有 preproc_blocks 的正文。MinerU 把**頁碼與註腳**放在
   `discarded_blocks`（型別 page_number／page_footnote），只讀正文那一路會
   同時違反兩條硬規定——註釋要收、原書頁碼要留。實測阿拉伯語那篇有 26 條
   註腳、22 個頁碼區塊，全都在 discarded_blocks 裡。

🚨 頁碼不用推算，用頁面上印的那一個。章首頁（版心不印頁碼）才回退到
   前後頁推出來，而且推完要跟頁序對得起來才放行。

🚨 節號有兩個被 OCR 吃掉（阿拉伯語 §5、§7）。第一版拿「這段看起來像不像
   新一節」去補，結果把**跨頁的續段**全judged成新節——55 節照樣連號、字數
   照樣對得上、閘照樣全過，但每一節的界線都往前挪了一段。這正是最難發現
   的那種錯：印出來一切正常。

   所以補號改成寫死的對照表 MISSING_NUM：只認那兩節開頭的原文。找不到、
   找到多個、或位置不在前後兩節之間，一律擋下不寫。其餘沒帶號的段落一律
   併進當前節，不做任何推測。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MID_DIR = Path(r"C:\Users\user\AppData\Local\Temp\claude"
               r"\c--Users-user-Desktop-know-graph-lab"
               r"\d58e3d0f-6f31-498e-b30f-2a931a54d6bc\scratchpad\mineru-out")

DOCS = {
    "infancy-arabic": {
        "title": "阿拉伯語耶穌嬰孩時期福音",
        "first_section": 1, "last_section": 55,
        "printed_from": 110, "printed_to": 132,
    },
    "infancy-latin": {
        "title": "拉丁語耶穌嬰孩時期福音（阿倫德爾抄本404）",
        "first_section": 68, "last_section": 74,
        "printed_from": 150, "printed_to": 154,
    },
}

VERSION_CODE = "cct_zh"

# OCR 把這幾節的節號吃掉了（那幾個數字是段首的大字，MinerU 沒認出來）。
# 值是該節開頭的原文，用來定位；比對不到就當作管線壞了，不寫入。
MISSING_NUM = {
    "infancy-arabic": {5: "行割禮的時候快到了", 7: "主耶穌在猶太省的伯利恆出世"},
    "infancy-latin": {},
}
# 節號後面可以接中文、引號、括號或刪節號——拉丁語 §68 後面就是「……」，
# 只認中文字會靜默漏掉整整一節。
SEC_PAT = re.compile(r"^(\d{1,3})\s*(?=[\u4e00-\u9fff「」『』（）()《》〈〉…．\.])")
# 卷末的譯者／審閱署名，書上每一卷都有
CREDIT_PAT = re.compile(r"^(翻譯|審閱)[：:]")
# 書上的版面小標，不是內容，不必收
DROP_HEADINGS = {"文本", "簡介"}


# ── Supabase ──────────────────────────────────────────────────────────────

def env() -> dict[str, str]:
    return dict(l.strip().split("=", 1)
                for l in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines()
                if "=" in l and not l.startswith("#"))


def api(e):
    url = e["SUPABASE_URL"].rstrip("/")
    h = {"apikey": e["SUPABASE_SERVICE_ROLE_KEY"],
         "Authorization": "Bearer " + e["SUPABASE_SERVICE_ROLE_KEY"],
         "Content-Type": "application/json"}
    return url, h


# ── middle.json ───────────────────────────────────────────────────────────

def block_text(b: dict) -> str:
    if b.get("type") in ("table", "image"):
        b = (b.get("blocks") or [b])[0]
    return "\n".join(
        "".join(s.get("content", "") for s in (line.get("spans") or []))
        for line in (b.get("lines") or [])
    ).strip()


def read_middle(slug: str) -> list[dict]:
    hits = sorted(MID_DIR.rglob(f"{slug}_middle.json"))
    if not hits:
        raise SystemExit(f"找不到 {slug}_middle.json —— 先跑 MinerU 並保留輸出夾")
    mid = json.loads(hits[0].read_text(encoding="utf-8"))
    pages = []
    for page in mid.get("pdf_info") or []:
        disc = page.get("discarded_blocks") or []
        printed, notes = None, []
        for b in disc:
            t = block_text(b)
            if not t:
                continue
            if b.get("type") == "page_number":
                m = re.search(r"\d{2,4}", t)
                if m:
                    printed = int(m.group())
            elif b.get("type") == "page_footnote":
                notes.append(t)
        # 🚨 一個 preproc_block 就是一段，不要把它們接起來再用空行切回去：
        #    有些區塊（圖、空框）文字是空的，接起來會多出假空行，而真正的
        #    段落之間反而只有一個 \n——照空行切會切不出任何一段。
        paras = [t for t in (block_text(b) for b in (page.get("preproc_blocks") or [])) if t]
        pages.append({
            "idx": int(page.get("page_idx", len(pages))),
            "printed": printed,
            "notes": notes,
            "paras": paras,
            "body": "\n".join(paras),
        })
    pages.sort(key=lambda p: p["idx"])
    return pages


def fill_printed(slug: str, pages: list[dict], lo: int, hi: int) -> list[str]:
    """章首頁不印頁碼，用頁序補；補完必須與宣告的範圍完全吻合才放行。"""
    problems = []
    if hi - lo + 1 != len(pages):
        problems.append(f"{slug}：宣告印刷頁 {lo}–{hi} 共 {hi - lo + 1} 頁，"
                        f"實際 {len(pages)} 頁")
    for p in pages:
        want = lo + p["idx"]
        if p["printed"] is None:
            p["printed"] = want
            p["printed_inferred"] = True
        elif p["printed"] != want:
            problems.append(f"{slug}：頁索引 {p['idx']} 印的是 {p['printed']}，"
                            f"照頁序應為 {want}")
    return problems


# ── 切節 ──────────────────────────────────────────────────────────────────

def split_sections(slug: str, pages: list[dict], first: int, last: int):
    """回傳 (sections, intro_paras, problems)。

    先把全篇切成段落（帶著它所在的印刷頁），再一段一段走：
      · 段首有節號且等於「下一個該出現的號」→ 開新節
      · 段首沒節號，但下一個該出現的號還沒出現過，而且這一段位在
        「上一節之後、下一個有號的段落之前」→ 判為被 OCR 吃掉節號，補號
      · 其餘 → 併入當前節
    """
    paras: list[dict] = []
    for p in pages:
        for chunk in p["paras"]:
            paras.append({"page": p["printed"], "text": chunk})

    # 第一個帶節號的段落才是正文起點
    start = None
    for i, pa in enumerate(paras):
        m = SEC_PAT.match(pa["text"])
        if m and int(m.group(1)) == first:
            start = i
            break
    if start is None:
        return [], [], [f"{slug}：找不到第 {first} 節的起點"]

    # 書上用一個「文本」的小標把主編的簡介與文獻本身隔開。標題之前是簡介
    # （＋主編署名），之後、第一個節號之前是文獻自己的序言——阿拉伯語那篇
    # 的三一頌與書名開場白屬於後者，不是簡介。
    head = [pa for pa in paras[:start]]
    cut = next((i for i, pa in enumerate(head) if pa["text"].strip() == "文本"), None)
    if cut is None:
        intro_paras, prologue = head, []
    else:
        intro_paras, prologue = head[:cut], head[cut + 1:]
    intro = [pa["text"] for pa in intro_paras]

    sections: list[dict] = []
    for pa in paras[start:]:
        m = SEC_PAT.match(pa["text"])
        if m:
            sections.append({"n": int(m.group(1)), "page": pa["page"], "inferred": False,
                             "paras": [pa["text"][m.end():].strip()]})
        elif sections:
            # 沒帶號的段落一律併進當前節。跨頁續段長得就像新的一段，
            # 用「看起來像不像新一節」去猜會把每一節的界線都挪掉一段。
            sections[-1]["paras"].append(pa["text"])

    problems = []
    # ── 補回被吃掉的節號：只認寫死的開頭原文 ──
    for n, opening in sorted(MISSING_NUM.get(slug, {}).items()):
        host = [s_ for s_ in sections if any(x.startswith(opening) for x in s_["paras"])]
        if len(host) != 1:
            problems.append(f"{slug}：補 §{n} 失敗——「{opening}」比對到 {len(host)} 處")
            continue
        h = host[0]
        hits = [i for i, x in enumerate(h["paras"]) if x.startswith(opening)]
        if len(hits) != 1:
            problems.append(f"{slug}：補 §{n} 失敗——同一節裡比對到 {len(hits)} 段")
            continue
        if not (h["n"] < n):
            problems.append(f"{slug}：補 §{n} 失敗——它落在 §{h['n']} 裡，位置不合")
            continue
        i = hits[0]
        tail = h["paras"][i:]
        h["paras"] = h["paras"][:i]
        sections.insert(sections.index(h) + 1,
                        {"n": n, "page": h["page"], "inferred": True, "paras": tail})

    # 補出來的節，頁碼要用它自己所在的那一頁，不是宿主節的
    page_of = {}
    for p in pages:
        for t in p["paras"]:
            page_of.setdefault(t.strip(), p["printed"])
    for s_ in sections:
        if s_["inferred"] and s_["paras"]:
            s_["page"] = page_of.get(s_["paras"][0].strip(), s_["page"])

    # 版權尾（翻譯：… 審閱：…）不是正文，別留在末節裡
    credits = []
    if sections:
        keep = []
        for x in sections[-1]["paras"]:
            if CREDIT_PAT.match(x.strip()):
                credits.append(x.strip())
            else:
                keep.append(x)
        sections[-1]["paras"] = keep

    nums = [s_["n"] for s_ in sections]
    if nums != list(range(first, last + 1)):
        missing = sorted(set(range(first, last + 1)) - set(nums))
        dupes = sorted(n for n in set(nums) if nums.count(n) > 1)
        problems.append(f"{slug}：節號不是 {first}–{last} 連號　缺 {missing}　"
                        f"重複 {dupes}　實得 {nums}")
    return sections, {"intro": intro, "prologue": [pa["text"] for pa in prologue],
                      "credits": credits}, problems


# ── 主流程 ────────────────────────────────────────────────────────────────

def build(slug: str, cfg: dict):
    pages = read_middle(slug)
    problems = fill_printed(slug, pages, cfg["printed_from"], cfg["printed_to"])
    sections, front, p2 = split_sections(slug, pages, cfg["first_section"], cfg["last_section"])
    problems += p2
    intro, prologue, credits = front["intro"], front["prologue"], front["credits"]

    notes_by_page = {p["printed"]: p["notes"] for p in pages}
    rows = []
    if prologue:
        text = "\n".join(prologue).strip()
        first_page = next((p["printed"] for p in pages
                           if any(x.strip() == prologue[0].strip() for x in p["paras"])), None)
        rows.append({
            "doc_slug": slug, "version_code": VERSION_CODE, "order_index": 0,
            "section_label": "序", "section_label_clean": "序",
            "chapter": None, "verse": None, "page_number": first_page,
            "text": text, "char_count": len(text),
            "footnote_defs": notes_by_page.get(first_page) or None,
        })
    for i, s in enumerate(sections, start=len(rows)):
        text = "\n".join(x for x in s["paras"] if x).strip()
        rows.append({
            "doc_slug": slug,
            "version_code": VERSION_CODE,
            "order_index": i,
            "section_label": str(s["n"]),
            "section_label_clean": str(s["n"]),
            "chapter": s["n"],
            "verse": None,
            "page_number": s["page"],
            "text": text,
            "char_count": len(text),
            "footnote_defs": notes_by_page.get(s["page"]) or None,
        })

    # 🚨 字數對不對不是好閘：節號被切掉、段落接合符不同，本來就會差幾十字，
    #    差多少都能說成「正常」。改成逐段點名——每一個 preproc 段落都要在
    #    某一節／簡介／序言／版權尾裡找得到，找不到的列出來讓人看。
    assigned = set()
    for sec in sections:
        assigned.update(x.strip() for x in sec["paras"] if x.strip())
    assigned.update(x.strip() for x in intro)
    assigned.update(x.strip() for x in prologue)
    assigned.update(x.strip() for x in credits)

    orphans = []
    for pg in pages:
        for t in pg["paras"]:
            tt = t.strip()
            # 節首的號在入庫時被切掉了，去掉號再比一次；版權尾兩個署名
            # 有時黏成同一段，拆開比。
            cands = {tt, re.sub(r"^\d{1,3}\s*", "", tt).strip()}
            if cands & assigned:
                continue
            if all(any(part in a for a in assigned)
                   for part in re.split(r"(?=(?:翻譯|審閱)[：:])", tt) if part.strip()):
                continue
            if tt in DROP_HEADINGS:
                continue
            orphans.append((pg["printed"], tt))
    if orphans:
        problems.append(f"{slug}：有 {len(orphans)} 段沒被收進任何一處"
                        f"（例：p{orphans[0][0]}「{orphans[0][1][:40]}」）")

    body_chars = sum(len(p["body"]) for p in pages)
    kept_chars = (sum(r["char_count"] for r in rows)
                  + sum(len(x) for x in intro) + sum(len(x) for x in credits))
    return {"pages": pages, "rows": rows, "intro": intro, "credits": credits,
            "prologue": bool(prologue),
            "problems": problems, "body_chars": body_chars, "kept_chars": kept_chars,
            "orphans": orphans,
            "inferred": [s["n"] for s in sections if s["inferred"]],
            "notes": sum(len(p["notes"]) for p in pages)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.write or a.dry_run):
        ap.error("要 --dry-run 或 --write")

    built = {slug: build(slug, cfg) for slug, cfg in DOCS.items()}

    blocking = []
    for slug, b in built.items():
        cfg = DOCS[slug]
        want = cfg["last_section"] - cfg["first_section"] + 1 + (1 if b["prologue"] else 0)
        print(f"\n════ {slug}　{cfg['title']}")
        print(f"  頁　　{len(b['pages'])} 頁　印刷頁 "
              f"{b['pages'][0]['printed']}–{b['pages'][-1]['printed']}"
              f"（推出來的 {sum(1 for p in b['pages'] if p.get('printed_inferred'))} 頁）")
        print(f"  節　　{len(b['rows'])} 節 / 應有 {want}　"
              f"補號 {b['inferred'] or '無'}")
        print(f"  註腳　{b['notes']} 條　序言 {'有' if b['prologue'] else '無'}"
              f"　版權尾 {b['credits'] or '無'}")
        print(f"  字　　正文 {b['body_chars']} → 入庫 {b['kept_chars']}"
              f"（差 {b['body_chars'] - b['kept_chars']}：節號與段落接合符，"
              f"不是內容）")
        print(f"  點名　沒被收進任何一處的段落 {len(b['orphans'])} 段")
        if b["problems"]:
            for p in b["problems"]:
                print(f"  🚨 {p}")
            blocking += b["problems"]
        else:
            print("  ✓ 閘全過")

    if blocking:
        print(f"\n⛔ {len(blocking)} 項未過，不寫入。")
        return 1
    if a.dry_run:
        print("\n（dry-run：沒有寫入）")
        return 0

    e = env()
    url, h = api(e)
    for slug, b in built.items():
        r = requests.post(f"{url}/rest/v1/apocrypha_sections", headers=h,
                          data=json.dumps(b["rows"], ensure_ascii=False).encode("utf-8"),
                          timeout=120)
        if r.status_code >= 400:
            print(f"⛔ 寫 sections 失敗 {slug}：{r.status_code} {r.text[:300]}")
            return 1
        intro = "\n\n".join(b["intro"] + b["credits"])
        r = requests.patch(f"{url}/rest/v1/apocrypha_documents", headers=h,
                           params={"slug": f"eq.{slug}"},
                           data=json.dumps({"intro_zh": intro}, ensure_ascii=False).encode("utf-8"),
                           timeout=60)
        if r.status_code >= 400:
            print(f"⛔ 寫 intro 失敗 {slug}：{r.status_code} {r.text[:300]}")
            return 1
        print(f"✓ {slug}：{len(b['rows'])} 節、簡介 {len(intro)} 字已寫入")
    return 0


if __name__ == "__main__":
    sys.exit(main())
