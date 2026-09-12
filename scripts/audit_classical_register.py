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

# ── 文言硬標記（2026-09-11 補）──────────────────────────────────────────────────
# 🚨 原本只認句末語氣詞，於是《基督信徒的慰藉》裡這幾段整批漏判、稽核報 0%：
#
#   「啊神啊，**爾**不請求我們所沒有的東西……然而**爾**卻奪去了我所愛的。」
#   「他**何以**不幸而短命呢？……他**未嘗**有一日無心痛之日……**我欲**知曉」
#   「幾乎**難以堪當**……當他病中乞求我的援助之際」
#
# 這些標記是逐條**實測過精確度**才收的，沒量過的一律不收。量下來被剔掉的有：
#   爾／汝 直接計數  → 1,066 段，幾乎全是音譯人名（泰戈爾、克爾凱郭爾、貝爾）
#   吾 直接計數      → 203 段，多半是人名「宮部金吾」
#   是以             → 命中「不**是以**宣教士的身份」
#   者也             → 命中「講**者也**應當」「讀**者也**許會」
#   之際／以至於     → 現代書面語本來就這樣寫，且「本於信以至於信」是和合本
#   未嘗（不設限）   → 命中「未**嘗試**馴化」，那是現代詞「嘗試」
#
# 留下來的這幾條，命中的除了內村那三段之外幾乎都是穆勒翻的吠陀與奧義書偈頌——
# 那些**本來就該是文言**（使用者的「詩詞例外」），所以 --clear 強制指定 --author
# 這道保險不能拿掉。
_CL_STRONG = re.compile(
    r"何以[^。！？]{0,20}[？?]"      # 何以……？（文言反詰）
    r"|未嘗(?!試)"                   # 未嘗；排除現代詞「嘗試」
    r"|[我吾]欲(?=[知見求得往言為])"  # 我欲知／吾欲求
    r"|難以堪當|莫此為甚|不勝[^，。]{0,4}之至"
    r"|[^，。]{2,10}而[^，。]{0,8}[也矣焉]。"  # ……而……也。
)
# 第二人稱文言化：用 爾／汝 而**通篇不用** 你／妳／祢。音譯人名不會這樣成群出現，
# 所以「≥2 次且完全沒有白話第二人稱」這個組合把 1,066 段的誤報收斂到 143 段。
_YOU_CLASSICAL = re.compile(r"[爾汝](?=[不卻乃其之能可必將曾無有為所來去知言])")
_YOU_VERNACULAR = re.compile(r"[你妳祢]")

# 詩詞：使用者明言例外。短行、無句號、成組出現的多半是詩。
_VERSE_HINT = re.compile(r"^[^。！？]{0,24}[，、]?$")

MIN_LEN = 40          # 太短的段落判不準（標題、日期、書名）


def classical_score(zh: str) -> float:
    """0（純白話）到 1（純文言）。純函式。"""
    t = zh or ""
    # 硬標記優先於密度。這幾段的白話標記（的／了／是）其實不少，密度公式算出來
    # 接近 0——但「我欲知曉」「未嘗有一日無心痛之日」就是文言，不該被稀釋掉。
    # 門檻 0.55 剛好落在 classical（≥0.5），而且這些標記都逐條量過精確度。
    if _CL_STRONG.search(t) or (
            len(_YOU_CLASSICAL.findall(t)) >= 2 and not _YOU_VERNACULAR.search(t)):
        return 0.6
    if len(t) < MIN_LEN:
        # 🚨 短段落不能一律放行。密度在幾十個字上算不準，但**句末語氣詞**本身就是
        #    硬證據：「本書今年已屆發行滿三十年。乃大榮幸也。令人感謝不已。」只有
        #    28 字，卻是道地的文言。原本 MIN_LEN 一刀切，讓這種段落整批漏掉——
        #    《基督信徒的慰藉》重譯後稽核報 0% 文言，站上第五個 chunk 就是這一句。
        return 0.6 if _FINAL.search(t) else 0.0
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
