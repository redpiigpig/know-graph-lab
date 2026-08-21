#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替 ACCS 多書卷合刊定出各書的 PDF 實體頁界，補進 accs_volume_config.json。

為什麼要這支：8 卷合刊（王代拉尼斯／十二先知書／林前後…）在 config 裡是
`needs_boundaries`，`accs_ocr_run.py` 一律跳過，所以那 21 個書卷永遠排不到。合刊 PDF
是純掃描（無文字層、無書籤），目錄只能用 vision 讀。

做法（每卷）：
  1. 掃前 30 頁找「目錄」，Gemini 讀出「書名 → 書內頁碼」。
  2. 取三頁正文讀「印在紙上的頁碼」反推 offset（PDF 張數 = 書內頁碼 + offset），
     三點取多數決，再拿目錄第一本的標題頁回驗一次。
  3. 輸出 ranges；`--write` 才寫回 config（預設只印提案）。

驗證是重點：offset 猜錯會讓整卷 OCR 灌到錯的 book_code，比不做還糟。所以回驗不過就不寫。
成本也是重點：整卷約 4-5 次 vision 呼叫。**別用暴力搜 offset**（offset範圍 x 書數，最壞
243 次）——Gemini 免費層一天總共才約 840 次，還要分給 ACCS 正線。

  python scripts/accs_find_boundaries.py --vol 46-47
  python scripts/accs_find_boundaries.py --all
  python scripts/accs_find_boundaries.py --vol 46-47 --write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import fitz  # noqa: E402
from google.genai import types  # noqa: E402

import ingest_accs_genesis as ing  # noqa: E402  (.env / API_KEYS / MODEL_CHAIN / _client)

CFG = ROOT / "accs_volume_config.json"
CACHE = Path("c:/tmp/accs_boundaries")

# 書名（繁中，含常見異寫）→ book_code。合刊封面/目錄用的是全名或簡稱。
NAME_TO_CODE = {
    "列王紀上": "1ki", "列王紀下": "2ki", "歷代志上": "1ch", "歷代志下": "2ch",
    "以斯拉記": "ezr", "尼希米記": "neh", "以斯帖記": "est",
    "箴言": "pro", "傳道書": "ecc", "雅歌": "sng",
    "以西結書": "ezk", "但以理書": "dan",
    "何西阿書": "hos", "約珥書": "jol", "阿摩司書": "amo", "俄巴底亞書": "oba",
    "約拿書": "jon", "彌迦書": "mic", "那鴻書": "nam", "哈巴谷書": "hab",
    "西番雅書": "zep", "哈該書": "hag", "撒迦利亞書": "zec", "瑪拉基書": "mal",
    "哥林多前書": "1co", "哥林多後書": "2co",
    "加拉太書": "gal", "以弗所書": "eph", "腓立比書": "php",
    "歌羅西書": "col", "帖撒羅尼迦前書": "1th", "帖撒羅尼迦後書": "2th",
    "提摩太前書": "1ti", "提摩太後書": "2ti", "提多書": "tit", "腓利門書": "phm",
    "雅各書": "jas", "彼得前書": "1pe", "彼得後書": "2pe",
    "約翰一書": "1jn", "約翰二書": "2jn", "約翰三書": "3jn", "猶大書": "jud",
}

TOC_PROMPT = """這是一本《古代基督信仰聖經註釋叢書》合刊的前頁掃描影像（數頁）。
請找出**目錄／目次**那一頁，讀出其中「聖經書卷名 → 該書起始頁碼」的對應。

只回傳 JSON 陣列，每元素 {"book": "書名", "page": 頁碼數字}。
- **聖經書卷**條目用繁體全名（如「列王紀上」「何西阿書」）。
- 另外，若目錄中有**正文之後的附錄類**條目（教父人物小傳／作者生平／主題索引／
  引用經文索引／參考書目），請把其中**最前面那一個**額外輸出成
  {"book": "__APPENDIX__", "page": 該條頁碼}。沒有就不輸出這一筆。
- 略過「序言」「導論」「縮寫表」這類正文之前的條目。
- 頁碼是印在書上的頁碼（阿拉伯數字），不是 PDF 張數。
- 找不到目錄就回傳 []。
- 不要 markdown 圍欄、不要說明文字。"""

