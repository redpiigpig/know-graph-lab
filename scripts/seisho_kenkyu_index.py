# -*- coding: utf-8 -*-
"""從《內村鑑三全集》（岩波 1932–33）重建《聖書之研究》357 號的書目。

想法：原刊 357 號沒有可取得的整套掃描，但全集每一卷末都附「第N卷內容年譜」，
逐篇記著「篇名＋聖書之研究第N號＋年月」。把 20 卷的年譜抽出來合併，就得到
一份「號 → 該號收在全集裡的篇目」的對照表，等於把刊物從全集反推回來。

兩個資料源都吃：
  --source archive   用 archive.org 的 djvu 文字層（粗 OCR，先看覆蓋率用）
  --source mineru    用本機 MinerU 轉出的 JSONL（正式版）

🚨 號數是漢數字又被 OCR 咬過（「第三 四ニ號」＝342、ニ 是片假名）。所以號數與年月
   互相校驗：本誌 1900 年 9 月創刊、按月發行，號數與年月是一條直線，對不上的標出來
   而不是默默採信。

    python scripts/seisho_kenkyu_index.py --source archive
    python scripts/seisho_kenkyu_index.py --source archive --report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = Path(__file__).resolve().parent.parent
CACHE = Path("c:/tmp/uchimura_zenshu_txt")
OUT = REPO / "output" / "seisho-kenkyu-index.jsonl"

FIRST_YEAR, FIRST_MONTH = 1900, 9          # 創刊：明治 33 年 9 月＝第 1 號

_K = {"〇": 0, "○": 0, "一": 1, "二": 2, "三": 3, "四": 4,
      "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def kanji_num(s: str) -> int | None:
    """「三四ニ」→342、「三十六」→36。OCR 會把二寫成片假名 ニ、一寫成 ー。"""
    s = s.replace("ニ", "二").replace("ー", "一").replace("Ｏ", "〇").replace("O", "〇")
    s = re.sub(r"[^〇○一二三四五六七八九十]", "", s)
    if not s:
        return None
    if "十" in s:                      # 位值寫法：三十六
        tot = cur = 0
        for ch in s:
            if ch == "十":
                tot += (cur or 1) * 10
                cur = 0
            else:
                cur = _K.get(ch, 0)
        return tot + cur
    v = 0                              # 逐字寫法：三四二
    for ch in s:
        v = v * 10 + _K.get(ch, 0)
    return v


def issue_of(year: int, month: int) -> int:
    return (year - FIRST_YEAR) * 12 + (month - FIRST_MONTH) + 1


# 「聖書之研究」被 OCR 咬成 聖甞之研究／^書之W究…；只鎖「之」＋「研究/硏究/W究」＋號
# 群組1＝篇名（誌名之前那一段），群組2＝號數。篇名不能吃進 match 本體，
# 否則 line[:m.start()] 永遠是空的——第一版就是這樣抽出 1327 筆全無標題。
MARK = re.compile(r"([^\n]{0,44}?)[聖胃甞書曹^\s]{0,3}[之乊]\s*[研硏]?\s*[究W]\s*[究]?\s*[第笫]?\s*"
                  r"([〇○一二三四五六七八九十ニーＯO\s]{1,9})\s*號")
YEAR = re.compile(r"[（(]\s*([〇○一二三四五六七八九\s]{4,6})\s*年\s*[)）]")
MONTH = re.compile(r"([〇○一二三四五六七八九十ニー]{1,3})\s*月")


def parse_text(text: str, vol: int) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if "號" not in line:
            continue
        m = MARK.search(line)
        if not m:
            continue
        issue = kanji_num(m.group(2))
        if not issue or not (1 <= issue <= 400):
            continue
        title = re.sub(r"\s+", "", m.group(1))
        title = re.sub(r"[聖胃甞書曹之\^\d]+$", "", title)[-40:]
        tail = line[m.end():]
        y = YEAR.search(tail) or YEAR.search(line)
        mo = MONTH.search(tail)
        year = kanji_num(y.group(1)) if y else None
        month = kanji_num(mo.group(1)) if mo else None
        rec = {"vol": vol, "issue": issue, "title": title,
               "year": year if year and 1900 <= year <= 1930 else None,
               "month": month if month and 1 <= month <= 12 else None}
        if rec["year"] and rec["month"]:
            rec["issue_from_date"] = issue_of(rec["year"], rec["month"])
            rec["consistent"] = abs(rec["issue_from_date"] - issue) <= 1
        rows.append(rec)
    return rows


def load_archive(vol: int) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"vol{vol:02d}.txt"
    if f.exists():
        return f.read_text(encoding="utf-8", errors="replace")
    ident = f"uchimurakanzzens{vol:02d}uchiuoft"
    url = f"https://archive.org/download/{ident}/{ident}_djvu.txt"
    last = ""
    for attempt in range(1, 5):          # archive.org 會中途斷線（IncompleteRead）
        try:
            raw = urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "kgl-research/1.0"}), timeout=300).read()
            t = raw.decode("utf-8", "replace")
            f.write_text(t, encoding="utf-8")   # 只有讀完整才寫快取
            return t
        except Exception as e:
            last = str(e)[:80]
            time.sleep(8 * attempt)
    print(f"  卷{vol:02d} 取檔失敗（{last}）", flush=True)
    return ""


def load_mineru(vol: int) -> str:
    import os
    from dotenv import load_dotenv
    load_dotenv(REPO / ".env")
    p = Path(os.environ["EBOOK_CHUNKS_DIR"]) / f"d0000001-0000-4000-8000-{vol:012d}.jsonl"
    if not p.exists():
        return ""
    return "\n".join(json.loads(l).get("content", "") for l in p.open(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["archive", "mineru"], default="archive")
    ap.add_argument("--report", action="store_true", help="只印覆蓋率，不寫檔")
    args = ap.parse_args()

    load = load_archive if args.source == "archive" else load_mineru
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        for vol, text in zip(range(1, 21), ex.map(load, range(1, 21))):
            got = parse_text(text, vol) if text else []
            rows += got
            print(f"  卷{vol:02d} 抽出 {len(got):4} 筆" + ("" if text else "（沒有文字可讀）"), flush=True)

    issues = sorted({r["issue"] for r in rows})
    ok = [r for r in rows if r.get("consistent")]
    bad = [r for r in rows if r.get("consistent") is False]
    missing = [n for n in range(1, 358) if n not in set(issues)]
    print()
    print(f"總筆數 {len(rows)}｜相異號 {len(issues)}／357｜有年月且對得上 {len(ok)}｜號與年月打架 {len(bad)}")
    print(f"沒出現過的號 {len(missing)} 個" + (f"：{missing[:25]}…" if missing else ""))
    if not args.report:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", encoding="utf-8") as fh:
            for r in sorted(rows, key=lambda x: (x["issue"], x["vol"])):
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"→ {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
