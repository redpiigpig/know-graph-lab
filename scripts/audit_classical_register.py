# -*- coding: utf-8 -*-
"""稽核譯文的語域：哪些段落被譯成文言文了。

為什麼要有這一支：內村、矢內原這一線的原文有不少是**文語体**（『基督信徒のなぐさめ』
1893 年就是），引擎於是整段譯成文言——「為一婦人之心思所奪，而以餘生送於無益之悲哀
中，其情可謂情矣，然非真正之勇氣也」。讀起來像清末的譯本，但**使用者要的是白話文**
（2026-09-10 定調），只有**詩詞**例外。

判準是虛詞密度，不是單看有沒有「之」——白話裡「之」「其」照樣出現（「總之」「其中」）。
真正的文言標記是**句末語氣詞**（也／矣／乎／哉／焉／耳）與**文言連詞**（而／則／然／
故／蓋／夫），而且要**成群出現**才算。

  python -X utf8 scripts/audit_classical_register.py                 # 全庫
  python -X utf8 scripts/audit_classical_register.py --author uchimura
  python -X utf8 scripts/audit_classical_register.py --work consolations --show 5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "ebook-collected-works"

# 句末語氣詞：接在句讀之前才算。這是文言最硬的標記——白話幾乎不用。
_FINAL = re.compile(r"[也矣乎哉焉耳歟耶][。，、；：？！]")
# 文言連詞／代詞，在句首或句中獨立出現
_FUNCTION = re.compile(r"[^\w]?(?:而|則|然|故|蓋|夫|茲|斯|遂|乃|爰|俾|凡|曷|豈|寧)(?=[^\w]|.)")
# 白話標記：出現得夠多就不算文言，即使夾了幾個文言虛詞
_VERNACULAR = re.compile(r"的|了|著|們|是|在|把|被|給|很|就|還|沒有|不是|可以|因為|所以")

# 詩詞：使用者明言例外。短行、無句號、成組出現的多半是詩。
_VERSE_HINT = re.compile(r"^[^。！？]{0,24}[，、]?$")

MIN_LEN = 40          # 太短的段落判不準（標題、日期、書名）


def classical_score(zh: str) -> float:
    """0（純白話）到 1（純文言）。純函式。"""
    t = zh or ""
    if len(t) < MIN_LEN:
        return 0.0
    finals = len(_FINAL.findall(t))
    funcs = len(_FUNCTION.findall(t))
    vern = len(_VERNACULAR.findall(t))
    # 每百字的文言標記數，扣掉白話標記的密度
    per100 = (finals * 3 + funcs) / (len(t) / 100)
    vern100 = vern / (len(t) / 100)
    raw = (per100 - vern100 * 0.6) / 12.0
    return max(0.0, min(1.0, raw))


def is_verse(zh: str) -> bool:
    """詩詞不改——使用者 2026-09-10 明言的例外。"""
    return bool(_VERSE_HINT.match((zh or "").strip())) and len(zh or "") < MIN_LEN


def classify(zh: str) -> str:
    if is_verse(zh):
        return "verse"
    s = classical_score(zh)
    if s >= 0.5:
        return "classical"
    if s >= 0.25:
        return "mixed"
    return "vernacular"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author")
    ap.add_argument("--work")
    ap.add_argument("--show", type=int, default=0, help="印出前 N 段文言樣本")
    ap.add_argument("--clear", action="store_true",
                    help="把文言段落的譯文清成 None，交給引擎用新 prompt 重譯")
    ap.add_argument("--also-mixed", action="store_true", help="連半文半白的也清")
    args = ap.parse_args()

    if args.clear and not (args.author or args.work):
        # 🚨 繆勒那批的「文言」是**真的該文言**——SBE 第 16 卷就是《易經》本身，
        #    《法句經》引的也是漢譯偈頌。全庫無差別清會把那些毀掉。
        print("--clear 必須指定 --author 或 --work（避免誤清繆勒的《易經》那類漢籍）")
        raise SystemExit(1)

    rows = []
    for data in sorted(ROOT.glob("*_data")):
        if args.author and not data.name.startswith(args.author):
            continue
        for slug in sorted(p for p in data.iterdir() if p.is_dir()):
            if args.work and slug.name != args.work:
                continue
            tally = {"classical": 0, "mixed": 0, "vernacular": 0, "verse": 0}
            samples = []
            targets = {"classical"} | ({"mixed"} if args.also_mixed else set())
            for f in slug.glob("sec*.json"):
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    continue
                zh = d.get("zh") or []
                touched = False
                for i, z in enumerate(zh):
                    if not z:
                        continue
                    k = classify(z)
                    tally[k] += 1
                    if k == "classical" and len(samples) < args.show:
                        samples.append(z)
                    if args.clear and k in targets:
                        zh[i] = None
                        touched = True
                if touched:
                    d["zh"] = zh
                    f.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
            total = sum(tally.values())
            if total:
                rows.append((data.name, slug.name, total, tally, samples))

    rows.sort(key=lambda r: -(r[3]["classical"] / max(1, r[2])))
    print(f"{'作者':16} {'作品':26} {'段':>5} {'文言':>6} {'混':>5} {'白話':>6}")
    grand_c = grand_t = 0
    for data, slug, total, t, samples in rows:
        pct = t["classical"] / total * 100
        grand_c += t["classical"]
        grand_t += total
        flag = " ←" if pct >= 20 else ""
        print(f"{data.name if hasattr(data,'name') else data:16} {slug:26} {total:5} "
              f"{t['classical']:5}({pct:4.0f}%) {t['mixed']:4} {t['vernacular']:5}{flag}")
        for s in samples:
            print(f"      | {s[:110]}")
    print(f"\n合計 {grand_t:,} 段，其中文言 {grand_c:,} 段（{grand_c/max(1,grand_t)*100:.1f}%）")


if __name__ == "__main__":
    main()
