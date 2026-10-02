#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從《神的歷史》《神的演化》《造神》抽出被引用的書 → output/god_books/raw.json

  造神：書末參考書目（Chicago 體，規則解析，不用 LLM）
  神的歷史：館內英文版 PDF 的尾註（LLM 抽書）
  神的演化：館內中譯本只有正文（註釋與書目頁掃描本沒有），從正文提到的書抽（LLM）

用法：python -X utf8 scripts/god_books_extract.py [aslan|armstrong|wright]
"""
import json, re, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "output" / "god_books"; OUT.mkdir(parents=True, exist_ok=True)
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
ASLAN = "e0965e49-95aa-41f0-b485-78fdc7872339"
WRIGHT = "8a4dd337-4291-4623-8a5b-dcdaca60831f"
ARM_PDF = (r"G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館\神學\Karen Armstrong，A History of God "
           r"The 4,000-Year Quest of Judaism, Christianity and Islam.pdf")


def chunks(bid):
    return [json.loads(l) for l in (CH / f"{bid}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def aslan():
    txt = "\n".join(c["content"] for c in chunks(ASLAN)[27:40])
    start = txt.index("Banning, E. B.")
    end = txt.index("前言：按照我們的形象造神", start)
    out, prev = [], ""
    for line in txt[start:end].split("\n"):
        line = re.sub(r"^\{\{s:[\d-]+\}\}", "", line).strip().replace("\u00ad", "")
        if not line:
            continue
        if line.startswith("──"):
            au, rest = prev, line.lstrip("─").lstrip(". ").strip()
        else:
            m = None
            for mm in re.finditer(r"\.\s+", line):
                pre = line[:mm.start()]
                last = re.split(r"[\s,]+", pre)[-1]
                nxt = line[mm.end():].split(" ")[0]
                if last in ("Jr", "Sr"):
                    continue
                if len(last) == 1 and last.isupper() and (re.fullmatch(r"[A-Z]\.?", nxt) or nxt.endswith(",")):
                    continue
                m = (pre, line[mm.end():]); break
            if not m:
                continue
            au, rest = m
            prev = au
        if rest.startswith(("“", '"')) or re.match(r"Pages?\s", rest):
            continue  # 期刊論文與書中一章
        segs = [x for x in re.split(r"(?<=[.?!])\s+(?=[A-Z0-9])", rest) if x]
        yrs = re.findall(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)", segs[-1]) if segs else []
        if not segs or not yrs or segs[0].startswith(("Translated", "Edited")):
            if "“" in line:
                continue  # 期刊論文
            out.append({"author": au, "title": rest[:140], "year": None, "flag": "unparsed", "raw": line})
            continue
        out.append({"author": au, "title": segs[0].rstrip(".").strip(), "year": yrs[0], "raw": line})
    for o in out:
        o["from"] = "造神"
    return out


PROMPT_ARM = """以下是 Karen Armstrong《A History of God》的英文尾註片段。請抽出被引用的「書」（專書、論文集、經典的現代版本與譯本都算），
略過：聖經與古蘭經章節、期刊論文、純 Ibid.、頁碼。古典作品（如 Augustine 的 City of God）若註中標明現代版本才收，否則略過。
回傳 JSON 陣列，每筆 {"author":"姓名(全名優先)","title":"書名","year":"出版年或null"}；同一本只列一次。

{text}"""

PROMPT_WRIGHT = """以下是羅伯‧賴特《神的演化》繁中譯本正文片段。請抽出作者在文中提到、引用或推薦的「書」（專書；含學術著作與通俗著作），
略過：聖經與古蘭經各卷、期刊論文、只提人名沒提書名的、經典古籍（柏拉圖、奧古斯丁等古人的原典，除非是現代學者的著作）。
回傳 JSON 陣列，每筆 {"author":"作者原文姓名（拉丁字母，不確定就寫中文）","title":"書的英文原名，不確定就寫中文書名","zh":"中文書名或null","year":"出版年或null"}。
若書名是你根據作者與主題確定的英文原名才寫英文，不要編造。

{text}"""


def run_llm(prompt_tpl, pieces, tag):
    from chapters_via_llm_toc import ask_model
    res = []
    cache = OUT / f"{tag}_llm.json"
    done = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    for i, p in enumerate(pieces):
        if str(i) in done:
            res += done[str(i)]; continue
        raw, eng = ask_model(prompt_tpl.replace("{text}", p))
        try:
            a = json.loads(re.search(r"\[.*\]", raw, re.S).group(0))
        except Exception:
            print(f"  {tag} 片段 {i} 解析失敗 ({eng}) {raw[:80]!r}", flush=True)
            continue
        a = [x for x in a if isinstance(x, dict) and x.get("title")]
        done[str(i)] = a; res += a
        cache.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
        print(f"  {tag} {i+1}/{len(pieces)} +{len(a)} ({eng})", flush=True)
    return res


def split(text, n):
    parts, cur = [], ""
    for para in text.split("\n"):
        if len(cur) + len(para) > n:
            parts.append(cur); cur = ""
        cur += para + "\n"
    return parts + [cur]


def armstrong():
    import fitz
    d = fitz.open(ARM_PDF)
    text = "\n".join(d[i].get_text() for i in range(199, 219))
    rows = run_llm(PROMPT_ARM, split(text, 5000), "armstrong")
    for r in rows:
        r["from"] = "神的歷史"
    return rows


def wright():
    text = "\n".join(re.sub(r"\{\{s:[\d-]+\}\}", "", c["content"]) for c in chunks(WRIGHT))
    rows = run_llm(PROMPT_WRIGHT, split(text, 9000), "wright")
    for r in rows:
        r["from"] = "神的演化"
    return rows


if __name__ == "__main__":
    which = sys.argv[1:] or ["aslan", "armstrong", "wright"]
    for w in which:
        rows = globals()[w]()
        (OUT / f"{w}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, len(rows), flush=True)
