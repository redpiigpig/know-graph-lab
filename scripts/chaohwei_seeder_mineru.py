#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《人間佛教的播種者》MinerU 輸出 → scan_ocr 的逐頁 JSON（build 吃的格式）。

2026-10-01：前 87 頁先用 Gemini 跑（照 skill 舊寫法，被使用者糾正），其餘用本機
MinerU 補。兩個引擎在重疊的 75 頁逐頁比對（約 2.5 萬字）得出這支的修正表：

* 字形：MinerU 照原書字形吐（爲眞衆啓虚内），Gemini 會正規化 → 統一成 Gemini 那邊，
  不然同一本書前後兩種寫法；
* 簡體外洩：说缘给来结稣锲别黄毁丢——MinerU 在這份低解析掃描上會漏出簡體字形；
* 真誤讀：師→帥 11 次（本書無「帥」字的正當用法，全換）；天/大、會/曾/僧 這類
  **兩邊都是字、判不了**的不動，列在 --report 裡交人看。
* 註號：MinerU 把 ❶ 有時讀成 ②、有時整個丟掉；丟掉的那種註文掛 `[^?]`，不猜號碼。

  python -X utf8 scripts/chaohwei_seeder_mineru.py --pages 88-133
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SRC = Path("c:/tmp/chaohwei_seeder/mineru.jsonl")
OUT = Path("c:/tmp/chaohwei_seeder/ocr_mineru")
RULE = "———————————————"

CHAR_MAP = str.maketrans({
    # 字形統一（對齊 Gemini 那 87 頁）
    "爲": "為", "眞": "真", "衆": "眾", "啓": "啟", "虚": "虛", "内": "內", "参": "參",
    "浄": "淨", "刹": "剎", "麽": "麼", "挿": "插", "敎": "教",
    # 簡體外洩
    "说": "說", "説": "說", "缘": "緣", "给": "給", "来": "來", "结": "結", "稣": "穌",
    "锲": "鍥", "别": "別", "黄": "黃", "毁": "毀", "丢": "丟",
    # 誤讀
    "帥": "師",
    "<": "〈", ">": "〉",
})
_CIRCLED = {c: i + 1 for i, c in enumerate("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳")}
_CIRCLED.update({c: i + 1 for i, c in enumerate("❶❷❸❹❺❻❼❽❾❿")})
_CIRC_RE = re.compile("[" + "".join(_CIRCLED) + "]")
# 偶數頁頁腳；書名 OCR 常讀歪（人間佛致／佛数的播種者），中間那個字放寬
_FOOT_L = re.compile(r"^(\d{1,3})\s*[·‧.．]\s*人間佛.的播種者$")
_RUNNING = re.compile(r"^(?:人間佛.的播種者|[一二三四五六七八九十]{1,3}\s*[·‧]\s*\S{2,15})$")  # 書眉漏進正文
_FOOT_R = re.compile(r"^(.{2,30}?)\s*[·‧.．]\s*(\d{1,3})$")             # 奇數頁：章名·頁碼


def merge_split_blocks(blocks: list[str]) -> list[str]:
    """MinerU 會把一段從行中間切成兩塊（留下「的探究上。」這種碎段）。純函式。

    判準看**印刷行寬**：新段第一行縮排兩格，所以前一塊的最後一行若印滿整行
    （≥ 本頁常見行寬 −1），下一塊就是同一段的續行，接回去。
    """
    widths = [len(ln) for b in blocks for ln in b.split("\n") if ln.strip()]
    if not widths:
        return blocks
    full = max(set(widths), key=widths.count)      # 本頁最常見的行寬＝滿行
    out: list[str] = []
    for b in blocks:
        if out and len(out[-1].split("\n")[-1]) >= full - 1 and full >= 15:
            out[-1] += "\n" + b
        else:
            out.append(b)
    return out


def page_to_record(c: dict) -> dict:
    """一頁 MinerU chunk → {printed, header, text}。純函式。"""
    printed = str(c["printed_page"]) if c.get("printed_page") else ""
    header = ""
    # 偶數頁的頁腳（「80·人間佛教的播種者」）沒被歸到 page_number：可能在 headers 欄，
    # 也可能是整頁**最後一行**——有註腳時就落在註腳區底下，只看正文區會漏掉
    lines = c["content"].rstrip().split("\n")
    last = lines[-1].strip() if lines else ""
    for cand in [*(c.get("headers") or []), last]:
        m = next((mm for rx in (_FOOT_L, _FOOT_R) if (mm := rx.match(cand.strip()))), None)
        if m:
            printed = printed or m.group(m.lastindex)
            header = m.group(1) if m.re is _FOOT_R else "人間佛教的播種者"
            if cand == last:
                lines.pop()
            break
    header = header or next((h for h in c.get("headers") or [] if not re.search(r"\d", h)), "")
    body, _, notes = "\n".join(lines).partition(RULE)
    blocks = merge_split_blocks([b.strip() for b in body.split("\n\n") if b.strip()])
    # 註文會折行：不以圈號開頭、而且上一行沒有句號收尾的，是上一條的續行
    note_lines: list[str] = []
    for n in (x.strip() for x in notes.strip().split("\n") if x.strip()):
        if note_lines and not _CIRC_RE.match(n) and not note_lines[-1].endswith(("。", "）", ")")):
            note_lines[-1] += n
        else:
            note_lines.append(n)
    refs: list[int] = []

    def ref(m: re.Match) -> str:
        refs.append(_CIRCLED[m.group(0)])
        return f"[^{_CIRCLED[m.group(0)]}]"

    paras = [_CIRC_RE.sub(ref, b.replace("\n", "")).translate(CHAR_MAP) for b in blocks]
    # 書眉（書名、章名）漏進正文：章首頁第一行的章名留著（build 會換成 ## 標題），其餘丟掉
    paras = [p for i, p in enumerate(paras) if not (_RUNNING.match(p.strip()) and i > 0)
             and not re.fullmatch(r"人間佛.的播種者", p.strip())]
    out_notes = []
    for i, n in enumerate(note_lines):
        n = n.translate(CHAR_MAP)
        m = _CIRC_RE.match(n)
        num = refs[i] if i < len(refs) else (_CIRCLED[m.group(0)] if m else "?")
        out_notes.append(f"[^{num}]: {_CIRC_RE.sub('', n, count=1).strip()}")
    return {"printed": printed, "header": header, "text": "\n".join(paras + out_notes)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", required=True, help="掃描頁區間（全書工作檔的頁次），例 88-133")
    ap.add_argument("--src", default=str(SRC), help="MinerU jsonl")
    ap.add_argument("--offset", type=int, default=0,
                    help="src 第 1 頁對應全書工作檔第幾頁之前（後半另掃一檔時用：work_b 第 1 頁＝工作檔 134 → 133）")
    a = ap.parse_args()
    lo, hi = map(int, a.pages.split("-"))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = {c["page_number"] + a.offset: c
            for c in map(json.loads, Path(a.src).read_text(encoding="utf-8").splitlines())}
    unknown = maybe = 0
    for wp in range(lo, hi + 1):
        rec = page_to_record(rows[wp])
        unknown += rec["text"].count("[^?]")
        maybe += len(re.findall(r"[天大曾僧]", rec["text"]))
        (OUT / f"{wp:03d}.json").write_text(json.dumps(
            {"work_page": wp, "format": "v2", **rec, "engine": "mineru"},
            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"寫出 {hi - lo + 1} 頁 → {OUT}；註號讀不到 {unknown} 條")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