TITLE_PROMPT = """這是《古代基督信仰聖經註釋叢書》中某一頁的掃描影像。
如果這頁是某卷聖經註釋的**標題頁／該書起始頁**（頁面上有明顯的書卷名作為大標題），
只回傳該書卷名的繁體全名（例如「列王紀上」）。
如果不是標題頁，只回傳「否」。不要其他文字。"""


def _gen(contents: list, schema: dict | None) -> str:
    """打一次 Gemini，沿用 ingest 的 key 池與模型鏈（含乾掉換模型的既有邏輯）。"""
    cfg_kw = {"temperature": 0.0}
    if schema:
        cfg_kw |= {"response_mime_type": "application/json", "response_schema": schema}
    last = None
    for model in ing.MODEL_CHAIN:
        for key in ing.API_KEYS:
            try:
                resp = ing._client(key).models.generate_content(
                    model=model, contents=contents,
                    config=types.GenerateContentConfig(**cfg_kw))
                txt = (resp.text or "").strip()
                if txt:
                    return txt
            except Exception as e:  # noqa: BLE001
                last = e
                continue
    raise RuntimeError(f"Gemini 全數失敗：{last}")


TOC_SCHEMA = {"type": "array", "items": {"type": "object", "properties": {
    "book": {"type": "string"}, "page": {"type": "integer"}}, "required": ["book", "page"]}}


def read_toc(doc: "fitz.Document", scan_pages: int = 30) -> list[dict]:
    parts = []
    for i in range(min(scan_pages, doc.page_count)):
        parts.append(types.Part.from_bytes(
            data=ing.render_page(doc, i), mime_type="image/png"))
    parts.append(types.Part.from_text(text=TOC_PROMPT))
    out = json.loads(_gen(parts, TOC_SCHEMA))
    return [e for e in out if isinstance(e, dict) and e.get("book") and e.get("page")]


def read_title(doc: "fitz.Document", pdf_page: int) -> str:
    if pdf_page < 1 or pdf_page > doc.page_count:
        return "否"
    parts = [types.Part.from_bytes(data=ing.render_page(doc, pdf_page - 1),
                                   mime_type="image/png"),
             types.Part.from_text(text=TITLE_PROMPT)]
    return _gen(parts, None).strip().strip("「」").splitlines()[0][:20]


PAGENO_PROMPT = """這是一本書的一頁掃描影像。請只回傳這一頁**印在頁面上的頁碼**（阿拉伯數字）。
頁碼通常在頁面最上緣或最下緣的角落。看不到頁碼就回傳「無」。不要其他文字。"""


def read_printed_pageno(doc: "fitz.Document", pdf_page: int) -> int | None:
    parts = [types.Part.from_bytes(data=ing.render_page(doc, pdf_page - 1),
                                   mime_type="image/png"),
             types.Part.from_text(text=PAGENO_PROMPT)]
    m = re.search(r"\d+", _gen(parts, None))
    return int(m.group()) if m else None


