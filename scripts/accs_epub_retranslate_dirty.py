#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 accs_ingest_epub 的 checkpoint 裡「譯壞了」的那幾則重譯。

  python -X utf8 scripts/accs_epub_retranslate_dirty.py            # 只列出，不改
  python -X utf8 scripts/accs_epub_retranslate_dirty.py --apply

為什麼需要這支：`accs_ingest_epub.py` 走 Gemini→NVIDIA→Haiku 三層鏈，額度乾的
那一段落到後備引擎時會出兩種壞法，兩種都不會報錯：

  ① **把自己的思考當成譯文交出來**——整則變成「We need to translate the English
     passage into Traditional Chinese, following rules: ...」。
  ② **夾雜沒譯完的外文**——中文句子中間冒出 hingegen（德文）、przeciw（波蘭文）、
     continually、slaughter、disposition 這種詞，讀起來像手滑，其實是模型在語言
     之間切換。總論那一段的教父署名也會整批留成英文（Athanasius、Chrysostom）。

實測 806 則裡有 58 則中招（10 則是①）。判準是**中文正文裡的拉丁字母比例**：
乾淨的譯文只有註腳編號與少數專名，比例趨近 0。

重譯走 **Gemini → Haiku**，逐則驗過才寫回——驗不過就換下一個引擎，都不過就保留
原譯並列出來，不要用另一個壞譯蓋掉一個壞譯。

🚨 **不要用 NVIDIA 重譯。** 上面②那種語言切換（hingegen／przeciw／continually）
   正是它出的，拿它來修等於再壞一次。Sonnet 最穩但常整天 429，所以不放在鏈首。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_ebook_to_zh as te   # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CKPT = Path("c:/tmp/accs_epub_zh_jer_lam.jsonl")
PROMPT = """你是古代基督教教父文獻的專業譯者。把下列英文譯成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體、禁夾雜英文或其他外文單詞）；學術散文語氣，忠實流暢。
2. 不加註、不改寫、不省略，也**不要輸出任何說明或思考過程**——只輸出譯文本身。
3. 經文引語沿用和合本語感；括號裡的教父名一律譯成中文。
4. 保留原有的省略號（. . . 譯為 ……）與方括號補字。

{source}"""

META = re.compile(r"(?i)\bwe need to translate|here is the translation|"
                  r"translate the (following|english)|following rules:")


def latin_ratio(text: str) -> float:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    return lat / max(cjk + lat, 1)


def is_dirty(text: str) -> bool:
    if not text.strip():
        return True
    if META.search(text):
        return True
    # 註腳編號與零星專名以外，中文正文不該有連續拉丁字母
    return latin_ratio(text) > 0.02 and len(re.findall(r"[A-Za-z]{3,}", text)) >= 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--engines", default="gemini,haiku",
                    help="逐則依序試，第一個通過驗證的就採用（預設 gemini,haiku）")
    a = ap.parse_args()

    rows = [json.loads(l) for l in CKPT.read_text(encoding="utf-8").splitlines() if l.strip()]
    dirty = [i for i, r in enumerate(rows) if is_dirty(r.get("body_zh") or "")]
    print(f"{len(rows)} 則裡 {len(dirty)} 則要重譯")
    if not a.apply:
        for i in dirty[:20]:
            b = rows[i]["body_zh"]
            print(f"  [{i}] 拉丁比 {latin_ratio(b):.0%}  {b[:90]}")
        print("\n（只列出；要重譯請加 --apply）")
        return 0

    te.PROMPT_TMPL = PROMPT
    ENGINES = {"gemini": te.gemini_translate, "haiku": te.haiku_translate,
               "sonnet": te.sonnet_translate, "nvidia": te.nvidia_translate}
    chain = [e.strip() for e in a.engines.split(",") if e.strip()]
    fixed = failed = 0
    for n, i in enumerate(dirty[: a.limit] if a.limit else dirty, 1):
        src = rows[i].get("body") or ""
        got = None
        for eng in chain:
            try:
                out = ENGINES[eng](src).strip()
            except Exception as e:                              # noqa: BLE001
                print(f"  [{i}] {eng} ✗ {str(e)[:60]}", flush=True)
                continue
            if is_dirty(out):
                print(f"  [{i}] {eng} ⊘ 仍不乾淨（拉丁比 {latin_ratio(out):.0%}）", flush=True)
                continue
            got = (eng, out)
            break
        if not got:
            failed += 1
            continue
        rows[i]["body_zh"] = got[1]
        fixed += 1
        print(f"  [{n}/{len(dirty)}] {i} ✓ {got[0]} {len(got[1])} 字", flush=True)
        CKPT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                        encoding="utf-8")
    print(f"\n重譯成功 {fixed}，仍待處理 {failed}")
    print("🚨 改完要重跑 `python -X utf8 scripts/accs_ingest_epub.py --upload`（冪等 upsert）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
