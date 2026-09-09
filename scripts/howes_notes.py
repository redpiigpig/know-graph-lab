# -*- coding: utf-8 -*-
"""豪斯《日本的現代先知》的**尾註、縮寫表、參考書目**抽取。

為什麼補這一支：初版轉錄只做正文，把 Notes／Bibliography 當「檢索裝置不是散文」
跳過。使用者 2026-09-09 推翻——「不然我怎麼確認他引用的史料？」正文引了一句話卻
查不到出處，對研究用途等於半成品。見 [[feedback_transcribe_notes_and_bibliography]]。

三塊（1-based PDF 頁碼）：
  * p428      Attribution Abbreviations —— **解讀註釋的鑰匙**。SK＝《聖書之研究》、
              MKK＝《無教會》、JCI＝Japan Christian Intelligencer、ZenshûA＝岩波
              1932–33 二十卷本、ZenshûB＝岩波 1981–84 四十卷本。缺這張表，
              「SK 335 (June 1928), 242; ZenshûA 13, 891」這種字串無法解讀。
  * p429–451  逐章尾註（序言＋導論＋16 章＋結論）
  * p452–457  Selected Bibliography

🚨 **不能靠內文的數字流切註號。**第一版這樣寫，結果第八章只抓到 29 條（實際 74
條）——因為註 30 與註 70 的號碼落在**頁首**，被書眉清理連帶吃掉，序號一斷後面
全部黏成一條。而且第十六章整章漏掉（章名 `Chapter 16: What Is Mukyôkai?` 有
`ô` 與 `?`，不在我當初的字元類裡）。

**改用版面幾何**，跟正文同一個教訓（見 howes_uchimura_biography.md）：

| 訊號 | 值 | 判準 |
|---|---|---|
| 章名 | font `StoneSans-Bold` | 新章開始 |
| 註號 | x0 ≈ 22（偶爾 26，號碼與註文黏在一起） | 新註開始 |
| 註文 | x0 ≈ 36.7，`StoneSerif` 7.5 | 註文與續行 |
| 書眉頁碼 | 字級 8.0，x0 ≈ 14.7（偶頁）或 ≈ 357（奇頁） | 丟 |

註號與註文**共用同一個 y**（懸掛縮排），所以先按 y 併成視覺行，號碼自然成為行首。

純函式鎖在 scripts/tests/test_howes_notes.py。

  python -X utf8 scripts/howes_notes.py --stats
  python -X utf8 scripts/howes_notes.py --note 8 59
  python -X utf8 scripts/howes_notes.py --json c:/tmp/howes_notes.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PDF_PATH = Path("c:/tmp/uchimura_cache/howes_japans_modern_prophet.pdf")

ABBREV_PAGES = (428, 429)      # 縮寫表跨到 429 上半（429 下半才開始尾註）
NOTES_PAGES = (429, 451)
BIBLIO_PAGES = (452, 457)

HEAD_FONT = "StoneSans-Bold"   # 章名唯一可靠的判準
NUM_X_MAX = 30.0               # 行首 x0 小於此＝註號欄
RUNNING_SIZE = 8.0             # 書眉頁碼字級（註文一律 7.5）
SAME_LINE_TOL = 2.5


def merged_lines(page_dict: dict) -> list[dict]:
    """一頁 → [{x0, size, font, text}]，按 y 把懸掛縮排的號碼與註文併成一行。"""
    frags = []
    for b in page_dict.get("blocks", []):
        for l in b.get("lines", []):
            sp = [s for s in l.get("spans", []) if s.get("text", "").strip()]
            if not sp:
                continue
            frags.append({"y": round(l["bbox"][1], 1), "x0": l["bbox"][0],
                          "size": sp[0]["size"], "font": sp[0]["font"],
                          "text": "".join(s["text"] for s in sp)})
    frags.sort(key=lambda f: (f["y"], f["x0"]))
    out: list[dict] = []
    for f in frags:
        if out and abs(f["y"] - out[-1]["y"]) <= SAME_LINE_TOL:
            out[-1]["text"] += f["text"]
        else:
            out.append(dict(f))
    return out


def is_running_head(ln: dict) -> bool:
    return ln["size"] >= RUNNING_SIZE - 0.1 and re.fullmatch(r"\d{3}", ln["text"].strip() or "x") is not None


_LEAD_NUM = re.compile(r"^(\d{1,3})\s*(?=[“\"'A-Za-z(])")


def parse_pages(pages: list[list[dict]]) -> list[dict]:
    """尾註各頁的 merged_lines → [{chapter, notes:[{n,text}]}]。"""
    chapters: list[dict] = []
    cur: dict | None = None
    for lines in pages:
        for ln in lines:
            t = ln["text"].strip()
            if not t or is_running_head(ln):
                continue
            if ln["font"] == HEAD_FONT:
                cur = {"chapter": t, "notes": []}
                chapters.append(cur)
                continue
            if cur is None:
                continue
            m = _LEAD_NUM.match(t)
            if m and ln["x0"] < NUM_X_MAX:
                cur["notes"].append({"n": int(m.group(1)), "text": t[m.end():].strip()})
            elif cur["notes"]:
                cur["notes"][-1]["text"] += " " + t
    for c in chapters:
        for nt in c["notes"]:
            nt["text"] = re.sub(r"\s+", " ", nt["text"]).strip()
    return chapters


def flat_text(pages: list[list[dict]]) -> str:
    """縮寫表／書目：不必分條，去書眉後整段串起來。"""
    parts = []
    for lines in pages:
        for ln in lines:
            if ln["text"].strip() and not is_running_head(ln):
                parts.append(ln["text"].strip())
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def load(pdf: Path = PDF_PATH) -> dict:
    import fitz
    doc = fitz.open(pdf)

    def pg(a: int, b: int) -> list[list[dict]]:
        return [merged_lines(doc[p].get_text("dict")) for p in range(a - 1, b)]

    abbrev = flat_text(pg(*ABBREV_PAGES))
    # 縮寫表那兩頁的尾巴已經是尾註開頭，切在第一個章名處
    cut = abbrev.find("Preface and Acknowledgments")
    if cut > 0:
        abbrev = abbrev[:cut].strip()
    chapters = parse_pages(pg(*NOTES_PAGES))
    biblio = flat_text(pg(*BIBLIO_PAGES))
    doc.close()
    return {"abbreviations": abbrev, "chapters": chapters, "bibliography": biblio}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--note", nargs=2, metavar=("CHAPTER", "N"))
    ap.add_argument("--json")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    data = load()

    if args.note:
        want, n = args.note[0], int(args.note[1])
        for c in data["chapters"]:
            if c["chapter"].startswith(f"Chapter {want}:") or want.lower() in c["chapter"].lower():
                for nt in c["notes"]:
                    if nt["n"] == n:
                        print(f"[{c['chapter']}] 註 {n}\n{nt['text']}")
                        return
        print("找不到")
        return
    if args.json:
        Path(args.json).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("已寫", args.json)
        return
    if args.dump:
        print("=== Attribution Abbreviations ===\n" + data["abbreviations"])
        for c in data["chapters"]:
            print(f"\n=== {c['chapter']} ===")
            for nt in c["notes"]:
                print(f"{nt['n']}. {nt['text']}")
        print("\n=== Selected Bibliography ===\n" + data["bibliography"])
        return

    print(f"縮寫表 {len(data['abbreviations']):,} 字元")
    print(f"參考書目 {len(data['bibliography']):,} 字元")
    tot = 0
    bad = []
    for c in data["chapters"]:
        ns = [nt["n"] for nt in c["notes"]]
        tot += len(ns)
        gap = "" if ns == list(range(1, len(ns) + 1)) else "  ⚠️ 序號不連續"
        if gap:
            bad.append(c["chapter"])
        print(f"  {c['chapter'][:46]:48s} {len(ns):3d} 註{gap}")
    print(f"合計 {len(data['chapters'])} 區塊 / {tot} 條註")
    if bad:
        print("序號不連續：", "；".join(bad))


if __name__ == "__main__":
    main()
