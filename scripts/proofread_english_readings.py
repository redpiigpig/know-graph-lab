"""逐句校讀國小英語課本的 50 篇課文，挑出「機械規則量不出來」的那一類毛病。

2026-09-17 使用者問「你有寫過測試每一頁都檢查過了是嗎」，我去把 PDF 渲染出來看，
才發現課文還有這些東西，而十三道閘全部放行：

    L01  Please, I am fine. ／ we have OK ／ I have OK      ← 不是英文
    L30  We always celebrate January. We often celebrate February. …  ← 連九句同框架
    L47  Dad works in Taichung, address in Taipei.          ← 不成句
    L08  she has ten fingers and ten feet                   ← 應該是 ten toes
    L14  beside river ／ near house                          ← 少冠詞
    L20  How much are the meatballs? It is twenty dollars.  ← 應該是 They are
    L26  she builds a cake                                   ← 應該是 bakes
    L35  Bob is the fattest boy in our class                 ← 拿學生的胖當例句不妥

那些閘量的是長度、重複、語言方向、字詞清單——**全是數得出來的東西**。
「這句是不是英文」「這篇是不是故事」「這樣寫對國小生妥不妥」數不出來，
再加多少條規則都一樣。所以這一步改用模型逐句校讀，輸出要修的清單。

用法：
    python scripts/proofread_english_readings.py              # 全部 50 課
    python scripts/proofread_english_readings.py --only 1 --only 30
    python scripts/proofread_english_readings.py --json out.json   # 給下游用
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import build_english_course50 as gen  # noqa: E402

OUT_DIR = gen.OUT_DIR


PROMPT = """你是台灣國小英語教材的審稿人。下面是第 {no} 課的課文（英文＋中譯）。
本課文法點是「{focus}」。

請逐句挑錯，只挑真正的問題，沒問題就回空陣列。要挑的是：

1. **不是英文**：文法錯、搭配錯、根本不通。
   例：`Please, I am fine.`、`we have OK`、`Dad works in Taichung, address in Taipei.`
2. **事實或常識錯**：例 `she has ten fingers and ten feet`（應該是 toes）、
   `A parrot does not talk`（鸚鵡會說話）、`she builds a cake`（應該是 bakes）。
3. **單複數／冠詞**：例 `beside river`、`How much are the meatballs? It is twenty dollars.`
4. **中譯不通**：例 `Please, I am fine.` 譯成「請，我很好。」
5. **對國小生不妥**：拿學生的外表（胖、笨）當例句、負面標籤。
6. **整篇不是故事**：九句都是同一個框架換一個字（例如連續九句
   `We celebrate January. We celebrate February.`），沒有人物也沒有情節。

不要挑：用字簡單、句子短、重複本課文法點——那些是刻意的。

只輸出 JSON，不要說明文字：
{{"verdict": "ok" 或 "rewrite",
  "issues": [{{"sentence": "有問題的那一句原文", "problem": "問題是什麼（繁體中文）",
              "fix": "改成什麼"}}]}}

verdict 填 "rewrite" 的條件：整篇不是故事，或者問題多到逐句改不如重寫。
只有零星幾句要改就填 "ok"。

課文：
{body}
"""


def lesson_text(data: dict) -> str:
    return "\n".join(f"{i}. {s['en']}　／　{s['zh']}"
                     for i, s in enumerate(data["reading"]["sentences"], 1))


def validate(payload: dict) -> list[str]:
    if not isinstance(payload, dict):
        return ["輸出不是物件"]
    if payload.get("verdict") not in ("ok", "rewrite"):
        return ['verdict 要是 "ok" 或 "rewrite"']
    issues = payload.get("issues")
    if not isinstance(issues, list):
        return ["issues 要是陣列"]
    for i, item in enumerate(issues, 1):
        if not isinstance(item, dict):
            return [f"第 {i} 筆不是物件"]
        for key in ("sentence", "problem", "fix"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                return [f"第 {i} 筆缺 {key}"]
    return []


FIX_PROMPT = """你是台灣國小英語教材的審稿人，正在修第 {no} 課的課文。
本課文法點是「{focus}」。下面是原課文，以及審稿挑出的問題。

請把有問題的句子改掉，**沒被挑到的句子原樣保留**，句數不變（{count} 句）。
改的時候要顧到：
- 英文要通順正確；中譯要是通順的繁體中文（台灣用語），不是逐字對譯。
- 這一課的學生只學到第 {no} 課，不要換上更難的字。
- 整篇要讀得像一段有人物與情節的短文。

