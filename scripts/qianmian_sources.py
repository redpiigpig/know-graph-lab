# -*- coding: utf-8 -*-
"""千面上帝：把三份素材彙整成逐章的來源包。

素材：
  1. stores/千面上帝/千面上帝：目錄.docx    七卷 28 章的章節綱要
  2. stores/千面上帝/千面上帝：書摘.xlsx    28 個分頁、1,960 條書摘（帶出處）
  3. Supabase video_transcripts             宗教史讀書會逐字稿 25 集

🚨 三者的「第 N 章」不是同一套編號。書摘分頁與讀書會集數沿用舊章序，目錄是後來
   重排過的定稿。全部以「目錄」為準，靠底下 SHEET_MAP / 標題比對做對應，
   絕不用序號當鍵（見 [[feedback_reader_silent_failures]]）。

輸出：output/qianmian/sources/ch01.json … ch28.json（中繼檔，不進版控）
"""
import json
import re
import sys
import zipfile
from html import unescape
from pathlib import Path

import openpyxl
import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "stores" / "千面上帝"
OUT = ROOT / "output" / "qianmian" / "sources"

# 書摘分頁 → 目錄章序。沒列到的分頁按標題自動比對。
SHEET_MAP = {
    "十一、經書的子民": 9,        # 被擄後猶太教＝第九章的「上帝的究極進化」「尼希米圍牆」
    "十二、宇宙城邦的公民": 11,
    "二十一、唯獨信心的信仰": 21,  # 即目錄的「良心的改革」
    "六、立約與征服的血祭": 6,
    "七、王國與聖殿的詩篇": 7,
}


def read_outline():
    """目錄 docx → [{no, volume, title, span, period, sections}]"""
    xml = zipfile.ZipFile(STORE / "千面上帝：目錄.docx").read("word/document.xml").decode("utf-8")
    lines = [unescape(re.sub(r"<[^>]+>", "", p)).strip()
             for p in re.sub(r"</w:p>", "\x00", xml).split("\x00")]
    lines = [l for l in lines if l and l != "千面上帝"]

    chapters, volume = [], ""
    for line in lines:
        if re.match(r"^第[一二三四五六七八九十]+卷：", line):
            volume = line
        elif "：從" in line:
            head, _, tail = line.partition("：從")
            span, _, period = tail.rpartition("(")
            chapters.append({
                "no": len(chapters) + 1,
                "volume": volume,
                "title": head.strip(),
                "span": "從" + span.strip(),
                "period": period.rstrip(")").strip(),
                "sections": [],
            })
        elif chapters:
            chapters[-1]["sections"].append(line.rstrip("。"))
    return chapters


def read_excerpts():
    """書摘 xlsx → {分頁名: [{topic, text, source}]}"""
    wb = openpyxl.load_workbook(STORE / "千面上帝：書摘.xlsx", read_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = []
        for row in ws.iter_rows(values_only=True):
            cells = [(str(c).strip() if c is not None else "") for c in row]
            cells += [""] * (3 - len(cells))
            topic, text, source = cells[0], cells[1], cells[2]
            if not text or len(text) < 20:
                continue
            rows.append({"topic": topic.replace("\n", ""), "text": text, "source": source})
        out[ws.title.strip()] = rows
    return out


def read_transcripts():
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"')
    key = env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.get(
        f"{env['SUPABASE_URL']}/rest/v1/video_transcripts",
        params={"project_slug": "eq.million-masks",
                "select": "episode,title,video_date,content", "order": "episode"},
        headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=60)
    r.raise_for_status()
    return r.json()


def norm(s):
    """標題正規化：去掉序號、標點、上中下終，只留書名本身。"""
    s = re.sub(r"^[一二三四五六七八九十百]+、", "", s)
    s = re.sub(r"^第[一二三四五六七八九十百]+章[、.．]?", "", s)
    s = re.sub(r"[（(【].*?[)）】]", "", s)          # (上)(下)(中)(終)
    s = re.sub(r"[-－]\s*\d+$", "", s)                # 同一場分段的 -1 -2 -3
    s = re.sub(r"[\s、。．.，,：:（）()《》\-]", "", s).strip()
    return re.sub(r"[上中下終]$", "", s)               # 沒加括號的「軸心的時代下」


def main():
    chapters = read_outline()
    assert len(chapters) == 28, f"目錄解析出 {len(chapters)} 章，應為 28"

    sheets = read_excerpts()
    by_norm = {norm(t): no for no, t in ((c["no"], c["title"]) for c in chapters)}

    # 書摘分頁 → 章
    assign, unmatched = {}, []
    for name, rows in sheets.items():
        no = SHEET_MAP.get(name) or by_norm.get(norm(name))
        if no is None:
            unmatched.append(name)
            continue
        assign.setdefault(no, []).extend(rows)

    # 逐字稿 → 章（用標題比對，不用集數）
    trans = {}
    for t in read_transcripts():
        no = by_norm.get(norm(t["title"]))
        if no is None:                      # 舊章序的「經書的子民」等
            key = norm(t["title"])
            for alias, target in {"經書的子民": 9, "種子與諸神的誕生": 2,
                                  "宇宙秩序下的永恆城邦": 3, "被拋入世界的萬物之靈": 1,
                                  "立約與征服的血祭": 6, "王國與聖殿的詩篇": 7}.items():
                if norm(alias) == key:
                    no = target
                    break
        if no is None:
            print(f"  ⚠ 逐字稿無法對應：ep{t['episode']} {t['title']}")
            continue
        trans.setdefault(no, []).append(t)

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"{'章':>3} {'書摘':>5} {'字數':>7} {'逐字稿':>6}  標題")
    for c in chapters:
        rows = assign.get(c["no"], [])
        eps = trans.get(c["no"], [])
        c["excerpts"] = rows
        c["transcripts"] = [{"episode": e["episode"], "title": e["title"],
                             "date": e["video_date"], "text": e["content"]} for e in eps]
        (OUT / f"ch{c['no']:02d}.json").write_text(
            json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        chars = sum(len(r["text"]) for r in rows)
        flag = "  ← 素材稀薄" if chars < 20000 else ""
        print(f"{c['no']:3d} {len(rows):5d} {chars:7d} {len(eps):6d}  {c['title']}{flag}")

    if unmatched:
        print("\n⚠ 未對應的書摘分頁：", unmatched)


if __name__ == "__main__":
    main()
