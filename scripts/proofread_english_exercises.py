"""逐題校讀國小英語課本的 1,700 道練習題。

姊妹檔 [proofread_english_readings.py] 校的是課文；這一支校**題目**。

2026-09-17 使用者：「甚麼叫做 We are hello.／I am thank. 小一的英文也不會是這樣啊」。
那批東西活在題目區，而我當時只做了課文校讀——題目從頭到尾沒有系統性看過，
我卻已經回報過「練習題經得起檢查」（實際上只看了選擇題那一頁）。

機械閘量得到的（重複、選項一樣、答案位置、標點、詞性）都已經有閘擋。
這一支要挑的是量不出來的那一類：

  - 答案根本不對（「whisper 的英文是？」標準答案填 wink）
  - 答案不只一個（挖空題沒有中文提示時，can 與 can't 都通）
  - 不是英文（We are hello.）
  - 中文提示與英文對不起來（「我想買兩個三明治。 I have ______」）
  - 誘答項毫無意義（問「你長大的地方」而選項放 wink／whisper）
  - 對國小生不妥

用法：
    python scripts/proofread_english_exercises.py --json out.json
    python scripts/proofread_english_exercises.py --only 1 --only 20
    python scripts/proofread_english_exercises.py --apply out.json
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

PROMPT = """你是台灣國小英語教材的審稿人。下面是第 {no} 課的練習題。
本課文法點是「{focus}」，本課單字：{words}

請逐題挑錯。只挑**真正有問題**的，沒問題就回空陣列。要挑的是：

1. **標準答案錯**：ans 填的不是正確答案。
2. **答案不只一個**：選項裡有兩個以上填進去都通順，而只認一個。
   挖空題沒有中文提示時最常發生。
3. **不是英文**：`We are hello.`、`I am thank.`、`They are you.` 這種。
4. **中文與英文對不起來**：中文說「我想買兩個三明治」，英文卻是 `I have ______`。
5. **誘答項沒有意義**：問「你長大的地方叫什麼」而選項放 wink／whisper——
   那三個一看就不是地方，等於送分。
6. **對國小生不妥**：拿學生的外表（胖、笨）當例句、負面標籤。
7. 句子重組的打散字詞**排不出**標準答案（少字或多字）。

不要挑：題目簡單、重複本課文法點、選項用同一組字——那些是刻意的，
國小課本的 be 動詞那一課本來就十題同一組選項。

只輸出 JSON，不要說明文字：
{{"issues": [{{"where": "mcq 第 3 題" 這種定位, "quote": "有問題的原文",
             "problem": "問題是什麼（繁體中文）", "fix": "改成什麼"}}]}}

題目：
{body}
"""


def lesson_text(data: dict) -> str:
    ex = data["exercises"]
    out = []
    for i, m in enumerate(ex["mcq"], 1):
        out.append(f"mcq 第 {i} 題：{m['q']}　選項 {' / '.join(m['opts'])}　答案 {m['ans']}")
    for i, x in enumerate(ex["fill"], 1):
        out.append(f"fill 第 {i} 題：{x['q']}　答案 {x['ans']}")
    for i, x in enumerate(ex["translate"], 1):
        out.append(f"translate 第 {i} 題：{x['q']}　答案 {x['ans']}")
    for i, x in enumerate(ex["unscramble"], 1):
        out.append(f"unscramble 第 {i} 題：{x['q']}　答案 {x['ans']}")
    return "\n".join(out)


def validate(payload) -> list[str]:
    if not isinstance(payload, dict):
        return ["輸出不是物件"]
    issues = payload.get("issues")
    if not isinstance(issues, list):
        return ["issues 要是陣列"]
    for i, item in enumerate(issues, 1):
        if not isinstance(item, dict):
            return [f"第 {i} 筆不是物件"]
        for key in ("where", "quote", "problem", "fix"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                return [f"第 {i} 筆缺 {key}"]
    return []


FIX_PROMPT = """你是台灣國小英語教材的審稿人，正在修第 {no} 課的練習題。
本課文法點是「{focus}」，本課單字：{words}

下面是原題目與審稿挑出的問題。請把有問題的題目改掉，**沒被挑到的原樣保留**，
每一區的題數不變（選擇 {n_mcq}、填空 {n_fill}、造句 {n_tr}、重組 {n_un}）。

