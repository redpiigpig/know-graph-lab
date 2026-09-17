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
import re
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

下面**每一題都有問題**，請逐題改好。題數不變，順序不變。

規矩：
- 選擇題：ans 必須逐字等於 opts 其中一個，四個選項不重複。
- 挖空題的中文提示一定要放在括號裡，而且**要給語意**——
  寫「（這條緞帶是紅色的）」不要寫「（這條緞帶是_____的）」，
  也不要只寫「（請填序數詞）」，那樣答案不只一個。
- 英文句不可以用全形標點（。，？），括號裡的中文提示才用全形。
- 只能用本課與前面幾課學過的字。
- 句子重組的打散字詞要排得出標準答案，不多字也不少字。

只輸出 JSON，不要說明文字。**key 要照抄下面每一題的編號**：
{{"items": {{"mcq-3": {{"q": "…", "opts": ["A","B","C","D"], "ans": "…"}},
            "fill-7": {{"q": "…", "ans": "…"}}}}}}

要改的題目：
{body}
"""


_WHERE = re.compile(r"(mcq|fill|translate|unscramble)\D*(\d+)")


def parse_where(where: str) -> tuple[str, int] | None:
    """把「mcq 第 3 題」解析成 ("mcq", 2)。解析不出來就回 None。"""
    hit = _WHERE.search(where.replace("選擇題", "mcq").replace("填空", "fill")
                        .replace("造句翻譯", "translate").replace("句子重組", "unscramble"))
    if not hit:
        return None
    return hit.group(1), int(hit.group(2)) - 1


def apply_fixes(report: list[dict]) -> None:
    """只把**被挑到的那幾題**交給模型，改完插回原位。

    🚨 不要把整個題區交出去。2026-09-18 第一版是「整區送出、整區收回、
    要求沒被挑到的原樣保留」，結果 L08 只挑了 mcq 第 2 題，模型卻把 10 題填空的
    中文提示整批刪掉——`I ____ a student.（我是學生）` 變成 `I ____ a student.`，
    而沒有提示答案就不只一個，正是前面立閘要防的事。模型碰不到沒交出去的東西，
    這是唯一可靠的擋法。
    """
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

        targets: dict[str, tuple[str, int]] = {}
        for it in issues:
            spot = parse_where(it["where"])
            if spot is None or not (0 <= spot[1] < len(ex[spot[0]])):
                continue
            targets[f"{spot[0]}-{spot[1] + 1}"] = spot
        if not targets:
            print(f"L{no:02d} ⚠ 定位不出任何一題，跳過", flush=True)
            continue

        body = []
        for key, (sect, idx) in targets.items():
            item = ex[sect][idx]
            why = next((i["problem"] for i in issues
                        if parse_where(i["where"]) == (sect, idx)), "")
            opts = f"　選項 {' / '.join(item['opts'])}" if "opts" in item else ""
            body.append(f"[{key}] {item['q']}{opts}　答案 {item['ans']}"
                        + chr(10) + f"      問題：{why}")

        def check(payload, want=targets):
            if not isinstance(payload, dict) or not isinstance(payload.get("items"), dict):
                return ["輸出要是 {\"items\": {…}}"]
            got = payload["items"]
            missing = [k for k in want if k not in got]
            if missing:
                return [f"漏了 {missing}"]
            errs = []
            for k, (sect, _) in want.items():
                item = got[k]
                if not isinstance(item, dict) or not item.get("q") or not item.get("ans"):
                    errs.append(f"{k} 缺 q/ans")
                    continue
                if sect == "mcq":
                    opts = item.get("opts")
                    if not isinstance(opts, list) or len(opts) != 4:
                        errs.append(f"{k} 要四個選項")
                    elif item["ans"] not in opts:
                        errs.append(f"{k} 答案不在選項裡")
                    elif len(set(opts)) != 4:
                        errs.append(f"{k} 選項重複")
            # 單題也要過閘：提示、標點、補語
            probe = {sect: [] for sect in ("mcq", "fill", "translate", "unscramble")}
            for k, (sect, _) in want.items():
                probe[sect].append(got[k])
            return (errs + gen.validate_hints(probe)
                    + gen.validate_punctuation(probe)
                    + gen.validate_complements(probe))

        fixed, errs = gen.ask(
            FIX_PROMPT.format(no=no, focus=lesson["focus"],
                              words="、".join(w["en"] for w in lesson["words"]),
                              body=chr(10).join(body)),
            check, attempts=5, stage=f"修訂題目 L{no:02d}")
        if fixed is None:
            print(f"L{no:02d} ⚠ 修訂失敗：{'；'.join(errs)}", flush=True)
            continue

        for k, (sect, idx) in targets.items():
            ex[sect][idx] = fixed["items"][k]
        gen.rebuild_scrambles(ex, seed=no)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"L{no:02d} ✓ 改了 {len(targets)} 題（只動這幾題）", flush=True)


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
