#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《神的演化》：MinerU 吃標點的頁、或批次頁數不符被丟掉的頁，改用 Gemini 單頁重跑 OCR。

單頁一次一頁，不會有批次回報頁碼錯位的問題；結果寫 c:/tmp/evo/gem1/NNN.json，
god_evolution_read_aloud.load_pages 會優先採用。已有檔的頁跳過，額度用完（429）會
FAIL 並略過，隔天再跑同一行就接著補。

  python -X utf8 scripts/god_evolution_reocr.py            # 補 gem 與 gem1 都沒有的頁
  python -X utf8 scripts/god_evolution_reocr.py 226,227    # 指定頁
"""
import glob
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import god_evolution_read_aloud as g  # noqa: E402
import scan_ocr  # noqa: E402
from ocr_pdf_to_text import ocr_pdf  # noqa: E402

OUT = Path("c:/tmp/evo/gem1")
SRC = Path("c:/tmp/evo/src.pdf")


def todo_pages() -> list[int]:
    pages = g.load_pages()
    return sorted(k for k, v in pages.items() if v["engine"] != "gemini")


def main() -> int:
    pages = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else todo_pages()
    OUT.mkdir(parents=True, exist_ok=True)
    prompt = scan_ocr.build_prompt({"title": "神的演化", "vertical": True, "skip_figures": True})

    def job(s: int) -> None:
        f = OUT / f"{s:03d}.json"
        if f.exists():
            return
        try:
            pg = ocr_pdf(SRC, model="gemini-3.6-flash", pages=(s, s), batch=0, prompt=prompt)
            f.write_text(json.dumps({"start": s, "end": s, "pages": pg}, ensure_ascii=False), encoding="utf-8")
            print(f"ok {s}", flush=True)
        except Exception as ex:  # noqa: BLE001
            print(f"FAIL {s} {str(ex)[:100]}", flush=True)

    print(f"待補 {len(pages)} 頁")
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(job, pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