規矩：
- 選擇題：ans 必須逐字等於 opts 其中一個，四個選項不重複；挖空題的中文提示
  一定要放在括號裡，否則答案會不只一個。
- 英文句不可以用全形標點（。，？），括號裡的中文提示才用全形。
- 只能用本課與前面幾課學過的字。
- 句子重組的打散字詞要排得出標準答案，不多字也不少字。

只輸出 JSON，不要說明文字：
{{"mcq": [{{"q": "…", "opts": ["A","B","C","D"], "ans": "…"}}],
  "fill": [{{"q": "…", "ans": "…"}}],
  "translate": [{{"q": "中文", "ans": "English."}}],
  "unscramble": [{{"q": "打散 / 的 / 字", "ans": "正確句子."}}]}}

原題目：
{body}

審稿挑出的問題：
{issues}
"""


def apply_fixes(report: list[dict]) -> None:
    lessons = {l["no"]: l for l in gen.load_lessons()}
    for row in report:
        no, issues = row["no"], row["issues"]
        if not issues:
            continue
        path = OUT_DIR / f"L{no:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        ex = data["exercises"]
        gen.CURRENT_LESSON = no
        lesson = lessons[no]
        want = {"mcq": len(ex["mcq"]), "fill": len(ex["fill"]),
                "translate": len(ex["translate"]), "unscramble": len(ex["unscramble"])}

        def check(payload, w=want):
            if not isinstance(payload, dict):
                return ["輸出不是物件"]
            errs = []
            for key, n in w.items():
                got = payload.get(key)
                if not isinstance(got, list) or len(got) != n:
                    errs.append(f"{key} 要剛好 {n} 題")
            return errs or gen.validate_exercises(payload, w)

        fixed, errs = gen.ask(
            FIX_PROMPT.format(no=no, focus=lesson["focus"],
                              words="、".join(w["en"] for w in lesson["words"]),
                              n_mcq=want["mcq"], n_fill=want["fill"],
                              n_tr=want["translate"], n_un=want["unscramble"],
                              body=lesson_text(data),
                              issues="\n".join(
                                  f"- {i['where']}「{i['quote']}」：{i['problem']}"
                                  f"（建議：{i['fix']}）" for i in issues)),
            check, attempts=5, stage=f"修訂題目 L{no:02d}")
        if fixed is None:
            print(f"L{no:02d} ⚠ 修訂失敗：{'；'.join(errs)}", flush=True)
            continue
        changed = sum(1 for k in want
                      for a, b in zip(ex[k], fixed[k]) if a != b)
        for k in want:
            ex[k] = fixed[k]
        gen.rebuild_scrambles(ex, seed=no)
        gen.shuffle_options(ex, seed=no)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"L{no:02d} ✓ 改了 {changed} 題", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, action="append")
    ap.add_argument("--json")
    ap.add_argument("--apply")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    gen.VERBOSE = args.verbose

    if args.apply:
        apply_fixes(json.loads(Path(args.apply).read_text(encoding="utf-8")))
        return

    report = []
    for lesson in gen.load_lessons():
        no = lesson["no"]
        if args.only and no not in args.only:
            continue
        path = OUT_DIR / f"L{no:02d}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        gen.CURRENT_LESSON = no
        payload, errs = gen.ask(
            PROMPT.format(no=no, focus=lesson["focus"],
                          words="、".join(w["en"] for w in lesson["words"]),
                          body=lesson_text(data)),
            validate, attempts=3, stage=f"校讀題目 L{no:02d}")
        if payload is None:
            print(f"L{no:02d} ⚠ 校讀失敗：{'；'.join(errs)}", flush=True)
            continue
        issues = payload["issues"]
        report.append({"no": no, "issues": issues})
        print(f"L{no:02d} {'✓' if not issues else f'△ {len(issues)} 處'}", flush=True)
        for it in issues:
            print(f"      {it['where']}「{it['quote'][:40]}」{it['problem'][:50]}",
                  flush=True)

    bad = [r["no"] for r in report if r["issues"]]
    print(f"\n校讀 {len(report)} 課、{sum(len(r['issues']) for r in report)} 處，"
          f"要改 {len(bad)} 課 {bad}")
    if args.json:
        Path(args.json).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"寫出 {args.json}")


if __name__ == "__main__":
    main()