def solve_offset(doc: "fitz.Document", toc: list[dict]) -> int | None:
    """PDF 張數與書內頁碼的位移。

    直接讀某幾頁「印在紙上的頁碼」反推（offset = PDF張數 - 印刷頁碼），三個取樣點一致才採用，
    再拿目錄第一本的標題頁回驗一次。**不要暴力搜 offset**：那要 offset範圍 x 書數 次
    vision 呼叫（最壞 243 次），而 Gemini 免費層一天總共才約 840 次、還要分給 ACCS 正線。
    """
    n = doc.page_count
    samples = [int(n * f) for f in (0.25, 0.35, 0.5, 0.65, 0.8)]
    offs = []
    for pg in samples:
        printed = read_printed_pageno(doc, pg)
        if printed:
            offs.append(pg - printed)
            print(f"    取樣 PDF p{pg} → 印刷頁碼 {printed}（offset {pg - printed}）", flush=True)
    if not offs:
        return None
    off = max(set(offs), key=offs.count)
    if offs.count(off) < 2:
        print(f"    ✗ 取樣不一致 {offs}", flush=True)
        return None
    first = toc[0]
    got = read_title(doc, first["page"] + off)
    if first["book"] in got or got in first["book"]:
        return off
    print(f"    ✗ 標題頁回驗失敗：p{first['page'] + off} 讀到 {got!r}，"
          f"預期 {first['book']!r}", flush=True)
    return None


def build_ranges(doc: "fitz.Document", toc: list[dict], offset: int) -> list[dict]:
    # 附錄（人物小傳／索引）不是逐節註釋，OCR 出來幾乎都是 0 entries 卻照樣吃請求；
    # 最後一本若一路算到 PDF 末頁，等於白跑上百頁。有標到就切在附錄前一頁。
    appendix = next((e["page"] for e in toc if e["book"] == "__APPENDIX__"), None)
    rows = sorted([e for e in toc if e["book"] != "__APPENDIX__"], key=lambda e: e["page"])
    tail = (appendix + offset - 1) if appendix else doc.page_count
    out = []
    for i, e in enumerate(rows):
        code = NAME_TO_CODE.get(e["book"].strip())
        if not code:
            print(f"    ⚠ 不認得書名 {e['book']!r}，跳過", flush=True)
            continue
        start = e["page"] + offset
        end = (rows[i + 1]["page"] + offset - 1) if i + 1 < len(rows) else tail
        out.append({"book": code, "pages": f"{start}-{end}"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true", help="寫回 accs_volume_config.json")
    a = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    todo = [v for v in cfg if v["status"] == "needs_boundaries"
            and (a.all or v["vol_key"] == a.vol)]
    if not todo:
        ap.error("需 --vol <key> 或 --all；且該卷須為 needs_boundaries")

    CACHE.mkdir(parents=True, exist_ok=True)
    changed = False
    for v in todo:
        key = v["vol_key"]
        print(f"\n=== {key}  {Path(v['pdf']).name} ===", flush=True)
        cache_f = CACHE / f"{key}.json"
        if cache_f.exists():
            saved = json.loads(cache_f.read_text(encoding="utf-8"))
            toc, offset = saved["toc"], saved["offset"]
            print(f"  [cache] 目錄 {len(toc)} 條, offset={offset}", flush=True)
        else:
            doc = fitz.open(v["pdf"])
            toc = read_toc(doc)
            preview = ", ".join("{}@{}".format(e["book"], e["page"]) for e in toc[:6])
            print(f"  目錄讀到 {len(toc)} 本: {preview}", flush=True)
            if not toc:
                print("  ✗ 找不到目錄，跳過", flush=True)
                doc.close()
                continue
            offset = solve_offset(doc, toc)
            if offset is None:
                print("  ✗ 回驗不過（offset 找不到），跳過——寧可不寫也不要寫錯", flush=True)
                doc.close()
                continue
            print(f"  ✓ offset={offset}（頁碼取樣一致＋標題頁回驗通過）", flush=True)
            cache_f.write_text(json.dumps({"toc": toc, "offset": offset},
                                          ensure_ascii=False), encoding="utf-8")
            doc.close()

        doc = fitz.open(v["pdf"])
        ranges = build_ranges(doc, toc, offset)
        doc.close()
        for r in ranges:
            print(f"     {r['book']:<5} {r['pages']}")
        if a.write and ranges:
            v["ranges"] = ranges
            v["status"] = "ready"
            changed = True

    if changed:
        CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n已寫回 {CFG.name}")
    elif a.write:
        print("\n沒有可寫入的結果")
    else:
        print("\n（提案模式，未寫入。加 --write 才更新 config）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