只輸出 JSON，不要說明文字：
{{"sentences": [{{"en": "英文句", "zh": "中文翻譯"}}]}}

原課文：
{body}

審稿挑出的問題：
{issues}
"""


def apply_fixes(report: list[dict]) -> None:
    """把校讀挑出的零星問題改掉，句數不變。

    🚨 不要拿審稿回傳的 fix 欄位直接做字串取代。那個欄位有時候給的是英文替換句、
    有時候是中譯替換句、有時候是一句中文指示（「加入人物與情節」），三種混在一起，
    機械取代會把課文改壞。改法是把問題清單餵回去讓它重寫那幾句，再驗一次。
    """
    lessons = {l["no"]: l for l in gen.load_lessons()}
    for row in report:
        no = row["no"]
        if row["verdict"] != "ok" or not row["issues"]:
            continue
        path = OUT_DIR / f"L{no:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        before = data["reading"]["sentences"]
        gen.CURRENT_LESSON = no
        issues = "\n".join(f"- 「{i['sentence']}」：{i['problem']}（建議：{i['fix']}）"
                           for i in row["issues"])

        def check(payload, n=len(before)):
            if not isinstance(payload, dict):
                return ["輸出不是物件"]
            got = payload.get("sentences")
            if not isinstance(got, list) or len(got) != n:
                return [f"要剛好 {n} 句，實得 {len(got) if isinstance(got, list) else '非陣列'}"]
            for i, s in enumerate(got, 1):
                if not isinstance(s, dict) or not s.get("en") or not s.get("zh"):
                    return [f"第 {i} 句缺 en/zh"]
            return (gen.validate_reading(got)
                    + gen._common_errs({"reading": {"sentences": got}}))

        fixed, errs = gen.ask(
            FIX_PROMPT.format(no=no, focus=lessons[no]["focus"],
                              count=len(before), body=lesson_text(data),
                              issues=issues),
            check, attempts=4, stage=f"修訂 L{no:02d}")
        if fixed is None:
            print(f"L{no:02d} ⚠ 修訂失敗：{'；'.join(errs)}", flush=True)
            continue
        data["reading"]["sentences"] = fixed["sentences"]
        changed = sum(1 for a, b in zip(before, fixed["sentences"]) if a["en"] != b["en"])
        got = gen.coverage(data)
        if got < gen.MIN_COVERAGE:
            print(f"L{no:02d} ⚠ 改完覆蓋掉到 {got:.0%}，不落地", flush=True)
            continue
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"L{no:02d} ✓ 改了 {changed}/{len(before)} 句　覆蓋 {got:.0%}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, action="append", help="只校指定課次")
    ap.add_argument("--json", help="把結果寫成 JSON")
    ap.add_argument("--apply", help="讀既有的校讀 JSON，把零星問題改掉")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    gen.VERBOSE = args.verbose

    if args.apply:
        apply_fixes(json.loads(Path(args.apply).read_text(encoding="utf-8")))
        return

    lessons = gen.load_lessons()
    report: list[dict] = []
    for lesson in lessons:
        no = lesson["no"]
        if args.only and no not in args.only:
            continue
        path = OUT_DIR / f"L{no:02d}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        payload, errs = gen.ask(
            PROMPT.format(no=no, focus=lesson["focus"], body=lesson_text(data)),
            validate, attempts=3, stage=f"校讀 L{no:02d}")
        if payload is None:
            print(f"L{no:02d} ⚠ 校讀失敗：{'；'.join(errs)}", flush=True)
            continue
        issues = payload["issues"]
        report.append({"no": no, "verdict": payload["verdict"], "issues": issues})
        mark = "✗ 建議重寫" if payload["verdict"] == "rewrite" else (
            f"△ {len(issues)} 處" if issues else "✓")
        print(f"L{no:02d} {mark}", flush=True)
        for item in issues:
            print(f"      「{item['sentence']}」 {item['problem']} → {item['fix']}",
                  flush=True)

    rewrite = [r["no"] for r in report if r["verdict"] == "rewrite"]
    patch = [r["no"] for r in report if r["verdict"] == "ok" and r["issues"]]
    print(f"\n校讀 {len(report)} 課：建議重寫 {len(rewrite)} 課 {rewrite}")
    print(f"                零星要改 {len(patch)} 課 {patch}")
    if args.json:
        Path(args.json).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"寫出 {args.json}")


if __name__ == "__main__":
    main()
